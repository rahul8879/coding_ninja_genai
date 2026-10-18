from uuid import uuid4
from pydantic import AwareDatetime
from app.scheduling import CLINIC_TZ
from datetime import date
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.scheduling import UnsupportedSchedule
from app.slot_service import DoctorNotFound, InvalidSlotDate, get_available_slots
import json
import logging
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from app.doctor_service import list_specialties, search_doctors

logger = logging.getLogger(__name__)



class DoctorSearchArgs(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    specialty: str = Field(min_length=1, max_length=100)


class AvailableSlotsArgs(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    doctor_id: int = Field(gt=0)
    on_date: date


class PrepareBookingArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doctor_id: int = Field(gt=0)
    starts_at: AwareDatetime


TOOLS = [{'type': 'function',
  'name': 'list_specialties',
  'description': 'List the exact specialty names in our doctor directory.',
  'parameters': {'type': 'object',
                 'properties': {},
                 'required': [],
                 'additionalProperties': False},
  'strict': True},
 {'type': 'function',
  'name': 'search_doctors',
  'description': 'Search by exact specialty. Returns up to 10 doctors ordered by rating. '
                 'Availability is schedule text, not confirmed slots.',
  'parameters': {'type': 'object',
                 'properties': {'specialty': {'type': 'string',
                                              'description': 'An exact name from '
                                                             'list_specialties.'}},
                 'required': ['specialty'],
                 'additionalProperties': False},
  'strict': True},
 {'type': 'function',
  'name': 'get_available_slots',
  'description': 'Get actual available slots for a doctor and clinic date. Does not book. Use '
                 'a doctor ID returned by search_doctors.',
  'parameters': {'type': 'object',
                 'properties': {'doctor_id': {'type': 'integer'},
                                'on_date': {'type': 'string',
                                            'description': 'Clinic date YYYY-MM-DD, '
                                                           'Asia/Kolkata.'}},
                 'required': ['doctor_id', 'on_date'],
                 'additionalProperties': False},
  'strict': True},
 {'type': 'function',
  'name': 'prepare_booking',
  'description': 'Prepare a confirmation card only after the user explicitly selects an '
                 'unambiguous doctor/date/time for booking. Rechecks availability. Does not '
                 'book or reserve. Copy the exact doctor_id and starts_at from tool results.',
  'parameters': {'type': 'object',
                 'properties': {'doctor_id': {'type': 'integer'},
                                'starts_at': {'type': 'string',
                                              'description': 'Exact slot ISO timestamp with '
                                                             'timezone.'}},
                 'required': ['doctor_id', 'starts_at'],
                 'additionalProperties': False},
  'strict': True}]


async def execute_tool(name: str, arguments: str):
    args = json.loads(arguments)
    if name == "list_specialties":
        if args != {}:
            raise ValueError("list_specialties expects no arguments")
        specialties = await run_in_threadpool(list_specialties)
        logger.info("tool_completed name=list_specialties")
        return {"specialties": specialties}
    if name == "search_doctors":
        validated = DoctorSearchArgs.model_validate(args)

        logger.info(
            "doctor_search_requested specialty=%r",
            validated.specialty,
        )

        doctors = await run_in_threadpool(
            search_doctors,
            specialty=validated.specialty,
        )

        logger.info(
            "doctor_search_completed specialty=%r count=%s doctor_ids=%s",
            validated.specialty,
            len(doctors),
            [doctor["id"] for doctor in doctors],
        )

        return {"count": len(doctors), "doctors": doctors}
    if name == "get_available_slots":
        try:
            validated = AvailableSlotsArgs.model_validate(args)
            result = await run_in_threadpool(get_available_slots, doctor_id=validated.doctor_id, on_date=validated.on_date)
            logger.info(
                    "tool_completed name=get_available_slots "
                    "doctor_id=%s on_date=%s count=%s",
                    validated.doctor_id,
                    validated.on_date.isoformat(),
                    len(result["slots"]),
                )
        except ValidationError:
            return {"ok": False, "error": "invalid_arguments", "message": "Provide a positive doctor ID and valid YYYY-MM-DD date."}
        except DoctorNotFound:
            return {"ok": False, "error": "doctor_not_found", "message": "Doctor not found. Search the directory again."}
        except InvalidSlotDate as exc:
            return {"ok": False, "error": "invalid_date", "message": str(exc)}
        except UnsupportedSchedule:
            logger.error("tool_failed name=get_available_slots reason=schedule")
            return {"ok": False, "error": "schedule_unavailable", "message": "Schedule needs review. Availability cannot be confirmed."}
        except SQLAlchemyError:
            logger.error("tool_failed name=get_available_slots reason=database")
            return {"ok": False, "error": "availability_unavailable", "message": "Availability could not be checked. Try later."}
        logger.info("tool_completed name=get_available_slots doctor_id=%s count=%s", validated.doctor_id, len(result["slots"]))
        return {"ok": True, **jsonable_encoder(result)}
    if name == "prepare_booking":
        try:
            validated = PrepareBookingArgs.model_validate(args)
        except ValidationError:
            return {"ok": False, "message": "Provide a valid doctor ID and timezone-aware timestamp."}
        availability = await execute_tool("get_available_slots", json.dumps({
            "doctor_id": validated.doctor_id,
            "on_date": validated.starts_at.astimezone(CLINIC_TZ).date().isoformat(),
        }))
        if not availability.get("ok"):
            return availability
        selected = next((slot for slot in availability["slots"]
            if slot["starts_at"] == validated.starts_at.astimezone(CLINIC_TZ).isoformat()), None)
        if selected is None:
            return {"ok": False, "message": "The selected slot is unavailable. Check available slots again."}
        return {
            "ok": True,
            "message": "Confirmation card prepared. Patient must click Confirm booking. No appointment saved.",
            "booking_proposal": {
                "proposal_id": str(uuid4()), "doctor_id": availability["doctor_id"],
                "doctor_name": availability["doctor_name"],
                "starts_at": selected["starts_at"], "ends_at": selected["ends_at"],
            },
        }
    raise ValueError("Unsupported tool")