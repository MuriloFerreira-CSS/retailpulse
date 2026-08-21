from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()


DATA_PATH = Path("data/raw")


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


TABLES = [
    "customers",
    "products",
    "sessions",
    "events",
    "searches",
    "orders",
    "order_items",
]


def get_engine():
    return create_engine(
        DATABASE_URL
    )


def clear_raw_tables(engine):
    print("\nLimpando tabelas raw...")

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    raw.order_items,
                    raw.orders,
                    raw.searches,
                    raw.events,
                    raw.sessions,
                    raw.products,
                    raw.customers
                RESTART IDENTITY
                CASCADE;
                """
            )
        )

    print("Tabelas limpas com sucesso.")


def load_table(
    engine,
    table_name: str
):
    file_path = (
        DATA_PATH
        / f"{table_name}.csv"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: "
            f"{file_path}"
        )

    df = pd.read_csv(
        file_path
    )

    df.to_sql(
        name=table_name,
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"[OK] {table_name}: "
        f"{len(df)} registros carregados"
    )


def validate_load(engine):
    print(
        "\nValidando registros no PostgreSQL..."
    )

    with engine.connect() as connection:

        for table_name in TABLES:

            result = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM raw.{table_name}
                    """
                )
            )

            count = result.scalar()

            print(
                f"{table_name}: "
                f"{count} registros"
            )


def main():
    print(
        "\n=== RETAILPULSE RAW LOAD ==="
    )

    engine = get_engine()

    clear_raw_tables(engine)

    print(
        "\nCarregando arquivos CSV..."
    )

    for table_name in TABLES:
        load_table(
            engine,
            table_name,
        )

    validate_load(engine)

    print(
        "\nRAW LOAD STATUS: COMPLETED ✅"
    )


if __name__ == "__main__":
    main()