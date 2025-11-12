import pandas as pd
import numpy as np
import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Instacart Sales Dashboard", layout="wide")
st.title("🛒 Instacart Dataset Dashboard")

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    data_folder = "data"
    
    if os.path.exists(data_folder):
        files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
        if not files:
            st.error(f"No CSV files found in '{data_folder}'.")
            st.stop()
        dfs = []
        progress_bar = st.progress(0)
        for i, f in enumerate(files):
            dfs.append(pd.read_csv(os.path.join(data_folder, f)))
            progress_bar.progress((i + 1) / len(files))
        df = pd.concat(dfs, ignore_index=True)
        progress_bar.empty()
        return df
    else:
        st.error(f"Data folder '{data_folder}' not found! Please upload it to your repo.")
        st.stop()

with st.spinner("Loading data..."):
    df = load_data()

# -----------------------------
# Key Metrics
# -----------------------------
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", f"{df['order_id'].nunique():,}")
col2.metric("Total Users", f"{df['user_id'].nunique():,}")
col3.metric("Unique Products", f"{df['product_name'].nunique():,}")

avg_products = df.groupby("order_id")["product_name"].count().mean()
col4.metric("Avg Products per Order", f"{avg_products:.2f}")

st.markdown("---")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

departments = st.sidebar.multiselect(
    "Select Department(s):",
    options=df["department"].dropna().unique()
)
if departments:
    df = df[df["department"].isin(departments)]

aisles = st.sidebar.multiselect(
    "Select Aisle(s):",
    options=df["aisle"].dropna().unique()
)
if aisles:
    df = df[df["aisle"].isin(aisles)]

products = st.sidebar.multiselect(
    "Select Product(s):",
    options=df["product_name"].dropna().unique()
)
if products:
    df = df[df["product_name"].isin(products)]

st.sidebar.markdown("Created by Bright Tavonga Bunhu")

# -----------------------------
# Order Patterns
# -----------------------------
st.header("🕒 Order Patterns")
col1, col2 = st.columns(2)

# Orders by day of week
if "Day" in df.columns:
    dow_counts = df.groupby("Day").size().reset_index(name="count")
    fig_dow = px.bar(
        dow_counts, x="Day", y="count",
        title="Orders by Day of Week",
        labels={"Day": "Day of Week", "count": "Number of Orders"}
    )
    col1.plotly_chart(fig_dow, use_container_width=True)

# Orders by hour of day
if "order_hour_of_day" in df.columns:
    hour_counts = df.groupby("order_hour_of_day").size().reset_index(name="count")
    fig_hour = px.line(
        hour_counts, x="order_hour_of_day", y="count",
        title="Orders by Hour of Day",
        labels={"order_hour_of_day": "Hour of Day", "count": "Number of Orders"}
    )
    col2.plotly_chart(fig_hour, use_container_width=True)

st.markdown("---")

# -----------------------------
# Product & Department Insights
# -----------------------------
st.header("🏬 Product & Department Insights")
col1, col2 = st.columns(2)

# Top 10 products
top_products = df["product_name"].value_counts().head(10).reset_index()
top_products.columns = ["Product Name", "Count"]
fig_top = px.bar(
    top_products, x="Count", y="Product Name",
    orientation="h", title="Top 10 Ordered Products"
)
col1.plotly_chart(fig_top, use_container_width=True)

# Orders by department
dept_counts = df["department"].value_counts().reset_index()
dept_counts.columns = ["Department", "Count"]
fig_dept = px.pie(
    dept_counts, names="Department", values="Count",
    title="Orders by Department"
)
col2.plotly_chart(fig_dept, use_container_width=True)

st.markdown("---")

# -----------------------------
# Reorder Analysis
# -----------------------------
st.header("🔁 Reordering Behavior")

