from datetime import datetime, timedelta

from mcp_tools import get_client, tools_session, parse_tool_result
from state import SchedulingState
from config import ORGANIZER_EMAIL, ALLOW_DUPLICATE_EVENTS

async def confirm_and_create_event(state: SchedulingState) -> dict:
    client = get_client()
    candidate = state["candidate"]
    panel = state["panel"]
    confirmed_slot = state["confirmed_slot"]

    start_time = confirmed_slot
    end_time = (
        datetime.fromisoformat(confirmed_slot) + timedelta(minutes=45)
    ).isoformat()

    attendee_emails = [candidate["email"]] + [member["email"] for member in panel]

    async with tools_session(client, "calendar") as tools:
        tools_by_name = {tool.name: tool for tool in tools}

        create_result_raw = await tools_by_name["create-event"].ainvoke(
            {
                "calendarId": ORGANIZER_EMAIL,
                "summary": f"Interview — {candidate['name']}",
                "description": (
                    f"Candidate: {candidate['name']}\n"
                    f"Resume summary: {candidate.get('resume_summary', 'N/A')}"
                ),
                "start": start_time,
                "end": end_time,
                "attendees": [{"email": email} for email in attendee_emails],
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"interview-{candidate.get('candidate_id', 'na')}-{confirmed_slot}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
                # Defaults to False (duplicate-detection safety net stays
                # active) — set ALLOW_DUPLICATE_EVENTS=true in agent/.env
                # only for repeated manual testing against the same slot.
                "allowDuplicates": ALLOW_DUPLICATE_EVENTS,
            }
        )
        create_result = parse_tool_result(create_result_raw)

    # The tool returns a structured dict: {"event": {...}, "conflicts": [...],
    # "duplicates": [...], "warnings": [...]} — not a plain success/error string.
    result_data = create_result[0] if isinstance(create_result, list) and create_result else {}

    if not isinstance(result_data, dict) or "event" not in result_data:
        raise RuntimeError(f"create-event failed or returned unexpected shape: {result_data}")

    event = result_data["event"]
    meet_link = event.get("hangoutLink")

    return {
        "status": "confirmed",
        "meet_link": meet_link,
    }
