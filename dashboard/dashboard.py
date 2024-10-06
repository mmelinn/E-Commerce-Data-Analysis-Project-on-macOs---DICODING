import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from func import DataAnalyzer, BrazilMapPlotter

PRIMARY_COLOR = "#F47C20"
SECONDARY_COLOR = "#2C3E50"
TERTIARY_COLOR = "#24426D"

sns.set(style='darkgrid', palette=[PRIMARY_COLOR, SECONDARY_COLOR, TERTIARY_COLOR])

datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", 
                    "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]

order_data = pd.read_csv("https://raw.githubusercontent.com/mmelinn/E-Commerce-Data-Analysis-Project-on-macOs---DICODING/refs/heads/main/dashboard/df.csv")
order_data.sort_values(by="order_approved_at", inplace=True)
order_data.reset_index(drop=True, inplace=True)

geo_data = pd.read_csv('https://raw.githubusercontent.com/mmelinn/E-Commerce-Data-Analysis-Project-on-macOs---DICODING/refs/heads/main/dashboard/geolocation.csv')
unique_customers = geo_data.drop_duplicates(subset='customer_unique_id')

for column in datetime_columns:
    order_data[column] = pd.to_datetime(order_data[column])

min_time = order_data["order_approved_at"].min()
max_time = order_data["order_approved_at"].max()

