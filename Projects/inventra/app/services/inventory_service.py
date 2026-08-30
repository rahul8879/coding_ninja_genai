"""
Inventra Inventory Service.

Responsibilities:
1. Read current stock for a SKU.
2. Return the configured reorder threshold for a SKU.
3. Evaluate stockout/reorder risk using a forecasted demand value.
4. Calculate a simple recommended reorder quantity.

IMPORTANT:
This service does not forecast demand. Demand comes from ForecastService.
This service only combines that prediction with the current inventory state.
"""

from typing import Optional

from db.session import SessionLocal
from db.models import Inventory


class InventoryService:
    """Inventory lookup and reorder-risk calculations."""

    def get_stock(self, sku: str) -> dict:
        """
        Return the current inventory state for one SKU.

        Args:
            sku:
                Product SKU, for example SKU045.

        Returns:
            Product information, current quantity, reorder threshold,
            region, unit cost, and vendor id.

            Returns an "error" key if the SKU is unknown.
        """

        db = SessionLocal()

        try:
            item = (
                db.query(Inventory)
                .filter(Inventory.sku == sku)
                .first()
            )

            if item is None:
                return {
                    "error": f"Unknown SKU '{sku}'."
                }

            return {
                "sku": item.sku,
                "name": item.name,
                "category": item.category,
                "region": item.region,
                "current_stock": item.qty,
                "reorder_threshold": item.reorder_threshold,
                "unit_cost": item.unit_cost,
                "vendor_id": item.vendor_id,
            }

        finally:
            db.close()

    def reorder_point(self, sku: str) -> dict:
        """
        Return the configured reorder threshold for a SKU.

        Note:
            The current dataset stores a reorder_threshold, not a full
            statistical reorder-point model. We therefore expose the
            real configured threshold instead of inventing safety stock
            or service-level assumptions.
        """

        db = SessionLocal()

        try:
            item = (
                db.query(Inventory)
                .filter(Inventory.sku == sku)
                .first()
            )

            if item is None:
                return {
                    "error": f"Unknown SKU '{sku}'."
                }

            return {
                "sku": item.sku,
                "name": item.name,
                "current_stock": item.qty,
                "reorder_threshold": item.reorder_threshold,
                "needs_reorder_now": (
                    item.qty <= item.reorder_threshold
                ),
            }

        finally:
            db.close()

    def stockout_risk(
        self,
        sku: str,
        predicted_demand: float,
    ) -> dict:
        """
        Evaluate whether forecasted demand creates a stock risk.

        Calculation:

            projected_stock =
                current_stock - predicted_demand

        Reorder is recommended when:

            projected_stock <= reorder_threshold

        Recommended reorder quantity:

            max(
                reorder_threshold - projected_stock,
                0
            )

        This is intentionally simple and deterministic for the POC.

        Args:
            sku:
                Product SKU.

            predicted_demand:
                Numeric demand prediction returned by ForecastService.

        Returns:
            Current stock, forecasted demand, projected stock,
            reorder threshold, risk flag, and recommended reorder quantity.
        """

        if predicted_demand < 0:
            return {
                "error": (
                    "predicted_demand cannot be negative."
                )
            }

        db = SessionLocal()

        try:
            item = (
                db.query(Inventory)
                .filter(Inventory.sku == sku)
                .first()
            )

            if item is None:
                return {
                    "error": f"Unknown SKU '{sku}'."
                }

            current_stock = float(item.qty)
            reorder_threshold = float(
                item.reorder_threshold
            )

            projected_stock = (
                current_stock
                - float(predicted_demand)
            )

            action_required = (
                projected_stock
                <= reorder_threshold
            )

            recommended_reorder_qty = max(
                reorder_threshold
                - projected_stock,
                0.0,
            )

            estimated_reorder_cost = None

            if item.unit_cost is not None:
                estimated_reorder_cost = (
                    recommended_reorder_qty
                    * float(item.unit_cost)
                )

            return {
                "sku": item.sku,
                "name": item.name,
                "category": item.category,
                "region": item.region,

                "current_stock": round(
                    current_stock,
                    2,
                ),

                "predicted_demand": round(
                    float(predicted_demand),
                    2,
                ),

                "projected_stock": round(
                    projected_stock,
                    2,
                ),

                "reorder_threshold": round(
                    reorder_threshold,
                    2,
                ),

                "stockout_risk": (
                    projected_stock < 0
                ),

                "reorder_recommended": (
                    action_required
                ),

                "recommended_reorder_qty": round(
                    recommended_reorder_qty,
                    2,
                ),

                "unit_cost": (
                    round(float(item.unit_cost), 2)
                    if item.unit_cost is not None
                    else None
                ),

                "estimated_reorder_cost": (
                    round(estimated_reorder_cost, 2)
                    if estimated_reorder_cost is not None
                    else None
                ),

                "vendor_id": item.vendor_id,
            }

        finally:
            db.close()

    def list_low_stock_items(self) -> list[dict]:
        """
        Return all SKUs that are already at or below their
        configured reorder threshold.

        This is a deterministic inventory query and does not use
        the forecast model.
        """

        db = SessionLocal()

        try:
            items = (
                db.query(Inventory)
                .filter(
                    Inventory.qty
                    <= Inventory.reorder_threshold
                )
                .order_by(Inventory.qty.asc())
                .all()
            )

            return [
                {
                    "sku": item.sku,
                    "name": item.name,
                    "category": item.category,
                    "region": item.region,
                    "current_stock": item.qty,
                    "reorder_threshold": (
                        item.reorder_threshold
                    ),
                    "vendor_id": item.vendor_id,
                }
                for item in items
            ]

        finally:
            db.close()


_inventory_service_instance: Optional[
    InventoryService
] = None


def get_inventory_service() -> InventoryService:
    """
    Return one shared InventoryService instance.
    """

    global _inventory_service_instance

    if _inventory_service_instance is None:
        _inventory_service_instance = (
            InventoryService()
        )

    return _inventory_service_instance
