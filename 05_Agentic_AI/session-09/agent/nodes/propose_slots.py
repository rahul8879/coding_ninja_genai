from datetime import datetime
from mcp_tools import get_client, tools_session, parse_tool_result
from state import SchedulingState

def _format_slots_for_email(slots: list[str]) -> str:
    lines = [f"{i}. {slot}" for i, slot in enumerate(slots, start=1)]
    return "\n".join(lines)

async def propose_slots_via_email(state: SchedulingState):
    client = get_client()
    candidate = state["candidate"]
    slots = state["proposed_slots"]

    subject = "Interview Scheduling — Backend Engineer"

    body = (
        f"Dear Rahul,\n\n"
        f"Thank you for your interest in the Backend Engineer role with us. "
        f"We were impressed with your background and would like to invite you "
        f"for an interview.\n\n"
        f"Could you please let us know which of the following time slots "
        f"works best for you?\n\n"
        f"{_format_slots_for_email(slots)}\n\n"
        f"If none of the above times are convenient, please suggest a few "
        f"alternative slots and we will do our best to accommodate.\n\n"
        f"We look forward to speaking with you.\n\n"
        f"Best regards,\n"
        f"Recruiting Team"
    )

    async with tools_session(client, "email") as tools:
        tools_by_name = {tool.name: tool for tool in tools}
        send_result_raw = await tools_by_name["send_email"].ainvoke({
            "to": [candidate["email"]],
            "subject": subject,
            "body": body,
        })
        send_email_result = parse_tool_result(send_result_raw)

    return send_email_result


    



