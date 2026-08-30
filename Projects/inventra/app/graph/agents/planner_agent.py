from app.graph.llm import get_llm
from app.graph.schemas import ExecutionPlan
from app.graph.state import InventraState


async def planner_agent(state: InventraState) -> dict:
    """Choose which specialist capabilities are required."""

    llm = get_llm().with_structured_output(ExecutionPlan)

    result = await llm.ainvoke(
              f"""
      Plan this Inventra request.
      Rules:
      forecast:
        forecast=true
      inventory:
        inventory=true
      finance:
        finance=true
      vendor:
        vendor=true

      reorder_decision:
        forecast=true
        inventory=true
        finance=true
        vendor=true

      For reorder decisions, Finance and Vendor are only executed later
      if the deterministic reorder gate is TRUE.

      Intent: {state.get("intent")}
      SKU: {state.get("sku")}
      Vendor: {state.get("vendor_id")}
      Region: {state.get("region")}
      Date: {state.get("target_date")}
      """
    )

    return result.model_dump()
