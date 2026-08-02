import asyncio
from datetime import datetime

from graph import build_graph

def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


async def main():
    app = build_graph()

    initial_state = {
        "job_id": "REQ-101",
        "clarification_attempts": 0,
        "poll_attempts": 0,
    }

    print("=" * 64)
    print(f"[{_ts()}] STARTING RUN — job_id={initial_state['job_id']}")
    print("=" * 64)

    final_state = dict(initial_state)

    async for update in app.astream(initial_state, stream_mode="updates"):
      
        for node_name, node_output in update.items():
            node_output = node_output or {}
            final_state.update(node_output)
            print(f"\n[{_ts()}] ✓ {node_name}")

            if node_name == "fetch_candidates_and_panel":
                cand = node_output.get("candidate", {})
                

            elif node_name == "check_panel_availability":
                slots = node_output.get("proposed_slots", [])
                print(f"    proposed slots: {slots}")

            elif node_name == "propose_slots_via_email":
                print("    email sent — GO REPLY FROM THE CANDIDATE INBOX NOW")
                print("    (reply with the slot number, e.g. '2')")

            elif node_name == "check_for_reply":
                attempt = node_output.get("poll_attempts")
                if node_output.get("candidate_reply_text"):
                    print(f"    reply found on poll {attempt}: {node_output['candidate_reply_text']!r}")
                else:
                    print(f"    no reply yet (poll {attempt}) — sleeping, will check again")

            elif node_name == "parse_reply":
                print(f"    LLM classified reply as: {node_output.get('reply_outcome')}")

            elif node_name == "confirm_and_create_event":
                print(f"    event created — meet link: {node_output.get('meet_link')}")

            elif node_name == "notify_panel":
                print("    panel notified")

    print("\n" + "=" * 64)
    print(f"[{_ts()}] FINAL STATE")
    print("=" * 64)
    for k, v in final_state.items():
        print(f"  {k}: {v}")


asyncio.run(main())