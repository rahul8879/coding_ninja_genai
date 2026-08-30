"""
Inventra Vendor Service.
Provides deterministic vendor capabilities backed by the real Vendors table.

The actual vendors.csv columns used are:

    vendor_id
    name
    lead_time_days
    unit_price
    on_time_delivery_rate
    quality_score
    avg_delay_days
    reliability_rating
    return_acceptance_rate
    total_shipments_last_year
    payment_terms_days
    bulk_discount_percent
    min_order_qty

"""

from typing import Optional

from db.session import SessionLocal
from db.models import Vendor


class VendorService:
    """Vendor lookup, procurement details, and transparent supplier scoring."""

    def vendor_details(self, vendor_id: str) -> dict:
        """Return the complete vendor profile for one vendor."""

        db = SessionLocal()

        try:
            vendor = (
                db.query(Vendor)
                .filter(Vendor.vendor_id == vendor_id)
                .first()
            )

            if vendor is None:
                return {"error": f"Unknown vendor '{vendor_id}'."}

            return {
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "lead_time_days": vendor.lead_time_days,
                "unit_price": vendor.unit_price,
                "on_time_delivery_rate": vendor.on_time_delivery_rate,
                "quality_score": vendor.quality_score,
                "avg_delay_days": vendor.avg_delay_days,
                "reliability_rating": vendor.reliability_rating,
                "return_acceptance_rate": vendor.return_acceptance_rate,
                "total_shipments_last_year": vendor.total_shipments_last_year,
                "payment_terms_days": vendor.payment_terms_days,
                "bulk_discount_percent": vendor.bulk_discount_percent,
                "min_order_qty": vendor.min_order_qty,
            }

        finally:
            db.close()

    def lead_time(self, vendor_id: str) -> dict:
        """Return procurement timing and delivery reliability information."""

        db = SessionLocal()

        try:
            vendor = (
                db.query(Vendor)
                .filter(Vendor.vendor_id == vendor_id)
                .first()
            )

            if vendor is None:
                return {"error": f"Unknown vendor '{vendor_id}'."}

            return {
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "lead_time_days": vendor.lead_time_days,
                "avg_delay_days": vendor.avg_delay_days,
                "on_time_delivery_rate": vendor.on_time_delivery_rate,
                "reliability_rating": vendor.reliability_rating,
            }

        finally:
            db.close()

    def supplier_score(self, vendor_id: str) -> dict:
        """
        Calculate a transparent POC supplier score using only real columns.

        Components:
            30% on-time delivery rate
            25% quality score
            25% reliability rating
            10% return acceptance rate
            10% delay score

        Assumptions for this POC:
            - rate columns can be 0-1 or 0-100
            - quality_score and reliability_rating are on a 1-5 scale
            - delay score penalizes average delay linearly:
                  0 days  -> 100
                  10 days -> 0

        These weights are business rules, not ML.
        """

        db = SessionLocal()

        try:
            vendor = (
                db.query(Vendor)
                .filter(Vendor.vendor_id == vendor_id)
                .first()
            )

            if vendor is None:
                return {"error": f"Unknown vendor '{vendor_id}'."}

            def to_percent(value: float) -> float:
                value = float(value or 0.0)
                return value * 100 if value <= 1 else value

            on_time_pct = to_percent(vendor.on_time_delivery_rate)
            return_acceptance_pct = to_percent(vendor.return_acceptance_rate)

            quality_pct = min(
                max(float(vendor.quality_score or 0.0) / 5 * 100, 0),
                100,
            )

            reliability_pct = min(
                max(float(vendor.reliability_rating or 0.0) / 5 * 100, 0),
                100,
            )

            avg_delay_days = float(vendor.avg_delay_days or 0.0)

            delay_score = max(
                0.0,
                min(100.0, 100.0 - avg_delay_days * 10),
            )

            score = (
                0.30 * on_time_pct
                + 0.25 * quality_pct
                + 0.25 * reliability_pct
                + 0.10 * return_acceptance_pct
                + 0.10 * delay_score
            )

            if score >= 85:
                score_band = "Excellent"
            elif score >= 70:
                score_band = "Good"
            elif score >= 55:
                score_band = "Moderate"
            else:
                score_band = "High Risk"

            return {
                "vendor_id": vendor.vendor_id,
                "name": vendor.name,
                "supplier_score": round(score, 2),
                "score_band": score_band,
                "components": {
                    "on_time_delivery_score": round(on_time_pct, 2),
                    "quality_score": round(quality_pct, 2),
                    "reliability_score": round(reliability_pct, 2),
                    "return_acceptance_score": round(return_acceptance_pct, 2),
                    "delay_score": round(delay_score, 2),
                },
                "weights": {
                    "on_time_delivery": 0.30,
                    "quality": 0.25,
                    "reliability": 0.25,
                    "return_acceptance": 0.10,
                    "delay": 0.10,
                },
                "lead_time_days": vendor.lead_time_days,
                "avg_delay_days": vendor.avg_delay_days,
                "unit_price": vendor.unit_price,
                "bulk_discount_percent": vendor.bulk_discount_percent,
                "min_order_qty": vendor.min_order_qty,
                "payment_terms_days": vendor.payment_terms_days,
            }

        finally:
            db.close()

    def list_vendors(self) -> list[dict]:
        """List every vendor available in the vendor master."""

        db = SessionLocal()

        try:
            vendors = (
                db.query(Vendor)
                .order_by(Vendor.vendor_id)
                .all()
            )

            return [
                {
                    "vendor_id": vendor.vendor_id,
                    "name": vendor.name,
                    "lead_time_days": vendor.lead_time_days,
                    "unit_price": vendor.unit_price,
                    "min_order_qty": vendor.min_order_qty,
                }
                for vendor in vendors
            ]

        finally:
            db.close()


_vendor_service_instance: Optional[VendorService] = None


def get_vendor_service() -> VendorService:
    """Return one shared VendorService instance."""

    global _vendor_service_instance

    if _vendor_service_instance is None:
        _vendor_service_instance = VendorService()

    return _vendor_service_instance
