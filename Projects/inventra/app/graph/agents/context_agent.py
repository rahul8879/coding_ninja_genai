from datetime import date, timedelta

from app.graph.llm import get_llm
from app.graph.schemas import ExtractedContext
from app.graph.state import InventraState


async def extract_context(state: InventraState) -> dict:
    """Extract intent and entities, using recent conversation memory."""

    today = date.today()

    history = "\n".join(
        f"{message.type}: {message.content}"
        for message in state.get("messages", [])[-6:]
    )

    llm = get_llm().with_structured_output(ExtractedContext)

    result = await llm.ainvoke(
        f"""
            Extract the current Inventra request.

            Today: {today.isoformat()}
            Tomorrow: {(today + timedelta(days=1)).isoformat()}

            Regions: North, South, East, West, Central.

            Intents:
            - reorder_decision
            - forecast
            - inventory
            - finance
            - vendor
            - general

            Use recent conversation only when the current request omits context
            that was clearly established earlier.

            Recent conversation:
            {history}

            Current request:
            {state["user_query"]}
            """
    )

    return result.model_dump()
