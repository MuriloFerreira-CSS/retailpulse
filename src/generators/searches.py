from pathlib import Path
import random

import pandas as pd


random.seed(42)


SEARCH_USAGE_RATE = 0.35

COLORS = [
    "preto",
    "branco",
    "azul",
    "vermelho",
    "verde",
    "bege",
    "marrom",
    "rosa",
]

ZERO_RESULT_TERMS = [
    "vestido holografico",
    "tenis neon premium",
    "jaqueta espacial",
    "calca prata metalica",
    "bota holografica",
    "bolsa transparente neon",
    "oculos futurista dourado",
    "camiseta led",
]


def build_search_term(product: pd.Series) -> str:
    search_type = random.choice(
        [
            "subcategory",
            "brand",
            "subcategory_color",
            "brand_subcategory",
        ]
    )

    subcategory = product["subcategory"].lower()
    brand = product["brand"].lower()

    if search_type == "subcategory":
        return subcategory

    if search_type == "brand":
        return brand

    if search_type == "subcategory_color":
        color = random.choice(COLORS)
        return f"{subcategory} {color}"

    return f"{brand} {subcategory}"


def generate_searches(
    sessions_path: str = "data/raw/sessions.csv",
    products_path: str = "data/raw/products.csv",
    events_path: str = "data/raw/events.csv",
) -> pd.DataFrame:

    sessions = pd.read_csv(sessions_path)
    products = pd.read_csv(products_path)
    events = pd.read_csv(events_path)

    active_products = products[
        products["stock"] > 0
    ].copy()

    purchase_events = events[
        events["event_type"] == "purchase"
    ][
        ["session_id", "product_id"]
    ].copy()

    purchase_by_session = dict(
        zip(
            purchase_events["session_id"],
            purchase_events["product_id"],
        )
    )

    product_lookup = active_products.set_index(
        "product_id"
    )

    searches = []
    search_counter = 1

    for _, session in sessions.iterrows():

        if random.random() > SEARCH_USAGE_RATE:
            continue

        session_id = session["session_id"]
        customer_id = session["customer_id"]

        session_start = pd.to_datetime(
            session["session_start"]
        )

        session_duration = int(
            session["session_duration_seconds"]
        )

        number_of_searches = random.choices(
            population=[1, 2, 3],
            weights=[70, 25, 5],
            k=1,
        )[0]

        for _ in range(number_of_searches):

            max_search_offset = max(
                min(
                    session_duration - 1,
                    600,
                ),
                1,
            )

            search_timestamp = (
                session_start
                + pd.to_timedelta(
                    random.randint(
                        1,
                        max_search_offset,
                    ),
                    unit="s",
                )
            )

            is_zero_result = (
                random.random() < 0.12
            )

            clicked_product_id = None
            generated_purchase = False
            revenue = 0.0

            if is_zero_result:

                search_term = random.choice(
                    ZERO_RESULT_TERMS
                )

                results_count = 0

            else:

                purchase_product_id = (
                    purchase_by_session.get(
                        session_id
                    )
                )

                if (
                    purchase_product_id is not None
                    and purchase_product_id
                    in product_lookup.index
                    and random.random() < 0.70
                ):
                    selected_product = (
                        product_lookup.loc[
                            purchase_product_id
                        ]
                    )

                    selected_product_id = (
                        purchase_product_id
                    )

                else:

                    selected_product = (
                        active_products.sample(
                            n=1,
                            random_state=random.randint(
                                1,
                                1_000_000,
                            ),
                        ).iloc[0]
                    )

                    selected_product_id = (
                        selected_product[
                            "product_id"
                        ]
                    )

                search_term = build_search_term(
                    selected_product
                )

                results_count = random.randint(
                    1,
                    80,
                )

                click_probability = 0.65

                if (
                    random.random()
                    < click_probability
                ):

                    clicked_product_id = (
                        selected_product_id
                    )

                    if (
                        session_id
                        in purchase_by_session
                        and purchase_by_session[
                            session_id
                        ]
                        == clicked_product_id
                    ):

                        generated_purchase = True

                        revenue = float(
                            selected_product[
                                "price"
                            ]
                        )

            search = {
                "search_id": (
                    f"SRCH{search_counter:07d}"
                ),
                "session_id": session_id,
                "customer_id": customer_id,
                "search_term": search_term,
                "results_count": results_count,
                "clicked_product_id": (
                    clicked_product_id
                ),
                "generated_purchase": (
                    generated_purchase
                ),
                "revenue": round(
                    revenue,
                    2,
                ),
                "search_timestamp": (
                    search_timestamp
                ),
            }

            searches.append(search)
            search_counter += 1

    return pd.DataFrame(searches)


if __name__ == "__main__":

    df_searches = generate_searches()

    output_path = Path(
        "data/raw/searches.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df_searches.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"{len(df_searches)} buscas geradas com sucesso."
    )

    print("\nBuscas sem resultado:")
    print(
        (
            df_searches["results_count"]
            == 0
        ).sum()
    )

    print("\nBuscas com clique:")
    print(
        df_searches[
            "clicked_product_id"
        ].notna().sum()
    )

    print("\nCompras originadas por busca:")
    print(
        df_searches[
            "generated_purchase"
        ].sum()
    )

    print("\nPrimeiros registros:")
    print(
        df_searches.head()
    )