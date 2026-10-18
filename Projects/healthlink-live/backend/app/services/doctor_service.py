from sqlalchemy import func, select
from app.db.database import engine
from app.db.models import Doctor


def search_doctors(specialty: str | None = None):
    query = select(
        Doctor.id,
        Doctor.name,
        Doctor.specialty,
        Doctor.experience_years,
        Doctor.rating,
        Doctor.availability,
        Doctor.location,
        Doctor.languages,
        Doctor.consultation_type,
    )
    if specialty:
        query = query.where(func.lower(Doctor.specialty) == specialty.lower())
    query = query.order_by(Doctor.rating.desc(), Doctor.id.asc()).limit(10)
    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()
    return [dict(row) for row in rows]


def list_specialties():
    query = select(Doctor.specialty).distinct().order_by(Doctor.specialty)
    with engine.connect() as connection:
        return list(connection.execute(query).scalars().all())