if "reordered" in df.columns:
    reorder_rate = df["reordered"].mean() * 100
    st.metric("Overall Reorder Rate", f"{reorder_rate:.2f}%")

    reorder_by_dept = df.groupby("department")["reordered"].mean().reset_index()
    reorder_by_dept = reorder_by_dept.sort_values("reordered", ascending=False)
    fig_reorder = px.bar(
        reorder_by_dept,
        x="department", y="reordered",
        title="Reorder Rate by Department",
        labels={"department": "Department", "reordered": "Reorder Rate"}
    )
    st.plotly_chart(fig_reorder, use_container_width=True)

    # -----------------------------
    # Top Reordered Products
    # -----------------------------
    top_reordered = df[df["reordered"] == 1]["product_name"].value_counts().head(10).reset_index()
    top_reordered.columns = ["Product Name", "Reorder Count"]
    fig_top_reordered = px.bar(
        top_reordered, x="Reorder Count", y="Product Name",
        orientation="h", title="Top 10 Reordered Products"
    )
    st.plotly_chart(fig_top_reordered, use_container_width=True)

st.markdown("---")

# -----------------------------
# User Behavior Insights
# -----------------------------
st.header("👥 User Behavior Insights")

avg_order_per_customer = df['order_id'].nunique() / df['user_id'].nunique()
st.metric("Avg Orders Per Customer", f"{avg_order_per_customer:.2f}")

# Busiest Users
top_users = df["user_id"].value_counts().head(10).reset_index()
top_users.columns = ["User ID", "Orders"]
fig_top_users = px.bar(
    top_users, x="Orders", y="User ID",
    orientation="h", title="Top 10 Busiest Users"
)
st.plotly_chart(fig_top_users, use_container_width=True)

# Order Heatmap (Day vs Hour)
if "Day" in df.columns and "order_hour_of_day" in df.columns:
    heatmap_data = df.groupby(["Day", "order_hour_of_day"]).size().reset_index(name="count")
    heatmap_pivot = heatmap_data.pivot(index="Day", columns="order_hour_of_day", values="count").fillna(0)
    fig_heatmap = px.imshow(
        heatmap_pivot, text_auto=True,
        labels=dict(x="Hour of Day", y="Day", color="Number of Orders"),
        title="Order Heatmap by Day & Hour"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Orders table
table_cols = [
    'user_id', 'order_id', 'add_to_cart_order', 'reordered', 'order_number',
    'days_since_prior_order', 'product_name', 'Day', 'order_hour_of_day'
]
table_data = df[table_cols].astype(str)
table_data = table_data.rename(columns={
    'user_id': 'User ID',
    'order_id': 'Order ID',
    'add_to_cart_order': 'Add to Cart Order',
    'reordered': 'Reordered',
    'order_number': 'Order Number',
    'days_since_prior_order': 'Days Since Prior Order',
    'product_name': 'Product Name',
    'Day': 'Day',
    'order_hour_of_day': 'Order Hour',
})

st.title('Orders Table')
num_rows = st.selectbox('Number of Rows', [10, 50, 100, 500, 1000, len(table_data)])
display_from = st.selectbox('Display From', ['Top', 'Bottom'])

table_data_display = table_data.head(num_rows) if display_from == 'Top' else table_data.tail(num_rows)

fig_table = go.Figure(data=[go.Table(
    header=dict(values=list(table_data_display.columns),
                fill_color='#2f4f7f', align='left', font=dict(color='white')),
    cells=dict(values=[table_data_display[col] for col in table_data_display.columns],
               fill_color='black', align='left', font=dict(color='white'))
)])
fig_table.update_layout(title='Orders Table', paper_bgcolor='black')
st.plotly_chart(fig_table, use_container_width=True)

st.markdown("---")

# -----------------------------
# Footer / Creator Info
# -----------------------------
col1, col2 = st.columns(2)
col1.metric("Creator", "Bright Tavonga Bunhu")
col2.metric("Level", "3.2 Student")

col1, col2 = st.columns(2)
col1.metric("University", "Midlands State University")
col2.metric("Location", "Zimbabwe")

col1, col2 = st.columns(2)
col1.markdown("Portfolio: [brighttavongabunhu.vercel.app](https://brighttavongabunhu.vercel.app)")
col2.markdown("GitHub: [github.com/brightbunhu](https://github.com/brightbunhu)")

col1, col2 = st.columns(2)
col1.markdown("Email: brightbunhu4@gmail.com")
col2.markdown("Phone: 0783234270")
