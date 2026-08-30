from typing import Annotated, Optional, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class InventraState(TypedDict, total=False):
    # Conversation memory
    messages: Annotated[list[AnyMessage], add_messages]
    # Current request
    user_query: str
    # Extracted context
    sku: Optional[str]
    vendor_id: Optional[str]
    region: Optional[str]
    target_date: Optional[str]
    intent: Optional[str]

    # Planner
    needs_forecast: bool
    needs_inventory: bool
    needs_finance: bool
    needs_vendor: bool

    # Agent outputs
    weather_result: Optional[dict]
    forecast_result: Optional[dict]
    inventory_result: Optional[dict]
    finance_result: Optional[dict]
    vendor_result: Optional[dict]

    # Business decision
    reorder_needed: Optional[bool]

    # Final
    aggregated_result: Optional[dict]
    final_answer: Optional[str]
    error: Optional[str]
