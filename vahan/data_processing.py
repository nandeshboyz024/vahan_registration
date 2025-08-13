
from __future__ import annotations
import pandas as pd
import numpy as np

def ensure_month_start(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp()
    return df

def total_by_category(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["date","category"], as_index=False)["registrations"].sum()
    return g

def total_by_manufacturer(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["date","manufacturer","category"], as_index=False)["registrations"].sum()
    return g

def add_growth_rates(ts: pd.DataFrame, value_col: str = "registrations") -> pd.DataFrame:
    ts = ts.sort_values("date").copy()
    ts["quarter"] = ts["date"].dt.to_period("Q")

    # Year-over-Year change (12 months back)
    ts["yoy_pct"] = ts.groupby(get_group_cols(ts))[value_col].transform(
        lambda x: x.pct_change(12)
    )

    # Quarter-over-Quarter change
    qsum = ts.groupby(get_group_cols(ts) + ["quarter"])[value_col].transform("sum")
    ts["qoq_pct"] = ts.groupby(get_group_cols(ts))["quarter"].transform(
        lambda q: q.map(qsum.groupby(q).first().pct_change())
    )

    return ts

# def add_growth_rates(ts: pd.DataFrame, value_col: str = "registrations") -> pd.DataFrame:
#     """
#     Adds YoY and QoQ percentage change for each group (if grouped).
#     Expects a time series at monthly frequency per group key(s).
#     """
#     ts = ts.sort_values("date").copy()

#     # Compute quarter index
#     ts["quarter"] = ts["date"].dt.to_period("Q")
#     # QoQ: compare current sum of quarter vs previous quarter within group
#     def _qoq(x):
#         qsum = x.groupby("quarter")[value_col].sum().rename("qsum")
#         qgrowth = qsum.pct_change().rename("qoq_pct")
#         x = x.merge(qsum.reset_index(), on="quarter", how="left")
#         x = x.merge(qgrowth.reset_index(), on="quarter", how="left")
#         return x

#     # YoY: compare same month vs 12 months ago within group
#     ts["yoy_pct"] = ts.groupby(get_group_cols(ts)).apply(
#         lambda g: g[value_col].pct_change(12)
#     ).reset_index(level=get_group_cols(ts), drop=True)

#     ts = ts.groupby(get_group_cols(ts), group_keys=False).apply(_qoq)

#     return ts

def get_group_cols(df: pd.DataFrame):
    return [c for c in ["category","manufacturer"] if c in df.columns and c != "date"]

def filter_df(df: pd.DataFrame, start_date=None, end_date=None, categories=None, manufacturers=None):
    dff = df.copy()
    if start_date:
        dff = dff[dff["date"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["date"] <= pd.to_datetime(end_date)]
    if categories:
        dff = dff[dff["category"].isin(categories)]
    if manufacturers:
        dff = dff[dff["manufacturer"].isin(manufacturers)]
    return dff

def latest_quarter(df: pd.DataFrame):
    q = pd.to_datetime(df["date"]).dt.to_period("Q")
    return q.max()

def summarize_latest(df_cat: pd.DataFrame, df_maker: pd.DataFrame):
    # latest month totals and growth
    latest_date = df_cat["date"].max()
    latest = df_cat[df_cat["date"] == latest_date].copy()
    return latest_date, latest.sort_values("registrations", ascending=False)

