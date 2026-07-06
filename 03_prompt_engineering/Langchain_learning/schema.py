from pydantic import BaseModel, Field, ValidationError
from typing import Literal, List

# output format ??
class CoTResult(BaseModel):
    category: Literal['Billing','Technical','Feature Request','Churn Risk','Spam','Other']
    urgency: Literal['High', 'Medium', 'Low']
    confidence: int = Field(ge=1, le=10)
    reasoning: str = Field(description='One sentence explanation')
    cot_steps: List[str] = Field(description='3-5 reasoning steps')


