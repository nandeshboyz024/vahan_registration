import streamlit as st
import pandas as pd
from vahan.data_ingestion import get_data
from vahan.data_processing import (
    ensure_month_start, total_by_category, total_by_manufacturer,
    add_growth_rates, filter_df, summarize_latest
)

st.set_page_config(page_title="Vahan Registration Trends", layout="wide")

st.title("Vahan Registration Trends – Investor View")

with st.sidebar:
    st.header("Data Source")
    source = st.radio("Choose source", ["local (demo)", "selenium (live)"], index=0)
    st.caption("Live scraping requires solving a CAPTCHA in a browser window.")

    st.header("Filters")
    date_range = st.date_input(
        "Date range",
        value=(pd.to_datetime("2023-01-01"), pd.to_datetime("today")),
        min_value=pd.to_datetime("2015-01-01"),
        max_value=pd.to_datetime("today")
    )
    cats = st.multiselect("Vehicle Category", ["2W", "3W", "4W"], default=["2W", "3W", "4W"])

    # We'll populate this after loading the data
    manu_filter = []

st.info(
    "This tool showcases YoY & QoQ growth for vehicle categories and manufacturers using public Vahan data. "
    "If live scraping is unavailable, a sample dataset is used for demo."
)

# Load data
if source.startswith("local"):
    df = get_data("local", csv_path="data/sample_registrations.csv")
else:
    df = get_data("selenium", csv_path="data/sample_registrations.csv", headless=False)

df = ensure_month_start(df)

# Populate manufacturer filter options AFTER loading data
with st.sidebar:
    available_makers = sorted(df["manufacturer"].dropna().unique())
    manu_filter = st.multiselect(
        "Select Manufacturers",
        options=available_makers,
        default=[]
    )

start_date, end_date = date_range

df_f = filter_df(df, start_date, end_date, cats or None, manu_filter or None)

# Aggregations
cat_ts = total_by_category(df_f)
cat_ts = add_growth_rates(cat_ts, value_col="registrations")

maker_ts = total_by_manufacturer(df_f)
maker_ts = add_growth_rates(maker_ts, value_col="registrations")

tab1, tab2, tab3 = st.tabs(["Overview", "By Category", "By Manufacturer"])

with tab1:
    st.subheader("Headline Snapshot")
    latest_date, latest = summarize_latest(cat_ts, maker_ts)
    cols = st.columns(3)
    for i, cat in enumerate(["2W", "3W", "4W"]):
        sub = cat_ts[cat_ts["category"] == cat].sort_values("date")
        if sub.empty:
            continue
        latest_row = sub[sub["date"] == sub["date"].max()].tail(1)
        yoy = latest_row["yoy_pct"].iloc[0]
        qoq = latest_row["qoq_pct"].iloc[0]
        with cols[i]:
            st.metric(
                label=f"{cat} – Latest ({latest_date.strftime('%b %Y')})",
                value=int(latest_row["registrations"].iloc[0]),
                delta=f"YoY {yoy:.1%}" if pd.notna(yoy) else "YoY n/a"
            )
            st.caption(f"QoQ change: {qoq:.1%}" if pd.notna(qoq) else "QoQ n/a")

    st.markdown("---")
    st.subheader("Trend – Total Registrations (by Category)")
    st.line_chart(cat_ts.pivot(index="date", columns="category", values="registrations"))

with tab2:
    st.subheader("Category Trends & Growth")
    for cat in ["2W", "3W", "4W"]:
        st.markdown(f"### {cat}")
        sub = cat_ts[cat_ts["category"] == cat].sort_values("date")
        if sub.empty:
            st.warning("No data for selection.")
            continue
        st.bar_chart(sub.set_index("date")["registrations"])
        sub_disp = sub[["date", "registrations", "yoy_pct", "qoq_pct"]].copy()
        sub_disp.columns = ["Date", "Registrations", "YoY %", "QoQ %"]
        st.dataframe(sub_disp.tail(12).reset_index(drop=True))

with tab3:
    st.subheader("Manufacturer Trends & Growth")
    show = maker_ts[maker_ts["manufacturer"].isin(manu_filter)].copy()
    st.line_chart(show.pivot(index="date", columns="manufacturer", values="registrations"))

    latest = show.groupby(["manufacturer"]).apply(
        lambda g: g[g["date"] == g["date"].max()].tail(1)
    ).reset_index(drop=True)
    latest = latest[["manufacturer", "category", "date", "registrations", "yoy_pct", "qoq_pct"]]
    latest = latest.sort_values("registrations", ascending=False)
    st.dataframe(latest.reset_index(drop=True))

st.caption(
    "Note: For live data, pass through the CAPTCHA once and the app will attempt to read the on-page charts. "
    "All figures represent registrations captured in Vahan; coverage can vary by state/RTO."
)