import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/instacart_data.csv")
    return df

df = load_data()

st.set_page_config(page_title="Instacart Dashboard", layout="wide")

st.title("Instacart Sales Dashboard")
st.markdown("EDA and Insights from Instacart Dataset")

# ------------------------
# Orders by Day of Week
# ------------------------
if "Day" in df.columns:
    dow_counts = df.groupby("Day").size().reset_index(name="count")
    fig_dow = px.bar(
        dow_counts, x="Day", y="count",
        title="Orders by Day of Week",
        labels={"Day": "Day of Week", "count": "Number of Orders"}
    )
    # Fix width: set a number instead of 'stretch'
    fig_dow.update_layout(width=800)
    st.plotly_chart(fig_dow, use_container_width=True)

# ------------------------
# Orders by Hour
# ------------------------
if "Hour" in df.columns:
    hour_counts = df.groupby("Hour").size().reset_index(name="count")
    fig_hour = px.bar(
        hour_counts, x="Hour", y="count",
        title="Orders by Hour",
        labels={"Hour": "Hour of Day", "count": "Number of Orders"}
    )
    fig_hour.update_layout(width=800)
    st.plotly_chart(fig_hour, use_container_width=True)

# ------------------------
# Top Products
# ------------------------
if "Product" in df.columns:
    top_products = df["Product"].value_counts().nlargest(10).reset_index()
    top_products.columns = ["Product", "count"]
    fig_top_products = px.bar(
        top_products, x="Product", y="count",
        title="Top 10 Products Ordered",
        labels={"Product": "Product", "count": "Number of Orders"}
    )
    fig_top_products.update_layout(width=800)
    st.plotly_chart(fig_top_products, use_container_width=True)

# ------------------------
# Reorder Rate
# ------------------------
if "Reordered" in df.columns:
    reorder_rate = df["Reordered"].mean()
    st.metric(label="Overall Reorder Rate", value=f"{reorder_rate:.2%}")

# ------------------------
# New Chart: Orders by Department
# ------------------------
if "Department" in df.columns:
    dept_counts = df.groupby("Department").size().reset_index(name="count")
    fig_dept = px.bar(
        dept_counts, x="Department", y="count",
        title="Orders by Department",
        labels={"Department": "Department", "count": "Number of Orders"}
    )
    fig_dept.update_layout(width=800)
    st.plotly_chart(fig_dept, use_container_width=True)

# ------------------------
# New Chart: Reorder Rate by Product
# ------------------------
if "Product" in df.columns and "Reordered" in df.columns:
    reorder_by_product = df.groupby("Product")["Reordered"].mean().reset_index()
    top_reorder = reorder_by_product.nlargest(10, "Reordered")
    fig_reorder_product = px.bar(
        top_reorder, x="Product", y="Reordered",
        title="Top 10 Products by Reorder Rate",
        labels={"Product": "Product", "Reordered": "Reorder Rate"}
    )
    fig_reorder_product.update_layout(width=800)
    st.plotly_chart(fig_reorder_product, use_container_width=True)
