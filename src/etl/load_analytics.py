from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ==========================================
# CONFIGURAÇÃO
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}"
    f"@localhost:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)


def get_engine():
    return create_engine(DATABASE_URL)


# ==========================================
# LIMPEZA
# ==========================================

def clear_analytics_tables(engine):
    print("\nLimpando schema analytics...")

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    analytics.fact_order_items,
                    analytics.fact_orders,
                    analytics.fact_searches,
                    analytics.fact_events,
                    analytics.fact_sessions,
                    analytics.dim_product,
                    analytics.dim_customer,
                    analytics.dim_date
                RESTART IDENTITY
                CASCADE;
                """
            )
        )

    print("Schema analytics limpo com sucesso.")


# ==========================================
# DIMENSÃO CLIENTE
# ==========================================

def load_dim_customer(engine):
    query = """
        SELECT
            customer_id,
            name,
            birth_date,
            city,
            state,
            signup_date,
            customer_segment
        FROM raw.customers
        ORDER BY customer_id
    """

    df = pd.read_sql(query, engine)

    df.to_sql(
        name="dim_customer",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] dim_customer: "
        f"{len(df)} registros"
    )


# ==========================================
# DIMENSÃO PRODUTO
# ==========================================

def load_dim_product(engine):
    query = """
        SELECT
            product_id,
            product_name,
            category,
            subcategory,
            brand,
            price,
            cost,
            stock,
            rating,
            is_active
        FROM raw.products
        ORDER BY product_id
    """

    df = pd.read_sql(query, engine)

    df.to_sql(
        name="dim_product",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] dim_product: "
        f"{len(df)} registros"
    )


# ==========================================
# DIMENSÃO DATA
# ==========================================

def load_dim_date(engine):
    query = """
        SELECT session_start AS date_value
        FROM raw.sessions

        UNION ALL

        SELECT event_timestamp
        FROM raw.events

        UNION ALL

        SELECT search_timestamp
        FROM raw.searches

        UNION ALL

        SELECT order_timestamp
        FROM raw.orders
    """

    dates = pd.read_sql(query, engine)

    dates["date_value"] = pd.to_datetime(
        dates["date_value"]
    )

    min_date = dates["date_value"].min().normalize()
    max_date = dates["date_value"].max().normalize()

    calendar = pd.DataFrame(
        {
            "full_date": pd.date_range(
                start=min_date,
                end=max_date,
                freq="D",
            )
        }
    )

    calendar["date_key"] = (
        calendar["full_date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    calendar["year"] = (
        calendar["full_date"].dt.year
    )

    calendar["quarter"] = (
        calendar["full_date"].dt.quarter
    )

    calendar["month"] = (
        calendar["full_date"].dt.month
    )

    calendar["month_name"] = (
        calendar["full_date"].dt.month_name()
    )

    calendar["day"] = (
        calendar["full_date"].dt.day
    )

    calendar["day_of_week"] = (
        calendar["full_date"].dt.dayofweek + 1
    )

    calendar["day_name"] = (
        calendar["full_date"].dt.day_name()
    )

    calendar["is_weekend"] = (
        calendar["full_date"]
        .dt.dayofweek
        .isin([5, 6])
    )

    calendar = calendar[
        [
            "date_key",
            "full_date",
            "year",
            "quarter",
            "month",
            "month_name",
            "day",
            "day_of_week",
            "day_name",
            "is_weekend",
        ]
    ]

    calendar.to_sql(
        name="dim_date",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] dim_date: "
        f"{len(calendar)} registros"
    )


# ==========================================
# FACT SESSIONS
# ==========================================

def load_fact_sessions(engine):
    sessions = pd.read_sql(
        "SELECT * FROM raw.sessions",
        engine,
    )

    customers = pd.read_sql(
        """
        SELECT
            customer_key,
            customer_id
        FROM analytics.dim_customer
        """,
        engine,
    )

    sessions = sessions.merge(
        customers,
        on="customer_id",
        how="left",
    )

    sessions["session_start"] = pd.to_datetime(
        sessions["session_start"]
    )

    sessions["date_key"] = (
        sessions["session_start"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact = sessions[
        [
            "session_id",
            "customer_key",
            "session_start",
            "date_key",
            "device",
            "traffic_source",
            "session_duration_seconds",
            "pages_viewed",
        ]
    ]

    fact.to_sql(
        name="fact_sessions",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] fact_sessions: "
        f"{len(fact)} registros"
    )


# ==========================================
# FACT EVENTS
# ==========================================

def load_fact_events(engine):
    events = pd.read_sql(
        "SELECT * FROM raw.events",
        engine,
    )

    customers = pd.read_sql(
        """
        SELECT
            customer_key,
            customer_id
        FROM analytics.dim_customer
        """,
        engine,
    )

    products = pd.read_sql(
        """
        SELECT
            product_key,
            product_id
        FROM analytics.dim_product
        """,
        engine,
    )

    events = events.merge(
        customers,
        on="customer_id",
        how="left",
    )

    events = events.merge(
        products,
        on="product_id",
        how="left",
    )

    events["event_timestamp"] = pd.to_datetime(
        events["event_timestamp"]
    )

    events["date_key"] = (
        events["event_timestamp"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact = events[
        [
            "event_id",
            "session_id",
            "customer_key",
            "product_key",
            "date_key",
            "event_type",
            "event_timestamp",
        ]
    ]

    fact.to_sql(
        name="fact_events",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] fact_events: "
        f"{len(fact)} registros"
    )


# ==========================================
# FACT SEARCHES
# ==========================================

def load_fact_searches(engine):
    searches = pd.read_sql(
        "SELECT * FROM raw.searches",
        engine,
    )

    customers = pd.read_sql(
        """
        SELECT
            customer_key,
            customer_id
        FROM analytics.dim_customer
        """,
        engine,
    )

    products = pd.read_sql(
        """
        SELECT
            product_key,
            product_id
        FROM analytics.dim_product
        """,
        engine,
    ).rename(
        columns={
            "product_id": "clicked_product_id",
            "product_key": "clicked_product_key",
        }
    )

    searches = searches.merge(
        customers,
        on="customer_id",
        how="left",
    )

    searches = searches.merge(
        products,
        on="clicked_product_id",
        how="left",
    )

    searches["search_timestamp"] = pd.to_datetime(
        searches["search_timestamp"]
    )

    searches["date_key"] = (
        searches["search_timestamp"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact = searches[
        [
            "search_id",
            "session_id",
            "customer_key",
            "clicked_product_key",
            "date_key",
            "search_term",
            "results_count",
            "generated_purchase",
            "revenue",
            "search_timestamp",
        ]
    ]

    fact.to_sql(
        name="fact_searches",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] fact_searches: "
        f"{len(fact)} registros"
    )


# ==========================================
# FACT ORDERS
# ==========================================

def load_fact_orders(engine):
    orders = pd.read_sql(
        "SELECT * FROM raw.orders",
        engine,
    )

    customers = pd.read_sql(
        """
        SELECT
            customer_key,
            customer_id
        FROM analytics.dim_customer
        """,
        engine,
    )

    orders = orders.merge(
        customers,
        on="customer_id",
        how="left",
    )

    orders["order_timestamp"] = pd.to_datetime(
        orders["order_timestamp"]
    )

    orders["date_key"] = (
        orders["order_timestamp"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact = orders[
        [
            "order_id",
            "session_id",
            "customer_key",
            "date_key",
            "order_timestamp",
            "subtotal",
            "discount_percentage",
            "discount_amount",
            "shipping_cost",
            "total_amount",
            "payment_method",
            "order_status",
        ]
    ]

    fact.to_sql(
        name="fact_orders",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] fact_orders: "
        f"{len(fact)} registros"
    )


# ==========================================
# FACT ORDER ITEMS
# ==========================================

def load_fact_order_items(engine):
    items = pd.read_sql(
        "SELECT * FROM raw.order_items",
        engine,
    )

    products = pd.read_sql(
        """
        SELECT
            product_key,
            product_id
        FROM analytics.dim_product
        """,
        engine,
    )

    items = items.merge(
        products,
        on="product_id",
        how="left",
    )

    fact = items[
        [
            "order_item_id",
            "order_id",
            "product_key",
            "quantity",
            "unit_price",
            "line_total",
        ]
    ]

    fact.to_sql(
        name="fact_order_items",
        con=engine,
        schema="analytics",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] fact_order_items: "
        f"{len(fact)} registros"
    )


# ==========================================
# VALIDAÇÃO
# ==========================================

def validate_analytics(engine):
    tables = [
        "dim_customer",
        "dim_product",
        "dim_date",
        "fact_sessions",
        "fact_events",
        "fact_searches",
        "fact_orders",
        "fact_order_items",
    ]

    print("\nValidando analytics...")

    with engine.connect() as connection:

        for table in tables:
            result = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM analytics.{table}
                    """
                )
            )

            count = result.scalar()

            print(
                f"{table}: {count} registros"
            )


# ==========================================
# PIPELINE
# ==========================================

def main():
    print(
        "\n=== RETAILPULSE ANALYTICS LOAD ==="
    )

    engine = get_engine()

    clear_analytics_tables(engine)

    print("\nCarregando dimensões...")

    load_dim_customer(engine)
    load_dim_product(engine)
    load_dim_date(engine)

    print("\nCarregando fatos...")

    load_fact_sessions(engine)
    load_fact_events(engine)
    load_fact_searches(engine)
    load_fact_orders(engine)
    load_fact_order_items(engine)

    validate_analytics(engine)

    print(
        "\nANALYTICS LOAD STATUS: COMPLETED ✅"
    )


if __name__ == "__main__":
    main()