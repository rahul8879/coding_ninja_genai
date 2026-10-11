import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    specialty: Mapped[str] = mapped_column(String(100), index=True)
    experience_years: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float)
    availability: Mapped[str] = mapped_column(String(200))
    location: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(50))
    qualifications: Mapped[str] = mapped_column(String(500))
    languages: Mapped[str] = mapped_column(String(200))
    consultation_type: Mapped[str] = mapped_column(String(100))
    __table_args__ = (
        CheckConstraint("experience_years >= 0", name="doctor_experience_nonnegative"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="doctor_rating_range"),
    )



class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(String(50), default="demo-patient")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="message_role_valid"),
        CheckConstraint(
            "status IN ('pending', 'completed', 'failed')", name="message_status_valid"
        ),
    )