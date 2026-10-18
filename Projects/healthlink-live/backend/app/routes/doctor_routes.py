from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from app.services.doctor_service import search_doctors


from datetime import date
import logging
from app.services.scheduling import UnsupportedSchedule
from app.services.slot_service import DoctorNotFound, InvalidSlotDate, get_available_slots
logger = logging.getLogger(__name__)




router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("")
def list_doctors(
    specialty: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
):
    if specialty is not None:
        specialty = specialty.strip()
        if not specialty:
            raise HTTPException(422, "Specialty cannot be blank")
    try:
        doctors = search_doctors(specialty=specialty)
    except SQLAlchemyError:
        raise HTTPException(503, "Doctor directory temporarily unavailable") from None
    return {"count": len(doctors), "doctors": doctors}


@router.get("/{doctor_id}/slots")
def list_doctor_slots(doctor_id: int, on_date: date = Query(...)):
    if doctor_id <= 0:
        raise HTTPException(422, "doctor_id must be positive")
    try:
        return get_available_slots(doctor_id, on_date)
    except DoctorNotFound:
        raise HTTPException(404, "Doctor not found") from None
    except InvalidSlotDate as exc:
        raise HTTPException(422, str(exc)) from None
    except UnsupportedSchedule:
        logger.error("unsupported_doctor_schedule doctor_id=%s", doctor_id)
        raise HTTPException(503, "This doctor's schedule needs review.") from None
    except SQLAlchemyError:
        raise HTTPException(503, "Could not load available slots.") from None