from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from app.doctor_service import search_doctors
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