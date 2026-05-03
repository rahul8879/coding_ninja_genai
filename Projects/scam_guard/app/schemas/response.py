
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ScamLabel(str,Enum):
    SCAM="Scam"
    NOT_SCAM = "Not Scam"
    UNCERTAIN = "Uncertain"


class IntentType(str, Enum):
    OTP_FRAUD = "OTP Fraud"
    PHISHING = "Phishing"
    ACCOUNT_SUSPENSION = "Account Suspension"
    REWARD_MANIPULATION = "Reward Manipulation"
    FEAR_TACTICS = "Fear Tactics"
    FAKE_AUTHORITY = "Fake Authority"
    LOAN_SCAM = "Loan Scam"
    URGENCY = "Urgency"
    SERVICE_REMINDER = "Service Reminder"
    INFORMATIONAL_ALERT = "Informational Alert"
    TRANSACTIONAL_NOTIFICATION = "Transactional Notification"
    ORDER_CONFIRMATION = "Order Confirmation"
    ACCOUNT_UPDATE = "Account Update"
    MARKETING_MESSAGE = "Marketing Message"
    UNKNOWN = "Unknown"

# output schema

class Scamresult(BaseModel):
    label: ScamLabel = Field(
        ...,
        description="Classification result: Scam, Not Scam, or uncertain"
    )

    intent : IntentType 
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description= "Confidence of classication between 0.0 to 1.0"
    )

    reasoning: str = Field(
        min_length=10,
        description=""
    )
    prompt_version_used: Optional[str]
    
