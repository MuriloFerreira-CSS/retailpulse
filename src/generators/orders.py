from pathlib import Path
import random

import pandas as pd


random.seed(42)


PAYMENT_METHODS = [
    "credit_card",
    "pix",
    "debit_card",
    "boleto",
]

PAYMENT_WEIGHTS = [
    55,
    30,
    10,
    5,
]


def generate_orders(
    events_path: str = "data/raw/events.csv",
    products_path: str = "data/raw/products.csv",
):
    events = pd.read_csv(events_path)
    products = pd.read_csv(products_path)

    purchase_events = events[
        events["event_type"] == "purchase"
    ].copy()

    product_lookup = products.set_index(
        "product_id"
    )

    orders = []
    order_items = []

    order_counter = 1
    order_item_counter = 1

    for _, purchase in purchase_events.iterrows():

        product_id = purchase["product_id"]

        if product_id not in product_lookup.index:
            continue

        product = product_lookup.loc[
            product_id
        ]

        unit_price = float(
            product["price"]
        )

        quantity = random.choices(
            population=[1, 2, 3],
            weights=[80, 17, 3],
            k=1,
        )[0]

        subtotal = round(
            unit_price * quantity,
            2,
        )

        discount_percentage = random.choices(
            population=[0, 5, 10, 15],
            weights=[65, 20, 10, 5],
            k=1,
        )[0]

        discount_amount = round(
            subtotal
            * (discount_percentage / 100),
            2,
        )

        subtotal_after_discount = (
            subtotal - discount_amount
        )

        if subtotal_after_discount >= 250:
            shipping_cost = 0.0
        else:
            shipping_cost = round(
                random.uniform(
                    9.90,
                    29.90,
                ),
                2,
            )

        total_amount = round(
            subtotal_after_discount
            + shipping_cost,
            2,
        )

        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=PAYMENT_WEIGHTS,
            k=1,
        )[0]

        order_id = f"O{order_counter:07d}"

        order = {
            "order_id": order_id,
            "session_id": purchase[
                "session_id"
            ],
            "customer_id": purchase[
                "customer_id"
            ],
            "order_timestamp": purchase[
                "event_timestamp"
            ],
            "subtotal": subtotal,
            "discount_percentage": (
                discount_percentage
            ),
            "discount_amount": (
                discount_amount
            ),
            "shipping_cost": (
                shipping_cost
            ),
            "total_amount": (
                total_amount
            ),
            "payment_method": (
                payment_method
            ),
            "order_status": "completed",
        }

        order_item = {
            "order_item_id": (
                f"OI{order_item_counter:08d}"
            ),
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": subtotal,
        }

        orders.append(order)
        order_items.append(order_item)

        order_counter += 1
        order_item_counter += 1

    return (
        pd.DataFrame(orders),
        pd.DataFrame(order_items),
    )


if __name__ == "__main__":

    df_orders, df_order_items = (
        generate_orders()
    )

    orders_path = Path(
        "data/raw/orders.csv"
    )

    order_items_path = Path(
        "data/raw/order_items.csv"
    )

    orders_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df_orders.to_csv(
        orders_path,
        index=False,
        encoding="utf-8-sig",
    )

    df_order_items.to_csv(
        order_items_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"{len(df_orders)} pedidos gerados."
    )

    print(
        f"{len(df_order_items)} itens de pedido gerados."
    )

    print(
        "\nReceita total:"
    )

    print(
        f"R$ {df_orders['total_amount'].sum():,.2f}"
    )

    print(
        "\nTicket médio:"
    )

    print(
        f"R$ {df_orders['total_amount'].mean():,.2f}"
    )

    print(
        "\nMétodos de pagamento:"
    )

    print(
        df_orders[
            "payment_method"
        ].value_counts()
    )

    print(
        "\nPrimeiros pedidos:"
    )

    print(
        df_orders.head()
    )