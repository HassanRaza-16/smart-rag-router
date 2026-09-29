import sqlite3

import pandas as pd
import streamlit as st

from app.core.config import get_settings


settings = get_settings()

st.set_page_config(
    page_title="SmartRAG Dashboard",
    layout="wide",
)

st.title("SmartRAG Router")
st.caption(
    "Semantic caching + cost-aware model routing"
)


connection = sqlite3.connect(
    settings.database_path
)

df = pd.read_sql_query(
    """
    SELECT *
    FROM requests
    ORDER BY id DESC
    """,
    connection,
)

connection.close()


if df.empty:

    st.info(
        "No requests yet. "
        "Call POST /query first."
    )

    st.stop()


total = len(df)

cache_hits = int(
    df["cache_hit"].sum()
)

cache_rate = (
    cache_hits / total
) * 100

average_latency = (
    df["latency_ms"].mean()
)

p95_latency = (
    df["latency_ms"].quantile(0.95)
)

total_cost = (
    df["estimated_cost"].sum()
)


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Requests",
    total,
)

col2.metric(
    "Cache Hit Rate",
    f"{cache_rate:.1f}%",
)

col3.metric(
    "Avg Latency",
    f"{average_latency:.0f} ms",
)

col4.metric(
    "P95 Latency",
    f"{p95_latency:.0f} ms",
)


st.divider()


col1, col2 = st.columns(2)


with col1:

    st.subheader("Model Usage")

    st.bar_chart(
        df["model"].value_counts()
    )


with col2:

    st.subheader("Latency")

    st.line_chart(
        df["latency_ms"]
    )


st.metric(
    "Estimated Cost",
    f"${total_cost:.4f}",
)


st.subheader("Request Logs")

st.dataframe(
    df,
    width="stretch",
)