import json
import logging
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from app.doctor_service import list_specialties, search_doctors

logger = logging.getLogger(__name__)


class DoctorSearchArgs(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    specialty: str = Field(min_length=1, max_length=100)





TOOLS = [
    {
        "type": "function",
        "name": "list_specialties",
        "description": "List the exact specialty names in our doctor directory.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_doctors",
        "description": "Search by exact specialty. Returns up to 10 doctors ordered by rating. Availability is schedule text, not confirmed slots.",
        "parameters": {
            "type": "object",
            "properties": {
                "specialty": {
                    "type": "string",
                    "description": "An exact name from list_specialties.",
                }
            },
            "required": ["specialty"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]




async def execute_tool(name: str, arguments: str):
    args = json.loads(arguments)
    if name == "list_specialties":
        if args != {}:
            raise ValueError("list_specialties expects no arguments")
        specialties = await run_in_threadpool(list_specialties)
        logger.info("tool_completed name=list_specialties")
        return {"specialties": specialties}
    if name == "search_doctors":
        validated = DoctorSearchArgs.model_validate(args)
        doctors = await run_in_threadpool(search_doctors, specialty=validated.specialty)
        logger.info("tool_completed name=search_doctors count=%s", len(doctors))
        return {"count": len(doctors), "doctors": doctors}
    raise ValueError("Unsupported tool")


