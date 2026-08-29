

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS forecasts;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS finance;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS vendors;

-- Vendors
CREATE TABLE vendors (
    vendor_id TEXT PRIMARY KEY,
    name TEXT,
    lead_time_days INTEGER,
    unit_price REAL,
    on_time_delivery_rate REAL,
    quality_score REAL,
    avg_delay_days REAL,
    reliability_rating TEXT,
    return_acceptance_rate REAL,
    total_shipments_last_year INTEGER,
    payment_terms_days INTEGER,
    bulk_discount_percent REAL,
    min_order_qty INTEGER
);

-- Inventory
CREATE TABLE inventory (
    sku TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    region TEXT,
    qty INTEGER,
    reorder_threshold INTEGER,
    unit_cost REAL,
    vendor_id TEXT,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);
CREATE INDEX idx_inventory_region ON inventory(region);
CREATE INDEX idx_inventory_vendor ON inventory(vendor_id);

-- Finance transactions
CREATE TABLE finance (
    id INTEGER PRIMARY KEY,
    sku TEXT,
    date TEXT,
    amount REAL,
    type TEXT,
    region TEXT,
    FOREIGN KEY (sku) REFERENCES inventory(sku)
);
CREATE INDEX idx_finance_sku ON finance(sku);
CREATE INDEX idx_finance_date ON finance(date);
CREATE INDEX idx_finance_region ON finance(region);

-- Sales with weather data
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    date TEXT,
    sku TEXT,
    qty INTEGER,
    revenue REAL,
    region TEXT,
    temperature REAL,
    rainfall REAL,
    humidity REAL,
    weather_condition TEXT,
    FOREIGN KEY (sku) REFERENCES inventory(sku)
);
CREATE INDEX idx_sales_sku ON sales(sku);
CREATE INDEX idx_sales_date ON sales(date);
CREATE INDEX idx_sales_region ON sales(region);
CREATE INDEX idx_sales_sku_region ON sales(sku, region);

-- Tickets for actions
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT,
    reason TEXT,
    recommended_qty INTEGER,
    vendor_id TEXT,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (sku) REFERENCES inventory(sku),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_sku ON tickets(sku);

-- Conversation history for persistent memory
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT,
    assistant_message TEXT,
    intent TEXT,
    metadata TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_conversations_session ON conversations(session_id);

-- Forecast tracking for accuracy evaluation
CREATE TABLE forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_date TEXT NOT NULL,
    sku TEXT NOT NULL,
    predicted_demand INTEGER,
    predicted_weather TEXT,
    recommendation TEXT,
    actual_demand INTEGER,
    actual_weather TEXT,
    accuracy_score REAL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (sku) REFERENCES inventory(sku)
);
CREATE INDEX idx_forecasts_sku ON forecasts(sku);
CREATE INDEX idx_forecasts_date ON forecasts(forecast_date);
