from pathlib import Path

import pandas as pd
from faker import Faker


fake = Faker("pt_BR")
Faker.seed(42)


def generate_customers(quantity: int = 5000) -> pd.DataFrame:
    customers = []

    for i in range(1, quantity + 1):
        customer = {
            "customer_id": f"C{i:05d}",
            "name": fake.name(),
            "email": fake.unique.email(),
            "birth_date": fake.date_of_birth(
                minimum_age=18,
                maximum_age=70
            ),
            "city": fake.city(),
            "state": fake.estado_sigla(),
            "signup_date": fake.date_between(
                start_date="-3y",
                end_date="today"
            ),
        }

        customers.append(customer)

    return pd.DataFrame(customers)


if __name__ == "__main__":
    df_customers = generate_customers()

    output_path = Path("data/raw/customers.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_customers.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"{len(df_customers)} clientes gerados com sucesso.")
    print(df_customers.head())