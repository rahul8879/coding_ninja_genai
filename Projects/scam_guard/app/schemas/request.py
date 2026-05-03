from pydantic import BaseModel, Field
from typing import Optional


# define input schema

class AnalyzeRequest(BaseModel):
    message: str = Field(
        min_length=5,
        description="The message text to analyze for scam detection"
    )
    prompt_version: Optional[str] = Field(
        default=None,
        description="Prompt version to use"
    )