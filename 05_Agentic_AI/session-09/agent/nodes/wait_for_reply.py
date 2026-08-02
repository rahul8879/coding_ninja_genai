import re
import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from mcp_tools import get_client, tools_session, parse_tool_result
from state import SchedulingState

POLL_INTERVAL_SECONDS = 15
MAX_POLL_ATTEMPTS = 6

def _parse_search_results(text: str) -> list[dict]:
    entries = []
    for block in text.strip().split("\n\n"):
        entry = {}
        for line in block.splitlines():
            if ": " in line:
                key, _, value = line.partition(": ")
                entry[key.strip().lower()] = value.strip()
        if "id" in entry:
            entries.append(entry)
    return entries


def _extract_latest_reply_only(full_email_text: str) -> str:
    body = full_email_text.split("\n\n", 1)[-1]
    body = body.replace("\r\n", "\n")
    match = re.search(r"\nOn .+?wrote:\n", body, re.DOTALL)
    if match:
        body = body[: match.start()]
    return body.strip()


def _parse_email_date(date_str: str):
    """Returns a naive UTC datetime, or None if it can't be parsed --
    isolated here so the scan loop below can just skip anything unparseable
    instead of crashing the whole poll."""
    try:
        return parsedate_to_datetime(date_str).astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None
    

async def check_for_reply(state: SchedulingState):
    attempts = state.get("poll_attempts", 0)
    already_processed_id = state.get("last_processed_reply_id")
    proposal_sent_at_str = state.get("proposal_sent_at")
    if proposal_sent_at_str:
        proposal_time = datetime.fromisoformat(proposal_sent_at_str)
    else:
        proposal_time = None

    if attempts>0:
        await asyncio.sleep(POLL_INTERVAL_SECONDS)

    client = get_client()
    candidate_email = state["candidate"]["email"]

    async with tools_session(client, "email") as tools:
        tools_by_name = {tool.name: tool for tool in tools}
        query = f'from:{candidate_email} subject:"Interview Scheduling"'

        if proposal_time:
            query += f' after:{proposal_time.isoformat()}'

        search_result_raw = await tools_by_name["search_emails"].ainvoke({"query": query})
        search_result = parse_tool_result(search_result_raw)
        entries = _parse_search_results(search_result[0])

        latest = None
        for entry in entries:
            if entry["id"] == already_processed_id:
                continue
            if proposal_time and "date" in entry:
                reply_time = _parse_email_date(entry["date"])
                if reply_time and reply_time <= proposal_time:
                    continue  # genuinely old -- keep scanning, don't give up on this poll yet
            latest = entry
            break

        if latest is None:
            return {"candidate_reply_text": None, "poll_attempts": attempts + 1}

        read_result_raw = await tools_by_name["read_email"].ainvoke(
            {"messageId": latest["id"]}
        )
        read_result = parse_tool_result(read_result_raw)

    full_text = read_result[0] if read_result else ""
    reply_only = _extract_latest_reply_only(full_text)

    return {
        "candidate_reply_text": reply_only,
        "last_processed_reply_id": latest["id"],
        "poll_attempts": attempts + 1,
    }





    


