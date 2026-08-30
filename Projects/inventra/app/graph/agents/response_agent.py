import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.llm import get_llm
from app.graph.state import InventraState


async def response_agent(state: InventraState) -> dict:
    if state.get("error"):
        answer = f"Unable to complete the request: {state['error']}"

        return {
            "final_answer": answer,
            "messages": [AIMessage(content=answer)],
        }

    evidence = json.dumps(
        state.get("aggregated_result", {}),
        indent=2,
        default=str,
    )

    response = await get_llm().ainvoke(
        [
            SystemMessage(
                content="""
                You are Inventra's response agent.
                Use only the supplied evidence.
                Never invent business values.
                Be concise.
"""
            ),
            HumanMessage(
                content=(
                    f"Request:\n{state['user_query']}\n\n"
                    f"Evidence:\n{evidence}"
                )
            ),
        ]
    )

    return {
        "final_answer": response.content,
        "messages": [AIMessage(content=response.content)],
    }
