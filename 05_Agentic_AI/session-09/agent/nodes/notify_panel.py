from mcp_tools import get_client, tools_session, parse_tool_result
from state import SchedulingState


async def notify_panel(state: SchedulingState) -> dict:
    """Send panel members a confirmation email with interview details and
    candidate context — separate from the calendar invite, since the
    invite alone doesn't carry enough context for prep."""
    client = get_client()
    candidate = state["candidate"]
    panel = state["panel"]
    confirmed_slot = state["confirmed_slot"]

    subject = f"Interview confirmed — {candidate['name']}"
    body = (
        f"Hi,\n\n"
        f"Your interview with {candidate['name']} is confirmed for {confirmed_slot}.\n\n"
        f"Join via Google Meet: {state.get('meet_link', 'link not available')}\n\n"
        f"Candidate background:\n{candidate.get('resume_summary', 'N/A')}\n\n"
        f"A calendar invite has been sent separately — this email is just for prep context.\n\n"
        f"Best,\nMODI TECH"
    )

    panel_emails = [member["email"] for member in panel]

    async with tools_session(client, "email") as tools:
        tools_by_name = {tool.name: tool for tool in tools}

        send_result_raw = await tools_by_name["send_email"].ainvoke(
            {
                "to": panel_emails,
                "subject": subject,
                "body": body,
            }
        )
        send_result = parse_tool_result(send_result_raw)

    # Unlike create-event (a structured dict — see confirm_event.py),
    # the Gmail send_email tool returns a plain human-readable STRING
    # on success, e.g.:
    #     send_result = ["Email sent successfully. Message ID: 18fa2c9d0e1f2a3b"]
    # and something containing the word "error" on failure, e.g.:
    #     send_result = ["Error sending email: invalid recipient address"]
    # So the failure check here is deliberately a substring match on
    # lowercased text, not a dict-shape check like confirm_event.py's —
    # different MCP tools return different shapes, and the parsing has
    # to match whichever shape THAT SPECIFIC tool actually uses. Always
    # worth printing the raw tool response once while wiring up a new
    # tool call, rather than guessing its shape from the tool's name.
    if isinstance(send_result, list) and send_result and isinstance(send_result[0], str):
        if "error" in send_result[0].lower():
            raise RuntimeError(f"notify_panel email failed: {send_result[0]}")

    return {
        "status": "confirmed",
    }