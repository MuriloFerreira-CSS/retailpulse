from pathlib import Path
import os

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine


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


@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)


@st.cache_data(ttl=300)
def load_view(view_name: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(f"SELECT * FROM analytics.{view_name}", engine)


st.set_page_config(
    page_title="RetailPulse Analytics",
    layout="wide",
)

st.title("RetailPulse — E-commerce Analytics")

try:
    overview = load_view("vw_executive_overview").iloc[0]
except Exception as exc:
    st.error(
        "Não foi possível conectar ao banco de dados. "
        "Verifique se o Postgres está rodando e se o .env está configurado."
    )
    st.exception(exc)
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Sessões", f"{int(overview['sessions']):,}")
col2.metric("Clientes", f"{int(overview['customers']):,}")
col3.metric("Pedidos", f"{int(overview['orders']):,}")
col4.metric("Receita", f"R$ {overview['revenue']:,.2f}")
col5.metric("Taxa de Conversão", f"{overview['conversion_rate']}%")

st.divider()

funnel_col, channel_col = st.columns(2)

with funnel_col:
    st.subheader("Funil de Conversão")

    funnel = load_view("vw_funnel").iloc[0]

    stages = [
        "Page View",
        "Product View",
        "Add to Cart",
        "Checkout",
        "Purchase",
    ]

    funnel_df = pd.DataFrame(
        {
            "stage": stages,
            "sessions": [
                funnel["page_view_sessions"],
                funnel["product_view_sessions"],
                funnel["add_to_cart_sessions"],
                funnel["checkout_sessions"],
                funnel["purchase_sessions"],
            ],
        }
    )

    chart = (
        alt.Chart(funnel_df)
        .mark_bar()
        .encode(
            x=alt.X("stage", sort=stages, title=None),
            y=alt.Y("sessions", title="Sessões"),
        )
    )

    st.altair_chart(chart, use_container_width=True)

with channel_col:
    st.subheader("Performance por Canal")

    channel_df = load_view("vw_channel_performance").sort_values(
        "revenue", ascending=False
    )

    channel_chart = (
        alt.Chart(channel_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "traffic_source",
                sort=channel_df["traffic_source"].tolist(),
                title=None,
            ),
            y=alt.Y("revenue", title="Receita (R$)"),
        )
    )

    st.altair_chart(channel_chart, use_container_width=True)

    st.dataframe(
        channel_df,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

search_col, product_col = st.columns(2)

with search_col:
    st.subheader("Termos Mais Buscados")

    search_df = load_view("vw_search_performance").sort_values(
        "searches", ascending=False
    )

    st.dataframe(
        search_df.head(15),
        use_container_width=True,
        hide_index=True,
    )

with product_col:
    st.subheader("Top Produtos por Receita")

    product_df = load_view("vw_product_performance").sort_values(
        "revenue", ascending=False
    )

    st.dataframe(
        product_df.head(15)[
            [
                "product_name",
                "category",
                "brand",
                "product_views",
                "add_to_carts",
                "purchases",
                "product_conversion_rate",
                "revenue",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
