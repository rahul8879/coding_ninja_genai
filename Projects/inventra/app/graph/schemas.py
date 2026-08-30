from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExtractedContext(BaseModel):
    sku: Optional[str] = Field(
        default=None,
        description="Product SKU such as SKU001."
    )

    vendor_id: Optional[str] = Field(
        default=None,
        description="Vendor ID such as V001."
    )

    region: Optional[
        Literal["North", "South", "East", "West", "Central"]
    ] = None

    target_date: Optional[str] = Field(
        default=None,
        description="YYYY-MM-DD when a date is required."
    )

    intent: Literal[
        "reorder_decision",
        "forecast",
        "inventory",
        "finance",
        "vendor",
        "general",
    ]


class ExecutionPlan(BaseModel):
    needs_forecast: bool = False
    needs_inventory: bool = False
    needs_finance: bool = False
    needs_vendor: bool = False
