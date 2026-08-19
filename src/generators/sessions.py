from pathlib import Path
import random

import pandas as pd


random.seed(42)


SESSION_RANGES = {
    "New": (1, 3),
    "Returning": (2, 6),
    "Loyal": (5, 12),
    "High Value": (8, 18),
}

DEVICES = ["mobile", "desktop", "tablet"]
DEVICE_WEIGHTS = [65, 30, 5]

TRAFFIC_SOURCES = [
    "organic",
    "paid_search",
    "paid_social",
    "direct",
    "email",
    "referral",
]

TRAFFIC_WEIGHTS = [30, 20, 18, 15, 10, 7]


def generate_sessions(customers_path: str = "data/raw/customers.csv") -> pd.DataFrame:
    customers = pd.read_csv(customers_path)

    sessions = []
    session_counter = 1

    for _, customer in customers.iterrows():
        segment = customer["customer_segment"]

        min_sessions, max_sessions = SESSION_RANGES[segment]
        number_of_sessions = random.randint(min_sessions, max_sessions)

        signup_date = pd.to_datetime(customer["signup_date"])

        for _ in range(number_of_sessions):
            session_start = signup_date + pd.to_timedelta(
                random.randint(0, 365),
                unit="D"
            )

            device = random.choices(
                DEVICES,
                weights=DEVICE_WEIGHTS,
                k=1
            )[0]

            traffic_source = random.choices(
                TRAFFIC_SOURCES,
                weights=TRAFFIC_WEIGHTS,
                k=1
            )[0]

            session_duration_seconds = random.randint(20, 1800)
            pages_viewed = random.randint(1, 20)

            session = {
                "session_id": f"S{session_counter:07d}",
                "customer_id": customer["customer_id"],
                "session_start": session_start,
                "device": device,
                "traffic_source": traffic_source,
                "session_duration_seconds": session_duration_seconds,
                "pages_viewed": pages_viewed,
            }

            sessions.append(session)
            session_counter += 1

    return pd.DataFrame(sessions)


if __name__ == "__main__":
    df_sessions = generate_sessions()

    output_path = Path("data/raw/sessions.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_sessions.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"{len(df_sessions)} sessões geradas com sucesso.")
    print(df_sessions.head())