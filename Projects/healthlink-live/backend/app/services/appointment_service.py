from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.database import engine
from app.db.models import Appointment, Conversation, Doctor
from app.services.scheduling import CLINIC_TZ, build_daily_slots

class BookingError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code, self.detail = status_code, detail

def appointment_result(appointment, *, replayed: bool):
    return {
        "appointment_id": appointment.id,
        "conversation_id": appointment.conversation_id,
        "doctor_id": appointment.doctor_id,
        "starts_at": appointment.starts_at,
        "ends_at": appointment.ends_at,
        "created_at": appointment.created_at,
        "status": "confirmed", "replayed": replayed,
    }

def find_previous_booking(session, *, idempotency_key, conversation_id, doctor_id, starts_at):
    previous = session.scalar(select(Appointment).where(Appointment.idempotency_key == idempotency_key))
    if previous is None:
        return None
    if not (previous.conversation_id == conversation_id and previous.doctor_id == doctor_id
            and previous.starts_at == starts_at):
        raise BookingError(409, "This idempotency key was already used for another booking.")
    return appointment_result(previous, replayed=True)

def book_appointment(*, conversation_id: str, doctor_id: int, starts_at: datetime, idempotency_key: str):
    starts_at = starts_at.astimezone(CLINIC_TZ)
    request_data = dict(conversation_id=conversation_id, doctor_id=doctor_id,
                        starts_at=starts_at, idempotency_key=idempotency_key)
    try:
        with Session(engine) as session:
            with session.begin():
                previous = find_previous_booking(session, **request_data)
                if previous is not None:
                    return previous
                conversation = session.get(Conversation, conversation_id)
                if conversation is None:
                    raise BookingError(404, "Conversation not found.")
                # Serialize this service's booking writes for the same doctor.
                doctor = session.scalar(select(Doctor).where(Doctor.id == doctor_id).with_for_update())
                if doctor is None:
                    raise BookingError(404, "Doctor not found.")
                previous = find_previous_booking(session, **request_data)
                if previous is not None:
                    return previous
                now = datetime.now(CLINIC_TZ)
                if not now.date() <= starts_at.date() <= now.date() + timedelta(days=14):
                    raise BookingError(422, "Choose a date between today and 14 days from today.")
                if starts_at < now + timedelta(minutes=30):
                    raise BookingError(422, "Book at least 30 minutes in advance.")
                slots = build_daily_slots(doctor.availability, starts_at.date())
                selected = next((s for s in slots if s["starts_at"] == starts_at), None)
                if selected is None:
                    raise BookingError(422, "This time is not a valid slot for this doctor.")
                ends_at = selected["ends_at"]
                overlap = session.scalar(select(Appointment.id).where(
                    Appointment.doctor_id == doctor_id,
                    Appointment.starts_at < ends_at, Appointment.ends_at > starts_at,
                ).limit(1))
                if overlap is not None:
                    raise BookingError(409, "This slot is no longer available. Choose another slot.")
                appointment = Appointment(patient_id=conversation.patient_id,
                    conversation_id=conversation_id, doctor_id=doctor_id,
                    starts_at=starts_at, ends_at=ends_at, idempotency_key=idempotency_key)
                session.add(appointment)
                session.flush()
                session.refresh(appointment)
                result = appointment_result(appointment, replayed=False)
            return result  # Commit happens before this return.
    except IntegrityError:
        # Failed transaction has rolled back before we inspect the unique key.
        with Session(engine) as session:
            previous = find_previous_booking(session, **request_data)
            if previous is not None:
                return previous
        raise BookingError(409, "Booking conflicted with another request. Refresh the slots.") from None