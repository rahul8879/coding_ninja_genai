from datetime import date, datetime, time, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import engine
from app.db.models import Appointment, Doctor
from app.services.scheduling import CLINIC_TZ, build_daily_slots

class DoctorNotFound(Exception):
    pass

class InvalidSlotDate(ValueError):
    pass

def get_available_slots(doctor_id: int, on_date: date):
    now = datetime.now(CLINIC_TZ)
    if not now.date() <= on_date <= now.date() + timedelta(days=14):
        raise InvalidSlotDate("Choose a date between today and 14 days from today.")
    day_start = datetime.combine(on_date, time.min, tzinfo=CLINIC_TZ)
    day_end = day_start + timedelta(days=1)
    with Session(engine) as session:
        doctor = session.get(Doctor, doctor_id)
        if doctor is None:
            raise DoctorNotFound
        candidates = build_daily_slots(doctor.availability, on_date)
        booked = session.execute(select(Appointment.starts_at, Appointment.ends_at).where(
            Appointment.doctor_id == doctor_id,
            Appointment.starts_at < day_end,
            Appointment.ends_at > day_start,
        )).all()
        available = []
        for slot in candidates:
            if slot["starts_at"] < now + timedelta(minutes=30):
                continue
            if any(slot["starts_at"] < booking.ends_at and slot["ends_at"] > booking.starts_at for booking in booked):
                continue
            available.append(slot)
        return {
            "doctor_id": doctor.id, "doctor_name": doctor.name, "date": on_date,
            "timezone": "Asia/Kolkata", "duration_minutes": 30, "slots": available,
        }
