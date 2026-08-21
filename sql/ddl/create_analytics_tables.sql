CREATE SCHEMA IF NOT EXISTS analytics;


-- =========================
-- DIMENSIONS
-- =========================

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(150),
    birth_date DATE,
    city VARCHAR(100),
    state VARCHAR(2),
    signup_date DATE,
    customer_segment VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(10) UNIQUE NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    price NUMERIC(10, 2),
    cost NUMERIC(10, 2),
    stock INTEGER,
    rating NUMERIC(3, 1),
    is_active BOOLEAN
);


CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    day INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN
);


-- =========================
-- FACTS
-- =========================

CREATE TABLE IF NOT EXISTS analytics.fact_sessions (
    session_id VARCHAR(20) PRIMARY KEY,

    customer_key INTEGER,

    session_start TIMESTAMP,
    date_key INTEGER,

    device VARCHAR(50),
    traffic_source VARCHAR(50),

    session_duration_seconds INTEGER,
    pages_viewed INTEGER,

    FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key)
);


CREATE TABLE IF NOT EXISTS analytics.fact_events (
    event_id VARCHAR(20) PRIMARY KEY,

    session_id VARCHAR(20),
    customer_key INTEGER,
    product_key INTEGER,
    date_key INTEGER,

    event_type VARCHAR(50),
    event_timestamp TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES analytics.fact_sessions(session_id),

    FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    FOREIGN KEY (product_key)
        REFERENCES analytics.dim_product(product_key),

    FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key)
);


CREATE TABLE IF NOT EXISTS analytics.fact_searches (
    search_id VARCHAR(20) PRIMARY KEY,

    session_id VARCHAR(20),
    customer_key INTEGER,
    clicked_product_key INTEGER,
    date_key INTEGER,

    search_term VARCHAR(255),
    results_count INTEGER,
    generated_purchase BOOLEAN,
    revenue NUMERIC(10, 2),
    search_timestamp TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES analytics.fact_sessions(session_id),

    FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    FOREIGN KEY (clicked_product_key)
        REFERENCES analytics.dim_product(product_key),

    FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key)
);


CREATE TABLE IF NOT EXISTS analytics.fact_orders (
    order_id VARCHAR(20) PRIMARY KEY,

    session_id VARCHAR(20),
    customer_key INTEGER,
    date_key INTEGER,

    order_timestamp TIMESTAMP,

    subtotal NUMERIC(10, 2),
    discount_percentage NUMERIC(5, 2),
    discount_amount NUMERIC(10, 2),
    shipping_cost NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),

    payment_method VARCHAR(50),
    order_status VARCHAR(50),

    FOREIGN KEY (session_id)
        REFERENCES analytics.fact_sessions(session_id),

    FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key)
);


CREATE TABLE IF NOT EXISTS analytics.fact_order_items (
    order_item_id VARCHAR(20) PRIMARY KEY,

    order_id VARCHAR(20),
    product_key INTEGER,

    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    line_total NUMERIC(10, 2),

    FOREIGN KEY (order_id)
        REFERENCES analytics.fact_orders(order_id),

    FOREIGN KEY (product_key)
        REFERENCES analytics.dim_product(product_key)
);