import pandas as pd
import numpy as np
import streamlit as st 
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(page_title="Instacart Sales Dashboard", layout="wide")
st.title("🛒 Instacart Dataset Dashboard")

# -------------------------------
# Load data safely
# -------------------------------
@st.cache_data
def load_data(files):
    dfs = [pd.read_csv(f) for f in files]
    df = pd.concat(dfs, ignore_index=True)
    return df

data_folder = "data"

if not os.path.exists(data_folder):
    st.error(f"Data folder '{data_folder}' not found! Make sure it exists in the repo.")
    st.stop()

csv_files = [os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith(".csv")]

if len(csv_files) == 0:
    st.error(f"No CSV files found in '{data_folder}' folder!")
    st.stop()

# Show spinner while loading
with st.spinner("Loading data..."):
    df = load_data(csv_files)

# -------------------------------
# Key Metrics
# -------------------------------
st.header("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", f"{df['order_id'].nunique():,}")
col2.metric("Total Users", f"{df['user_id'].nunique():,}")

col3.metric("Unique Products", f"{df['product_name'].nunique():,}")

avg_products = df.groupby("order_id")["product_name"].count().mean()
col4.metric("Avg Products per Order", f"{avg_products:.2f}")

st.markdown("---")

# -------------------------------
# Filters
# -------------------------------
st.sidebar.header("🔍 Filters")

departments = st.sidebar.multiselect(
    "Select Department(s):",
    options=df["department"].dropna().unique(),
    default=[]
)
if departments:
    df = df[df["department"].isin(departments)]
    
aisle = st.sidebar.multiselect(
    "Select Aisle(s):",
    options=df["aisle"].dropna().unique(),
    default=[]
)
if aisle:
    df = df[df["aisle"].isin(aisle)]
    
product_name = st.sidebar.multiselect(
    "Select Product(s):",
    options=df["product_name"].dropna().unique(),
    default=[]
)
if product_name:
    df = df[df["product_name"].isin(product_name)]

st.sidebar.markdown("Created by Bright Tavonga Bunhu")

# -------------------------------
# Order Patterns
# -------------------------------
st.header("🕒 Order Patterns")

col1, col2 = st.columns(2)

# Orders by Day
if "Day" in df.columns:
    dow_counts = df.groupby("Day").size().reset_index(name="count")
    fig_dow = px.bar(
        dow_counts, x="Day", y="count",
        title="Orders by Day of Week",
        labels={"Day": "Day of Week", "count": "Number of Orders"},
        width='stretch'
    )
    col1.plotly_chart(fig_dow, use_container_width=True)

# Orders by Hour Bin
if "order_hour_bins" in df.columns:
    hour_counts = df.groupby("order_hour_bins").size().reset_index(name="count")
    fig_hour = px.line(
        hour_counts, x="order_hour_bins", y="count",
        title="Orders by Hour of Day",
        labels={"order_hour_bins": "Hour of Day", "count": "Number of Orders"},
        width='stretch'
    )
    col2.plotly_chart(fig_hour, use_container_width=True)

st.markdown("---")

# Orders by Hour of Day
if "order_hour_of_day" in df.columns:
    hour_counts2 = df.groupby("order_hour_of_day").size().reset_index(name="count")
    fig_hour2 = px.line(
        hour_counts2, x="order_hour_of_day", y="count",
        title="Orders by Hour of Day",
        labels={"order_hour_of_day": "Hour of Day", "count": "Number of Orders"},
        width='stretch'
    )
    st.plotly_chart(fig_hour2, use_container_width=True)

st.markdown("---")

# -------------------------------
# Product & Department Insights
# -------------------------------
st.header("🏬 Product & Department Insights")

col1, col2 = st.columns(2)

# Top 10 Products
top_products = df["product_name"].value_counts().head(10).reset_index()
top_products.columns = ["Product Name", "Count"]
fig_top = px.bar(
    top_products, x="Count", y="Product Name",
    orientation="h", title="Top 10 Ordered Products",
    width='stretch'
)
col1.plotly_chart(fig_top, use_container_width=True)

# Orders by Department
dept_counts = df["department"].value_counts().reset_index()
dept_counts.columns = ["Department", "Count"]
fig_dept = px.pie(
    dept_counts, names="Department", values="Count",
    title="Orders by Department",
    width='stretch'
)
col2.plotly_chart(fig_dept, use_container_width=True)

st.markdown("---")

# -------------------------------
# Reordering Behavior
# -------------------------------
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
        labels={"department": "Department", "reordered": "Reorder Rate"},
        width='stretch'
    )
    st.plotly_chart(fig_reorder, use_container_width=True)

st.markdown("---")

# -------------------------------
# User Behavior Insights
# -------------------------------
st.header("👥 User Behavior Insights")

avg_order_per_customer = df['order_id'].nunique() / df['user_id'].nunique()
st.metric("Avg Order Per Customer", f"{avg_order_per_customer:.2f}")

# Orders Table
table_data = df[['user_id', 'order_id', 'add_to_cart_order', 'reordered', 'order_number','days_since_prior_order','product_name', 'Day', 'order_hour']].astype(str)
table_data = table_data.rename(columns={
    'user_id': 'User ID',
    'order_id': 'Order ID',
    'add_to_cart_order': 'Add to Cart Order',
    'reordered': 'Reordered',
    'order_number': 'Order Number',
    'days_since_prior_order': 'Days Since Prior Order',
    'product_name': 'Product Name',    
    'Day': 'Day',
    'order_hour': 'Order Hour',
})

st.title('Orders Table')

num_rows = st.selectbox('Number of Rows', [10, 50, 100, 500, 1000, len(table_data)])
display_from = st.selectbox('Display From', ['Top', 'Bottom'])

if display_from == 'Top':
    table_data_display = table_data.head(num_rows)
else:
    table_data_display = table_data.tail(num_rows)

fig_table = go.Figure(data=[go.Table(
    header=dict(values=list(table_data_display.columns), fill_color='#2f4f7f', align='left', font=dict(color='white')),
    cells=dict(values=[table_data_display[col] for col in table_data_display.columns], fill_color='black', align='left', font=dict(color='white'))
)])
fig_table.update_layout(title='Orders Table', paper_bgcolor='black')
st.plotly_chart(fig_table, use_container_width=True)

st.markdown("---")

# -------------------------------
# Footer / Info
# -------------------------------
col1, col2 = st.columns(2)
col1.metric("Creator", "Bright Tavonga Bunhu")
col2.metric("Level", "3.2 Student")

st.markdown("---")
col1, col2 = st.columns(2)
col1.metric("University", "Midlands State University")
col2.metric("Location", "Zimbabwe")

st.markdown("---")
col1, col2 = st.columns(2)
col1.markdown("Portfolio: [brighttavongabunhu.vercel.app](https://brighttavongabunhu.vercel.app)")
col2.markdown("GitHub: [github.com/brightbunhu](https://github.com/brightbunhu)")

st.markdown("")
col1, col2 = st.columns(2)
col1.markdown("Email: brightbunhu4@gmail.com")
col2.markdown("Phone: 0783234270")

st.markdown("---")
