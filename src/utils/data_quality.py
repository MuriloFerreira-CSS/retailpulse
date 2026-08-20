from pathlib import Path

import pandas as pd


DATA_PATH = Path("data/raw")


def load_data():
    customers = pd.read_csv(
        DATA_PATH / "customers.csv"
    )

    products = pd.read_csv(
        DATA_PATH / "products.csv"
    )

    sessions = pd.read_csv(
        DATA_PATH / "sessions.csv"
    )

    events = pd.read_csv(
        DATA_PATH / "events.csv"
    )

    searches = pd.read_csv(
        DATA_PATH / "searches.csv"
    )

    orders = pd.read_csv(
        DATA_PATH / "orders.csv"
    )

    order_items = pd.read_csv(
        DATA_PATH / "order_items.csv"
    )

    return {
        "customers": customers,
        "products": products,
        "sessions": sessions,
        "events": events,
        "searches": searches,
        "orders": orders,
        "order_items": order_items,
    }


def run_check(
    condition: bool,
    description: str,
):
    if condition:
        print(f"[PASS] {description}")
        return True

    print(f"[FAIL] {description}")
    return False


def validate_data():
    data = load_data()

    customers = data["customers"]
    products = data["products"]
    sessions = data["sessions"]
    events = data["events"]
    searches = data["searches"]
    orders = data["orders"]
    order_items = data["order_items"]

    results = []

    print("\n=== RETAILPULSE DATA QUALITY ===\n")

    # -------------------------
    # Customers
    # -------------------------

    results.append(
        run_check(
            customers["customer_id"].is_unique,
            "customer_id is unique",
        )
    )

    results.append(
        run_check(
            customers["customer_id"].notna().all(),
            "customer_id has no null values",
        )
    )

    # -------------------------
    # Products
    # -------------------------

    results.append(
        run_check(
            products["product_id"].is_unique,
            "product_id is unique",
        )
    )

    results.append(
        run_check(
            (products["price"] > 0).all(),
            "all products have positive prices",
        )
    )

    results.append(
        run_check(
            (products["stock"] >= 0).all(),
            "product stock is never negative",
        )
    )

    # -------------------------
    # Sessions
    # -------------------------

    results.append(
        run_check(
            sessions["session_id"].is_unique,
            "session_id is unique",
        )
    )

    results.append(
        run_check(
            sessions["customer_id"].isin(
                customers["customer_id"]
            ).all(),
            "all sessions reference valid customers",
        )
    )

    session_dates = pd.to_datetime(
        sessions["session_start"]
    )

    today = pd.Timestamp.today().normalize()

    results.append(
        run_check(
            (session_dates <= today).all(),
            "no sessions occur in the future",
        )
    )

    # -------------------------
    # Events
    # -------------------------

    results.append(
        run_check(
            events["event_id"].is_unique,
            "event_id is unique",
        )
    )

    results.append(
        run_check(
            events["session_id"].isin(
                sessions["session_id"]
            ).all(),
            "all events reference valid sessions",
        )
    )

    results.append(
        run_check(
            events["customer_id"].isin(
                customers["customer_id"]
            ).all(),
            "all events reference valid customers",
        )
    )

    # -------------------------
    # Purchases vs Orders
    # -------------------------

    purchase_events = events[
        events["event_type"] == "purchase"
    ]

    results.append(
        run_check(
            len(purchase_events) == len(orders),
            "purchase events count matches orders count",
        )
    )

    results.append(
        run_check(
            orders["order_id"].is_unique,
            "order_id is unique",
        )
    )

    results.append(
        run_check(
            orders["session_id"].isin(
                sessions["session_id"]
            ).all(),
            "all orders reference valid sessions",
        )
    )

    results.append(
        run_check(
            orders["customer_id"].isin(
                customers["customer_id"]
            ).all(),
            "all orders reference valid customers",
        )
    )

    results.append(
        run_check(
            (orders["total_amount"] >= 0).all(),
            "order totals are never negative",
        )
    )

    # -------------------------
    # Order Items
    # -------------------------

    results.append(
        run_check(
            order_items["order_item_id"].is_unique,
            "order_item_id is unique",
        )
    )

    results.append(
        run_check(
            order_items["order_id"].isin(
                orders["order_id"]
            ).all(),
            "all order items reference valid orders",
        )
    )

    results.append(
        run_check(
            order_items["product_id"].isin(
                products["product_id"]
            ).all(),
            "all order items reference valid products",
        )
    )

    results.append(
        run_check(
            (order_items["quantity"] > 0).all(),
            "all order item quantities are positive",
        )
    )

    # -------------------------
    # Searches
    # -------------------------

    results.append(
        run_check(
            searches["search_id"].is_unique,
            "search_id is unique",
        )
    )

    results.append(
        run_check(
            searches["session_id"].isin(
                sessions["session_id"]
            ).all(),
            "all searches reference valid sessions",
        )
    )

    clicked_products = searches[
        "clicked_product_id"
    ].dropna()

    results.append(
        run_check(
            clicked_products.isin(
                products["product_id"]
            ).all(),
            "all clicked products are valid products",
        )
    )

    results.append(
        run_check(
            (
                searches["results_count"] >= 0
            ).all(),
            "search result counts are never negative",
        )
    )

    # -------------------------
    # Final Result
    # -------------------------

    passed = sum(results)
    total = len(results)
    failed = total - passed

    print("\n==============================")
    print(f"Checks passed: {passed}/{total}")
    print(f"Checks failed: {failed}")
    print("==============================")

    if failed == 0:
        print("\nDATA QUALITY STATUS: PASSED ✅")
    else:
        print("\nDATA QUALITY STATUS: FAILED ❌")


if __name__ == "__main__":
    validate_data()