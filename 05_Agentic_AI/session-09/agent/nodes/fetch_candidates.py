from mcp_tools import get_client,tools_session,parse_tool_result
from state import SchedulingState


async def fetch_candidates_and_panel(state: SchedulingState) -> dict:
    """Look up the candidate ready for scheduling and their assigned panel
    for the given job_id. Pure tool calls, no LLM reasoning needed here."""
    client = get_client()

    async with tools_session(client, "ats") as tools:
        tools_by_name = {tool.name: tool for tool in tools}

        candidates_raw = await tools_by_name["get_candidates_ready_for_scheduling"].ainvoke(
            {"job_id": state["job_id"]}
        )
        candidates = parse_tool_result(candidates_raw)
        if not candidates:
            raise ValueError(
                f"No candidates ready for scheduling for job_id={state['job_id']}"
            )

        # MVP: handle the first ready candidate only. Multiple candidates per
        # job_id would need a loop or separate graph runs — out of scope for now.
        candidate = candidates[0]

        panel_raw = await tools_by_name["get_panel"].ainvoke({"job_id": state["job_id"]})
        panel = parse_tool_result(panel_raw)

    return {
        "candidate": candidate,
        "panel": panel,
        "status": "checking_availability",
    }