from langgraph.graph import StateGraph, START, END
from state import SchedulingState

from nodes.fetch_candidates import fetch_candidates_and_panel
from nodes.check_availability import check_panel_availability
from nodes.propose_slots import propose_slots_via_email
from nodes.wait_for_reply import check_for_reply
from nodes.parse_reply import parse_reply
from nodes.confirm_event import confirm_and_create_event
from nodes.notify_panel import notify_panel


from routing import (
    route_after_reply_check,
    route_after_parse,
)

def build_graph(checkpointer=None):
    graph = StateGraph(SchedulingState)

    # register all nodes
    graph.add_node("fetch_candidates_and_panel", fetch_candidates_and_panel)
    graph.add_node("check_panel_availability", check_panel_availability)
    graph.add_node("propose_slots_via_email", propose_slots_via_email)
    graph.add_node("check_for_reply", check_for_reply)
    graph.add_node("parse_reply", parse_reply)
    graph.add_node("confirm_and_create_event", confirm_and_create_event)
    graph.add_node("notify_panel", notify_panel)


    # sequential connections
    graph.add_edge(START, "fetch_candidates_and_panel")
    graph.add_edge("fetch_candidates_and_panel", "check_panel_availability")
    graph.add_edge("check_panel_availability", "propose_slots_via_email")
    graph.add_edge("propose_slots_via_email", "check_for_reply")

    graph.add_conditional_edges(
        "check_for_reply",
        route_after_reply_check,
        {
            "parse_reply": "parse_reply",
            "check_for_reply": "check_for_reply",
            "give_up": END,
        }

    )

    graph.add_conditional_edges(
        "parse_reply",
        route_after_parse,
        {
            "confirm_and_create_event": "confirm_and_create_event",
            "propose_slots_via_email": "propose_slots_via_email",
        },
    )

    graph.add_edge("confirm_and_create_event", "notify_panel")
    graph.add_edge("notify_panel", END)

    return graph.compile(checkpointer=checkpointer)




