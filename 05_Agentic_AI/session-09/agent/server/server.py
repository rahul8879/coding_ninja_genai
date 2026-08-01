import json
from mcp.server.fastmcp import FastMCP
from pathlib import Path
mcp = FastMCP('ats-mock')

DATA_PATH = Path(__file__).parent.parent / 'data' / 'seed_data.json'

def load_data():
    with open(DATA_PATH, 'r') as f:
        return json.load(f)
    

@mcp.tool()
def get_open_requisitions():
    data = load_data()
    return data['requisitions']



@mcp.tool()
def get_candidates_ready_for_scheduling(job_id):
    data = load_data()
    req = next((r for r in data['requisitions'] if r['id'] == job_id), None)
    if not req:
        return [{"error": f"No requisition found for {job_id}"}]

    ready = []

    for cid in req['candidate_ids']:
        candidate = data['candidates'].get(cid)
        if candidate and candidate['stage'] == 'panel_interview_scheduling':
            ready.append({"candidate_id": cid, **candidate})

    return ready


@mcp.tool()
def get_candidate(candidate_id: str) -> dict:
    """Fetch a single candidate's full profile by their ID."""
    data = load_data()
    candidate = data["candidates"].get(candidate_id)
    if not candidate:
        return {"error": f"No candidate found for id {candidate_id}"}
    return candidate


@mcp.tool()
def get_panel(job_id: str) -> list[dict]:
    """Fetch the interview panel members assigned to a given job requisition."""
    data = load_data()
    req = next((r for r in data["requisitions"] if r["job_id"] == job_id), None)
    if not req:
        return [{"error": f"No requisition found for {job_id}"}]
    return [data["panel"][pid] for pid in req["panel_ids"]]


if __name__ == "__main__":
    mcp.run(transport='stdio')
