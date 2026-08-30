"""
Inventra Finance Service.

Provides:
1. cash_position()
2. margin()

No artificial budget-check tool is included because the supplied datasets
do not contain a reliable budget/limit field.

Important terminology:
sales - purchases from the finance ledger is reported as
"ledger_net_cash_flow", not "ledger_net_margin".
"""

from typing import Optional

from sqlalchemy import func

from db.session import SessionLocal
from db.models import Finance, Sales, Inventory


class FinanceService:
    """Cash position and per-SKU unit economics."""

    def cash_position(
        self,
        region: Optional[str] = None,
    ) -> dict:
        """
        Net cash position from finance ledger:

            sale transactions - purchase transactions

        Args:
            region: Optional region filter.

        Returns:
            Company-wide or regional ledger cash summary.
        """

        db = SessionLocal()

        try:
            query = db.query(Finance)

            if region:
                query = query.filter(
                    Finance.region == region
                )

            sales_total = (
                query.filter(Finance.type == "sale")
                .with_entities(
                    func.sum(Finance.amount),
                    func.count(Finance.id),
                )
                .first()
            )

            purchases_total = (
                query.filter(Finance.type == "purchase")
                .with_entities(
                    func.sum(Finance.amount),
                    func.count(Finance.id),
                )
                .first()
            )

            total_sales = sales_total[0] or 0.0
            sales_count = sales_total[1] or 0

            total_purchases = purchases_total[0] or 0.0
            purchases_count = purchases_total[1] or 0

            return {
                "region": region or "all",
                "total_sales": round(total_sales, 2),
                "sales_transaction_count": sales_count,
                "total_purchases": round(total_purchases, 2),
                "purchase_transaction_count": purchases_count,
                "net_cash_position": round(
                    total_sales - total_purchases,
                    2,
                ),
            }

        finally:
            db.close()

    def margin(
        self,
        sku: str,
    ) -> dict:
        """
        Calculate unit economics and historical ledger cash movement.

        Unit margin:
            average selling price - unit cost

        Ledger cash flow:
            finance sale transactions - finance purchase transactions

        Note:
            Ledger cash flow is not the same as accounting gross margin.
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

            sales_total = (
                db.query(func.sum(Finance.amount))
                .filter(
                    Finance.sku == sku,
                    Finance.type == "sale",
                )
                .scalar()
            ) or 0.0

            purchases_total = (
                db.query(func.sum(Finance.amount))
                .filter(
                    Finance.sku == sku,
                    Finance.type == "purchase",
                )
                .scalar()
            ) or 0.0

            sales_summary = (
                db.query(
                    func.sum(Sales.qty),
                    func.sum(Sales.revenue),
                )
                .filter(Sales.sku == sku)
                .first()
            )

            total_qty_sold = sales_summary[0] or 0
            total_revenue = sales_summary[1] or 0.0

            avg_selling_price = None
            unit_margin = None
            unit_margin_percent = None

            if total_qty_sold > 0:
                avg_selling_price = (
                    total_revenue / total_qty_sold
                )

                if item.unit_cost is not None:
                    unit_margin = (
                        avg_selling_price - item.unit_cost
                    )

                    if avg_selling_price > 0:
                        unit_margin_percent = (
                            unit_margin
                            / avg_selling_price
                        ) * 100

            return {
                "sku": sku,
                "name": item.name,
                "category": item.category,
                "unit_cost": (
                    round(item.unit_cost, 2)
                    if item.unit_cost is not None
                    else None
                ),
                "avg_selling_price": (
                    round(avg_selling_price, 2)
                    if avg_selling_price is not None
                    else None
                ),
                "unit_margin": (
                    round(unit_margin, 2)
                    if unit_margin is not None
                    else None
                ),
                "unit_margin_percent": (
                    round(unit_margin_percent, 2)
                    if unit_margin_percent is not None
                    else None
                ),
                "ledger_total_sales": round(
                    sales_total,
                    2,
                ),
                "ledger_total_purchases": round(
                    purchases_total,
                    2,
                ),
                "ledger_net_cash_flow": round(
                    sales_total - purchases_total,
                    2,
                ),
            }

        finally:
            db.close()


_finance_service_instance: Optional[FinanceService] = None


def get_finance_service() -> FinanceService:
    """Return one shared FinanceService instance."""

    global _finance_service_instance

    if _finance_service_instance is None:
        _finance_service_instance = FinanceService()

    return _finance_service_instance
