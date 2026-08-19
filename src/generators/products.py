from pathlib import Path
import random

import pandas as pd
from faker import Faker


fake = Faker("pt_BR")

Faker.seed(42)
random.seed(42)


PRODUCT_CATALOG = {
    "Roupas": {
        "Camisetas": (39.90, 149.90),
        "Calças": (79.90, 249.90),
        "Vestidos": (89.90, 299.90),
        "Moletons": (99.90, 249.90),
        "Jaquetas": (149.90, 499.90),
    },
    "Calçados": {
        "Tênis": (129.90, 599.90),
        "Botas": (179.90, 599.90),
        "Sandálias": (69.90, 249.90),
        "Sapatos": (149.90, 499.90),
    },
    "Acessórios": {
        "Bolsas": (79.90, 399.90),
        "Bonés": (39.90, 129.90),
        "Cintos": (39.90, 149.90),
        "Óculos": (69.90, 299.90),
        "Joias": (59.90, 499.90),
    },
}


BRANDS = [
    "Pulse",
    "Urban Wave",
    "North",
    "Essence",
    "Vitta",
    "Nova",
]


def generate_products(quantity: int = 500) -> pd.DataFrame:
    products = []

    for i in range(1, quantity + 1):
        category = random.choice(list(PRODUCT_CATALOG.keys()))

        subcategory = random.choice(
            list(PRODUCT_CATALOG[category].keys())
        )

        min_price, max_price = PRODUCT_CATALOG[category][subcategory]

        price = round(
            random.uniform(min_price, max_price),
            2
        )

        cost = round(
            price * random.uniform(0.30, 0.60),
            2
        )

        stock = random.randint(0, 300)

        rating = round(
            random.uniform(3.0, 5.0),
            1
        )

        brand = random.choice(BRANDS)

        product = {
            "product_id": f"P{i:05d}",
            "product_name": f"{subcategory} {brand} {i}",
            "category": category,
            "subcategory": subcategory,
            "brand": brand,
            "price": price,
            "cost": cost,
            "stock": stock,
            "rating": rating,
            "is_active": stock > 0,
        }

        products.append(product)

    return pd.DataFrame(products)


if __name__ == "__main__":
    df_products = generate_products()

    output_path = Path("data/raw/products.csv")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df_products.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"{len(df_products)} produtos gerados com sucesso.")
    print(df_products.head())