import io
import pandas as pd
import streamlit as st
from pathlib import Path
st.set_page_config(page_title="Elite Elixir | Sales",layout="wide")
st.title("Elite Elixir | Sales Dashboard")
st.caption("Analyze sales across channels with CSV inputs.")
up=st.file_uploader("Upload sales CSV",type="csv")
try:
    df=pd.read_csv(up if up else Path(__file__).with_name("sample_sales.csv"))
    required={"date","order_id","channel","product","quantity","unit_price","discount"}
    if not required.issubset(df.columns):
        st.error("Missing columns: "+", ".join(sorted(required-set(df.columns))));st.stop()
    df["date"]=pd.to_datetime(df["date"],errors="coerce")
    for c in ["quantity","unit_price","discount"]:df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
    df=df.dropna(subset=["date"])
    df["revenue"]=(df.quantity*df.unit_price-df.discount).clip(lower=0)
    channels=st.multiselect("Channels",sorted(df.channel.dropna().unique()),default=sorted(df.channel.dropna().unique()))
    df=df[df.channel.isin(channels)]
    a,b,c=st.columns(3)
    orders=df.order_id.nunique()
    a.metric("Revenue",f"₹{df.revenue.sum():,.0f}")
    b.metric("Orders",f"{orders:,}")
    c.metric("Average order value",f"₹{df.revenue.sum()/orders:,.0f}" if orders else "₹0")
    st.subheader("Daily revenue")
    st.line_chart(df.groupby(df.date.dt.date).revenue.sum())
    st.subheader("Revenue by channel")
    st.bar_chart(df.groupby("channel").revenue.sum())
    st.subheader("Product summary")
    st.dataframe(df.groupby("product",as_index=False).agg(revenue=("revenue","sum"),units=("quantity","sum")),use_container_width=True)
    st.download_button("Download filtered sales",df.to_csv(index=False).encode(),"filtered_sales.csv","text/csv")
except Exception as e:st.error(f"Could not read CSV: {e}")
