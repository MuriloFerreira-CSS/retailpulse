CREATE SCHEMA IF NOT EXISTS raw;


CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(150),
    email VARCHAR(200),
    birth_date DATE,
    city VARCHAR(100),
    state VARCHAR(2),
    signup_date DATE,
    customer_segment VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS raw.products (
    product_id VARCHAR(10) PRIMARY KEY,
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


CREATE TABLE IF NOT EXISTS raw.sessions (
    session_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(10),
    session_start TIMESTAMP,
    device VARCHAR(50),
    traffic_source VARCHAR(50),
    session_duration_seconds INTEGER,
    pages_viewed INTEGER,

    FOREIGN KEY (customer_id)
        REFERENCES raw.customers(customer_id)
);


CREATE TABLE IF NOT EXISTS raw.events (
    event_id VARCHAR(20) PRIMARY KEY,
    session_id VARCHAR(20),
    customer_id VARCHAR(10),
    event_type VARCHAR(50),
    product_id VARCHAR(10),
    event_timestamp TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES raw.sessions(session_id),

    FOREIGN KEY (customer_id)
        REFERENCES raw.customers(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES raw.products(product_id)
);


CREATE TABLE IF NOT EXISTS raw.searches (
    search_id VARCHAR(20) PRIMARY KEY,
    session_id VARCHAR(20),
    customer_id VARCHAR(10),
    search_term VARCHAR(255),
    results_count INTEGER,
    clicked_product_id VARCHAR(10),
    generated_purchase BOOLEAN,
    revenue NUMERIC(10, 2),
    search_timestamp TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES raw.sessions(session_id),

    FOREIGN KEY (customer_id)
        REFERENCES raw.customers(customer_id),

    FOREIGN KEY (clicked_product_id)
        REFERENCES raw.products(product_id)
);


CREATE TABLE IF NOT EXISTS raw.orders (
    order_id VARCHAR(20) PRIMARY KEY,
    session_id VARCHAR(20),
    customer_id VARCHAR(10),
    order_timestamp TIMESTAMP,
    subtotal NUMERIC(10, 2),
    discount_percentage NUMERIC(5, 2),
    discount_amount NUMERIC(10, 2),
    shipping_cost NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),
    payment_method VARCHAR(50),
    order_status VARCHAR(50),

    FOREIGN KEY (session_id)
        REFERENCES raw.sessions(session_id),

    FOREIGN KEY (customer_id)
        REFERENCES raw.customers(customer_id)
);


CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20),
    product_id VARCHAR(10),
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    line_total NUMERIC(10, 2),

    FOREIGN KEY (order_id)
        REFERENCES raw.orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES raw.products(product_id)
);