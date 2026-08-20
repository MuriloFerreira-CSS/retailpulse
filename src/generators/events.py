from pathlib import Path
import random

import pandas as pd


random.seed(42)


SEGMENT_PROBABILITIES = {
    "New": {
        "product_view": 0.65,
        "add_to_cart": 0.18,
        "checkout": 0.08,
        "purchase": 0.04,
    },
    "Returning": {
        "product_view": 0.75,
        "add_to_cart": 0.28,
        "checkout": 0.15,
        "purchase": 0.09,
    },
    "Loyal": {
        "product_view": 0.85,
        "add_to_cart": 0.40,
        "checkout": 0.25,
        "purchase": 0.17,
    },
    "High Value": {
        "product_view": 0.90,
        "add_to_cart": 0.50,
        "checkout": 0.35,
        "purchase": 0.25,
    },
}


DEVICE_MULTIPLIERS = {
    "mobile": 0.90,
    "desktop": 1.10,
    "tablet": 0.95,
}


def generate_events(
    sessions_path: str = "data/raw/sessions.csv",
    customers_path: str = "data/raw/customers.csv",
    products_path: str = "data/raw/products.csv",
) -> pd.DataFrame:

    sessions = pd.read_csv(sessions_path)
    customers = pd.read_csv(customers_path)
    products = pd.read_csv(products_path)

    sessions = sessions.merge(
        customers[
            ["customer_id", "customer_segment"]
        ],
        on="customer_id",
        how="left"
    )

    active_products = products[
        products["is_active"] == True
    ]

    product_ids = active_products[
        "product_id"
    ].tolist()

    events = []
    event_counter = 1

    for _, session in sessions.iterrows():
        session_id = session["session_id"]
        customer_id = session["customer_id"]
        segment = session["customer_segment"]
        device = session["device"]

        session_start = pd.to_datetime(
            session["session_start"]
        )

        probabilities = SEGMENT_PROBABILITIES[
            segment
        ]

        device_multiplier = DEVICE_MULTIPLIERS[
            device
        ]

        event_time = session_start

        events.append({
            "event_id": f"E{event_counter:08d}",
            "session_id": session_id,
            "customer_id": customer_id,
            "event_type": "page_view",
            "product_id": None,
            "event_timestamp": event_time,
        })

        event_counter += 1

        product_view_probability = min(
            probabilities["product_view"]
            * device_multiplier,
            1
        )

        if random.random() > product_view_probability:
            continue

        product_id = random.choice(product_ids)

        event_time += pd.to_timedelta(
            random.randint(5, 120),
            unit="s"
        )

        events.append({
            "event_id": f"E{event_counter:08d}",
            "session_id": session_id,
            "customer_id": customer_id,
            "event_type": "product_view",
            "product_id": product_id,
            "event_timestamp": event_time,
        })

        event_counter += 1

        add_to_cart_probability = min(
            probabilities["add_to_cart"]
            * device_multiplier,
            1
        )

        if random.random() > add_to_cart_probability:
            continue

        event_time += pd.to_timedelta(
            random.randint(10, 180),
            unit="s"
        )

        events.append({
            "event_id": f"E{event_counter:08d}",
            "session_id": session_id,
            "customer_id": customer_id,
            "event_type": "add_to_cart",
            "product_id": product_id,
            "event_timestamp": event_time,
        })

        event_counter += 1

        checkout_probability = min(
            probabilities["checkout"]
            * device_multiplier,
            1
        )

        if random.random() > checkout_probability:
            continue

        event_time += pd.to_timedelta(
            random.randint(20, 240),
            unit="s"
        )

        events.append({
            "event_id": f"E{event_counter:08d}",
            "session_id": session_id,
            "customer_id": customer_id,
            "event_type": "checkout",
            "product_id": product_id,
            "event_timestamp": event_time,
        })

        event_counter += 1

        purchase_probability = min(
            probabilities["purchase"]
            * device_multiplier,
            1
        )

        if random.random() > purchase_probability:
            continue

        event_time += pd.to_timedelta(
            random.randint(20, 180),
            unit="s"
        )

        events.append({
            "event_id": f"E{event_counter:08d}",
            "session_id": session_id,
            "customer_id": customer_id,
            "event_type": "purchase",
            "product_id": product_id,
            "event_timestamp": event_time,
        })

        event_counter += 1

    return pd.DataFrame(events)


if __name__ == "__main__":
    df_events = generate_events()

    output_path = Path(
        "data/raw/events.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df_events.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"{len(df_events)} eventos gerados com sucesso."
    )

    print("\nEventos por tipo:")
    print(
        df_events["event_type"]
        .value_counts()
    )

    print("\nPrimeiros registros:")
    print(df_events.head())
    