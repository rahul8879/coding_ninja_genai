
from sqlalchemy import (
    Column, Integer, String, Float, Text, ForeignKey, DateTime, func
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(String, primary_key=True)
    name = Column(String)
    lead_time_days = Column(Integer)
    unit_price = Column(Float)
    on_time_delivery_rate = Column(Float)
    quality_score = Column(Float)
    avg_delay_days = Column(Float)
    reliability_rating = Column(String)
    return_acceptance_rate = Column(Float)
    total_shipments_last_year = Column(Integer)
    payment_terms_days = Column(Integer)
    bulk_discount_percent = Column(Float)
    min_order_qty = Column(Integer)

    inventory_items = relationship("Inventory", back_populates="vendor")


class Inventory(Base):
    __tablename__ = "inventory"

    sku = Column(String, primary_key=True)
    name = Column(String)
    category = Column(String)
    region = Column(String, index=True)
    qty = Column(Integer)
    reorder_threshold = Column(Integer)
    unit_cost = Column(Float)
    vendor_id = Column(String, ForeignKey("vendors.vendor_id"), index=True)

    vendor = relationship("Vendor", back_populates="inventory_items")

    @property
    def is_below_threshold(self) -> bool:
        """Convenience check used by the Decision Agent."""
        return self.qty is not None and self.reorder_threshold is not None \
            and self.qty <= self.reorder_threshold


class Finance(Base):
    __tablename__ = "finance"

    id = Column(Integer, primary_key=True)
    sku = Column(String, ForeignKey("inventory.sku"), index=True)
    date = Column(String, index=True)  # stored as TEXT (YYYY-MM-DD) to match schema.sql
    amount = Column(Float)
    type = Column(String)  # 'sale' | 'purchase'
    region = Column(String, index=True)


class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    date = Column(String, index=True)
    sku = Column(String, ForeignKey("inventory.sku"), index=True)
    qty = Column(Integer)
    revenue = Column(Float)
    region = Column(String, index=True)
    temperature = Column(Float)
    rainfall = Column(Float)
    humidity = Column(Float)
    weather_condition = Column(String)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, ForeignKey("inventory.sku"), index=True)
    reason = Column(Text)
    recommended_qty = Column(Integer)
    vendor_id = Column(String, ForeignKey("vendors.vendor_id"))
    priority = Column(String, default="medium")
    status = Column(String, default="pending", index=True)
    created_at = Column(DateTime, server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    user_message = Column(Text)
    assistant_message = Column(Text)
    intent = Column(String)
    metadata_ = Column("metadata", Text)  # 'metadata' is reserved in declarative_base
    created_at = Column(DateTime, server_default=func.now())


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_date = Column(String, nullable=False, index=True)
    sku = Column(String, ForeignKey("inventory.sku"), nullable=False, index=True)
    predicted_demand = Column(Integer)
    predicted_weather = Column(String)
    recommendation = Column(Text)
    actual_demand = Column(Integer)
    actual_weather = Column(String)
    accuracy_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
