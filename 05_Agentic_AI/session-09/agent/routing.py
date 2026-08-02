from state import SchedulingState
from nodes.wait_for_reply import MAX_POLL_ATTEMPTS as CANDIDATE_MAX_POLL_ATTEMPTS


def route_after_reply_check(state: SchedulingState) -> str:
    """After check_for_reply: move on if a reply arrived, keep polling if
    not (up to the attempt limit), or give up if we've waited too long."""
    if state.get("candidate_reply_text"):
        return "parse_reply"
    if state.get("poll_attempts", 0) >= CANDIDATE_MAX_POLL_ATTEMPTS:
        return "give_up"
    return "check_for_reply"


def route_after_parse(state: SchedulingState) -> str:
    """After parse_reply: branch based on how the LLM classified the reply."""
    outcome = state.get("reply_outcome")
    if outcome == "slot_confirmed":
        return "confirm_and_create_event"
    if outcome == "all_rejected":
        return "request_panel_availability"
    return "propose_slots_via_email"