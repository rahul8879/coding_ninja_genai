import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, Response
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError
from app.services.appointment_service import BookingError, book_appointment
from app.services.scheduling import UnsupportedSchedule

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/appointments", tags=["appointments"])

from app.schemas.appointment import AppointmentRequest

@router.post("", status_code=201)
def create_appointment(payload: AppointmentRequest, response: Response):
    try:
        result = book_appointment(conversation_id=str(payload.conversation_id),
            doctor_id=payload.doctor_id, starts_at=payload.starts_at,
            idempotency_key=str(payload.idempotency_key))
        if result["replayed"]:
            response.status_code = 200
        return result
    except BookingError as exc:
        raise HTTPException(exc.status_code, exc.detail) from None
    except UnsupportedSchedule:
        logger.error("booking_schedule_unsupported doctor_id=%s", payload.doctor_id)
        raise HTTPException(503, "This doctor's schedule needs review.") from None
    except SQLAlchemyError:
        logger.error("booking_database_error doctor_id=%s", payload.doctor_id)
        raise HTTPException(503, "Booking is temporarily unavailable. Retry with the same key.") from None
