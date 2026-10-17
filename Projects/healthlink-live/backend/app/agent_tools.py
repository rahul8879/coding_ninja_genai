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


TOOLS = [{'type': 'function', 'name': 'list_specialties',
           'description': 'List the exact specialty names in our doctor directory.', 
           'parameters': {'type': 'object', 'properties': {}, 'required': [], 'additionalProperties': False}, 
           'strict': True}, 
           {'type': 'function', 'name': 'search_doctors', 'description': 'Search by exact specialty. Returns up to 10 doctors ordered by rating. Availability is schedule text, not confirmed slots.', 'parameters': {'type': 'object', 'properties': {'specialty': {'type': 'string', 'description': 'An exact name from list_specialties.'}}, 'required': ['specialty'], 'additionalProperties': False}, 'strict': True}, {'type': 'function', 'name': 'get_available_slots', 'description': 'Get actual available slots for a doctor and clinic date. Does not book. Use a doctor ID returned by search_doctors.', 'parameters': {'type': 'object', 'properties': {'doctor_id': {'type': 'integer'}, 'on_date': {'type': 'string', 'description': 'Clinic date YYYY-MM-DD, Asia/Kolkata.'}}, 'required': ['doctor_id', 'on_date'], 'additionalProperties': False}, 'strict': True}]


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
        doctors = await run_in_threadpool(search_doctors, specialty=validated.specialty)
        logger.info("tool_completed name=search_doctors count=%s", len(doctors))
        return {"count": len(doctors), "doctors": doctors}
    if name == "get_available_slots":
        try:
            validated = AvailableSlotsArgs.model_validate(args)
            result = await run_in_threadpool(get_available_slots, doctor_id=validated.doctor_id, on_date=validated.on_date)
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
    raise ValueError("Unsupported tool")