st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f4f4f4;
        padding: 20px;
    }
    .css-1d391kg {
        color: #ff6b00;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.write(' ')
    with col2:
        st.image("https://raw.githubusercontent.com/mmelinn/E-Commerce-Data-Analysis-Project-on-macOs---DICODING/refs/heads/main/dashboard/logoDICODINGShop.png", width=200)
    with col3:
        st.write(' ')

    selected_start_date, selected_end_date = st.date_input(
        label="Select Date Range",
        value=[min_time, max_time],
        min_value=min_time,
        max_value=max_time
    )

st.sidebar.markdown("<p style='text-align:center;color:#30475E;'> <br> <br> <br>DICODING Shop - 2024</p>", unsafe_allow_html=True)

filtered_data = order_data[(order_data["order_approved_at"] >= str(selected_start_date)) & 
                           (order_data["order_approved_at"] <= str(selected_end_date))]

data_analyzer = DataAnalyzer(filtered_data)
map_visualizer = BrazilMapPlotter(unique_customers, plt, mpimg, urllib, st)

daily_orders = data_analyzer.create_daily_orders_df()
customer_spending = data_analyzer.create_sum_spend_df()
item_sales = data_analyzer.create_sum_order_items_df()
review_scores, common_reviews = data_analyzer.review_score_df()
customer_states, frequent_state = data_analyzer.create_bystate_df()
order_status_data, common_order_status = data_analyzer.create_order_status()

def apply_plot_style(ax, title, xlabel=None, ylabel=None):
    ax.set_title(title, fontsize=22, color=SECONDARY_COLOR, weight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=18, color=SECONDARY_COLOR, labelpad=15)
    ax.set_ylabel(ylabel, fontsize=18, color=SECONDARY_COLOR, labelpad=15)
    ax.tick_params(axis='both', which='major', labelsize=14, colors=SECONDARY_COLOR)
    ax.grid(True, linestyle='--', alpha=0.6, color=TERTIARY_COLOR)
    sns.despine()

def format_to_idr(value):
    return f"{value:.0f}".replace(',', '.')

st.title("DICODING-Shop Data Analysis")

st.markdown(f"<h2 style='text-align: center; color:{TERTIARY_COLOR};'>Daily Orders Delivered</h2>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    total_orders = daily_orders["order_count"].sum()
    st.markdown(f"<h4 style='text-align: center;'>Total Orders: {total_orders}</h4>", unsafe_allow_html=True)

with col_b:
    total_revenue = daily_orders["revenue"].sum()
    st.markdown(f"<h4 style='text-align: center;'>Total Revenue: {format_to_idr(total_revenue)}</h4>", unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=daily_orders["order_approved_at"],
    y=daily_orders["order_count"],
    marker="o",
    linewidth=2,
    color=PRIMARY_COLOR,
    ax=ax
)
apply_plot_style(ax, "Daily Orders Delivered", "Date", "Order Count")
st.pyplot(fig)

st.markdown(f"<h2 style='text-align: center; color:{TERTIARY_COLOR};'>Customer Spend Overview</h2>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    total_spending = customer_spending["total_spend"].sum()
    st.markdown(f"<h4 style='text-align: center;'>Total Spending: {format_to_idr(total_spending)}</h4>", unsafe_allow_html=True)

with col_b:
    average_spending = customer_spending["total_spend"].mean()
    st.markdown(f"<h4 style='text-align: center;'>Average Spending: {format_to_idr(average_spending)}</h4>", unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=customer_spending,
    x="order_approved_at",
    y="total_spend",
    marker="o",
    linewidth=2,
    color=PRIMARY_COLOR,
    ax=ax
)
apply_plot_style(ax, "Customer Spending Over Time", "Date", "Total Spend")
st.pyplot(fig)

st.markdown(f"<h2 style='text-align: center; color:{TERTIARY_COLOR};'>Product Orders</h2>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    total_products = item_sales["product_count"].sum()
    st.markdown(f"<h4 style='text-align: center;'>Total Products Sold: {total_products}</h4>", unsafe_allow_html=True)

with col_b:
    average_products = item_sales["product_count"].mean()
    st.markdown(f"<h4 style='text-align: center;'>Average Products Sold: {average_products:.2f}</h4>", unsafe_allow_html=True)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

sns.barplot(x="product_count", 
            y="product_category_name_english", 
            data=item_sales.head(5), 
            palette=[PRIMARY_COLOR], 
            ax=ax[0])
apply_plot_style(ax[0], "Top Sold Products", "Sales Count", None)

sns.barplot(x="product_count", 
            y="product_category_name_english", 
            data=item_sales.sort_values(by="product_count", ascending=True).head(5), 
            palette=[PRIMARY_COLOR], 
            ax=ax[1])
apply_plot_style(ax[1], "Least Sold Products", "Sales Count", None)
ax[1].invert_yaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()

st.pyplot(fig)

st.markdown(f"<h2 style='text-align: center; color:{TERTIARY_COLOR};'>Review Score Analysis</h2>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    average_review_score = review_scores.mean()
    st.markdown(f"<h4 style='text-align: center;'>Average Review Score: {average_review_score:.2f}</h4>", unsafe_allow_html=True)

with col_b:
    common_review_score = review_scores.value_counts().idxmax()
    st.markdown(f"<h4 style='text-align: center;'>Most Common Review Score: {common_review_score}</h4>", unsafe_allow_html=True)

fig, ax = plt.subplots(figsize=(12, 6))
color_palette = sns.color_palette([PRIMARY_COLOR, SECONDARY_COLOR, TERTIARY_COLOR], len(review_scores))

sns.barplot(x=review_scores.index,
            y=review_scores.values,
            order=review_scores.index,
            palette=color_palette,
            ax=ax)

apply_plot_style(ax, "Customer Review Scores", "Rating", "Count")
for i, v in enumerate(review_scores.values):
    ax.text(i, v + 5, str(v), ha='center', va='bottom', fontsize=12, color=SECONDARY_COLOR)

st.pyplot(fig)

st.markdown(f"<h2 style='text-align: center; color:{TERTIARY_COLOR};'>Customer Demographics</h2>", unsafe_allow_html=True)

tab_state, tab_geo = st.tabs(["State", "Geolocation"])

with tab_state:
    common_state = customer_states.customer_state.value_counts().index[0]
    st.markdown(f"<h4 style='text-align: center;'>Most Common State: {common_state}</h4>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=customer_states.customer_state.value_counts().index,
                y=customer_states.customer_count.values, 
                data=customer_states,
                palette=[PRIMARY_COLOR, SECONDARY_COLOR, TERTIARY_COLOR],
                ax=ax)

    apply_plot_style(ax, "Customer Distribution by State", "State", "Number of Customers")
    st.pyplot(fig)

with tab_geo:
    map_visualizer.plot()

    with st.expander("See Explanation"):
        st.write('According to the graph, there are more customers in the southeast and south regions, particularly in capital cities like São Paulo, Rio de Janeiro, and Porto Alegre.')

st.caption('© 2024 DICODING Shop - Melinda NS')
