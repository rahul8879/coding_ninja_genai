# from agent import config
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from state import SchedulingState
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)
class ReplyClassification(BaseModel):

    outcome: Literal["slot_confirmed", "all_rejected", "unclear"] = Field(
        description=(
            "slot_confirmed: candidate clearly picked one of the numbered slots. "
            "all_rejected: candidate rejected every proposed slot and none work. "
            "unclear: reply doesn't clearly fall into either case."
        )
    )
    confirmed_slot_number: Optional[int] = Field(
        default=None,
        description="1-indexed slot number the candidate picked, only set when outcome is slot_confirmed",
    )

async def parse_reply(state: SchedulingState) -> dict:
    structured_llm = llm.with_structured_output(ReplyClassification)
    slots_text = "\n".join(
        f"{i}. {slot}" for i, slot in enumerate(state["proposed_slots"], start=1)
    )

    prompt = (
        f"We proposed these interview slots to a candidate:\n{slots_text}\n\n"
        f"The candidate replied:\n\"{state['candidate_reply_text']}\"\n\n"
        f"Classify this reply. Important: only use 'slot_confirmed' if the "
        f"candidate clearly identifies ONE specific slot number or a specific "
        f"time that matches one of the options. A vague reply like "
        f"'I'm flexible' or 'anytime works' or 'available anytime' does NOT "
        f"count as slot_confirmed — classify those as 'unclear' so we ask "
        f"the candidate to pick a specific number."
    )

    result = await structured_llm.ainvoke(prompt)
    if (
        result.outcome == "slot_confirmed"
        and result.confirmed_slot_number
        and 1 <= result.confirmed_slot_number <= len(state["proposed_slots"])
    ):
        confirmed_slot = state["proposed_slots"][result.confirmed_slot_number - 1]
        return {
            "confirmed_slot": confirmed_slot,
            "reply_outcome": "slot_confirmed",
            "status": "confirmed",
        }

    if result.outcome == "all_rejected":
        return {
            "reply_outcome": "all_rejected",
            "status": "checking_availability",
        }

    attempts = state.get("clarification_attempts", 0) + 1
    return {
        "reply_outcome": "unclear",
        "clarification_attempts": attempts,
        "status": "awaiting_reply",
    }
    