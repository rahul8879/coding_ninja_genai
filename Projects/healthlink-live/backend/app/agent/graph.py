import json
import logging
from datetime import datetime
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from openai import AsyncOpenAI

from app.tools.executor import TOOLS, execute_tool
from app.agent.llm_client import MODEL
from app.services.scheduling import CLINIC_TZ


logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 4

BOOKING_REPLY = (
    "Please click Confirm booking on the appointment card to "
    "finalize it. Typing yes in chat does not confirm the booking."
)

from app.prompts import load_healthlink_prompt
AGENT_PROMPT = load_healthlink_prompt()


class AgentState(TypedDict):
    messages: list[Any]
    tool_calls: list[dict[str, Any]]
    model_calls: int
    reply: str
    booking_proposal: dict[str, Any] | None


def build_agent(client: AsyncOpenAI):

    async def model_node(state: AgentState):
        # Allow up to four model rounds that can request tools.
        # A subsequent round can only generate the final response.
        allow_tools = state["model_calls"] < MAX_TOOL_ROUNDS

        instructions = (
            AGENT_PROMPT
            + "\nCurrent clinic date and time: "
            + datetime.now(CLINIC_TZ).isoformat(timespec="seconds")
            + "\nClinic timezone: Asia/Kolkata."
        )

        response = await client.responses.create(
            model=MODEL,
            instructions=instructions,
            input=state["messages"],
            tools=TOOLS,
            tool_choice="auto" if allow_tools else "none",
            parallel_tool_calls=False,
            max_output_tokens=800,
            store=False,
        )

        if response.status != "completed":
            raise ValueError("Incomplete model response")

        calls = [
            {
                "name": item.name,
                "arguments": item.arguments,
                "call_id": item.call_id,
            }
            for item in response.output
            if item.type == "function_call"
        ]

        logger.info(
            "agent_model_round round=%s tools_allowed=%s tools=%s",
            state["model_calls"] + 1,
            allow_tools,
            [call["name"] for call in calls],
        )

        if calls and not allow_tools:
            raise ValueError("Agent exceeded tool-call limit")

        reply = response.output_text.strip()

        if not calls and not reply:
            raise ValueError("Agent returned no answer")

        return {
            "messages": state["messages"] + list(response.output),
            "tool_calls": calls,
            "model_calls": state["model_calls"] + 1,
            "reply": reply,
        }

    async def tools_node(state: AgentState):
        outputs = []
        proposal = state.get("booking_proposal")

        for call in state["tool_calls"]:
            logger.info(
                "agent_tool_started name=%s",
                call["name"],
            )

            result = await execute_tool(
                call["name"],
                call["arguments"],
            )

            if call["name"] == "prepare_booking":
                proposal = (
                    result.get("booking_proposal")
                    if result.get("ok")
                    else None
                )

                logger.info(
                    "booking_proposal_prepared success=%s",
                    proposal is not None,
                )

            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call["call_id"],
                    "output": json.dumps(result),
                }
            )

        return {
            "messages": state["messages"] + outputs,
            "booking_proposal": proposal,
        }

    async def booking_reply_node(state: AgentState):
        # A successful tool result already contains the card data.
        # Return a clear instruction without another model call that
        # could introduce a repeated yes/no confirmation question.
        return {"reply": BOOKING_REPLY}

    def after_model(state: AgentState):
        return "tools" if state["tool_calls"] else "done"

    def after_tools(state: AgentState):
        if state.get("booking_proposal") is not None:
            return "booking_reply"

        return "model"

    graph = StateGraph(AgentState)

    graph.add_node("model", model_node)
    graph.add_node("tools", tools_node)
    graph.add_node("booking_reply", booking_reply_node)

    graph.add_edge(START, "model")

    graph.add_conditional_edges(
        "model",
        after_model,
        {
            "tools": "tools",
            "done": END,
        },
    )

    graph.add_conditional_edges(
        "tools",
        after_tools,
        {
            "booking_reply": "booking_reply",
            "model": "model",
        },
    )

    graph.add_edge("booking_reply", END)

    return graph.compile()