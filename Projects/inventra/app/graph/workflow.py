from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.aggregator import aggregate_results
from app.graph.agents.context_agent import extract_context
from app.graph.agents.finance_agent import finance_agent
from app.graph.agents.forecast_agent import forecast_agent
from app.graph.agents.inventory_agent import inventory_agent
from app.graph.agents.planner_agent import planner_agent
from app.graph.agents.response_agent import response_agent
from app.graph.agents.vendor_agent import vendor_agent
from app.graph.decision import reorder_decision
from app.graph.router import (
    after_finance,
    after_forecast,
    after_inventory,
    after_planner,
    after_reorder,
)
from app.graph.state import InventraState


def build_graph():
    builder = StateGraph(InventraState)

    builder.add_node("context", extract_context)
    builder.add_node("planner", planner_agent)
    builder.add_node("forecast", forecast_agent)
    builder.add_node("inventory", inventory_agent)
    builder.add_node("reorder_decision", reorder_decision)
    builder.add_node("finance", finance_agent)
    builder.add_node("vendor", vendor_agent)
    builder.add_node("aggregate", aggregate_results)
    builder.add_node("respond", response_agent)

    builder.add_edge(START, "context")
    builder.add_edge("context", "planner")

    builder.add_conditional_edges(
        "planner",
        after_planner,
        {
            "forecast": "forecast",
            "inventory": "inventory",
            "finance": "finance",
            "vendor": "vendor",
            "aggregate": "aggregate",
        },
    )

    builder.add_conditional_edges(
        "forecast",
        after_forecast,
        {
            "inventory": "inventory",
            "aggregate": "aggregate",
        },
    )

    builder.add_conditional_edges(
        "inventory",
        after_inventory,
        {
            "reorder_decision": "reorder_decision",
            "aggregate": "aggregate",
        },
    )

    builder.add_conditional_edges(
        "reorder_decision",
        after_reorder,
        {
            "finance": "finance",
            "aggregate": "aggregate",
        },
    )

    builder.add_conditional_edges(
        "finance",
        after_finance,
        {
            "vendor": "vendor",
            "aggregate": "aggregate",
        },
    )

    builder.add_edge("vendor", "aggregate")
    builder.add_edge("aggregate", "respond")
    builder.add_edge("respond", END)

    # Conversation memory is stored per thread_id.
    memory = InMemorySaver()

    return builder.compile(
        # checkpointer=memory
    )


graph = build_graph()
