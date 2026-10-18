from uuid import UUID
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

class AppointmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conversation_id: UUID
    doctor_id: int = Field(gt=0)
    starts_at: AwareDatetime
    idempotency_key: UUID
