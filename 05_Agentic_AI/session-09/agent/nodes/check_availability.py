from datetime import datetime, timedelta
from mcp_tools import get_client, tools_session, parse_tool_result
from state import SchedulingState
from config import ORGANIZER_EMAIL


def _overlaps_any(start, end, busy_periods) -> bool:
    for period in busy_periods:
        busy_start = datetime.fromisoformat(period["start"]).replace(tzinfo=None)
        busy_end = datetime.fromisoformat(period["end"]).replace(tzinfo=None)
        if start < busy_end and end > busy_start:
            return True
    return False




async def check_panel_availability(state: SchedulingState):
    client = get_client()

    time_min = datetime.utcnow().replace(microsecond=0).isoformat()
    time_max = (datetime.utcnow() + timedelta(days=2)).replace(microsecond=0).isoformat()

    # step 2 : create the tool session
    async with tools_session(client, "calendar") as tools:
        # get-freebusy
        tools_by_name = {tool.name: tool for tool in tools}

        freebusy_raw = await tools_by_name["get-freebusy"].ainvoke({
            "calendars":[{"id": ORGANIZER_EMAIL}],
            "timeMin": time_min,
            "timeMax": time_max,
        })
        freebusy = parse_tool_result(freebusy_raw)
    busy_periods = freebusy[0]['calendars'][ORGANIZER_EMAIL]['busy']

    candidate_slots = []

    for day_offset in range(1,4):
        day = datetime.utcnow() + timedelta(days=day_offset)
        for hour in (11,14,16):
            slot_start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(minutes=45)
            if not _overlaps_any(slot_start, slot_end, busy_periods):
                candidate_slots.append(slot_start.isoformat())
        if len(candidate_slots) >= 5:
            break

    return {
        "proposed_slots": candidate_slots[:5],
        "status": "checking_availability",
    }


# {'proposed_slots': ['2026-08-03T11:00:00', 
#                     '2026-08-03T16:00:00', 
#                     '2026-08-04T11:00:00'], 
#                     'status': 'checking_availability'}