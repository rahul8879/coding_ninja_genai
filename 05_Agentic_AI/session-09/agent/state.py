from typing import TypedDict, Literal, Optional

class SchedulingState(TypedDict):
    job_id: str
    candidate: dict
    panel: list[dict]
    proposed_slots: list[str]
    panel_provided_slots: Optional[list[str]]
    email_thread_id: Optional[str]
    proposal_sent_at: Optional[str]
    candidate_reply_text: Optional[str]
    last_processed_reply_id: Optional[str]
    panel_reply_texts: dict
    panel_poll_attempts: int
    confirmed_slot: Optional[str]
    meet_link: Optional[str]
    clarification_attempts: int
    poll_attempts: int
    reply_outcome: Optional[Literal["slot_confirmed", "all_rejected", "unclear"]]
    status: Literal["fetching", "checking_availability", "awaiting_reply", "confirmed"]