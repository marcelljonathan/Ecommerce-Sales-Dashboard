import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide", # Uses full widht of the browser
    initial_sidebar_state="expanded" # Sidebar opened by default
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; color: #e8e8e8; } 
 
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a1d27; border-right: 1px solid #2e3047; }
 
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e2235 0%, #252a3d 100%);
        border: 1px solid #2e3047;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .kpi-label { font-size: 12px; color: #7c8db5; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #e8e8e8; }
    .kpi-delta { font-size: 13px; margin-top: 4px; }
    .kpi-delta.pos { color: #4ade80; }
    .kpi-delta.neg { color: #f87171; }
 
    /* Section headers */
    .section-header {
        font-size: 16px;
        font-weight: 600;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 24px 0 12px 0;
        border-left: 3px solid #6c63ff;
        padding-left: 10px;
    }
 
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['year_month'] = df['order_date'].dt.to_period('M').astype(str)
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['month_name'] = df['order_date'].dt.strftime('%b')
    return df
 
# ─── Replace this path with your actual CSV file path ───
DATA_PATH = "C:/Users/Support/Documents/Marcell/Learning/Sales Dashboard/E-Commerce Sales Data.csv"
 
try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"❌ File not found: `{DATA_PATH}`\n\nPlease update `DATA_PATH` in the script to your CSV file location.")
    st.stop()

# ─────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filters")
st.sidebar.markdown("---")

# Date range
min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()
start_date_input = st.sidebar.date_input(
    "Start Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)
end_date_input = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)
 
# Swap silently if user sets start after end
if start_date_input > end_date_input:
    start_date_input, end_date_input = end_date_input, start_date_input
 
# Region
all_regions = sorted(df['region'].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", all_regions, default=all_regions)
 
# Product category
all_cats = sorted(df['product_category'].dropna().unique().tolist())
selected_cats = st.sidebar.multiselect("Product Category", all_cats, default=all_cats)
 
# Payment method
all_payments = sorted(df['payment_method'].dropna().unique().tolist())
selected_payments = st.sidebar.multiselect("Payment Method", all_payments, default=all_payments)
 
# Returns filter
return_filter = st.sidebar.radio("Order Type", ["All Orders", "Non-returned Only", "Returned Only"])
 
# Discount filter
discount_range = st.sidebar.slider("Discount % Range", 0, int(df['discount_percent'].max()), (0, int(df['discount_percent'].max())))
 
st.sidebar.markdown("---")
st.sidebar.markdown("## 📋 View")
show_raw = st.sidebar.checkbox("Show Raw Dataset", value=False)

# ─────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────
start_date = pd.to_datetime(start_date_input)
end_date = pd.to_datetime(end_date_input)
 
filtered = df[
    (df['order_date'] >= start_date) &
    (df['order_date'] <= end_date) &
    (df['region'].isin(selected_regions)) &
    (df['product_category'].isin(selected_cats)) &
    (df['payment_method'].isin(selected_payments)) &
    (df['discount_percent'] >= discount_range[0]) &
    (df['discount_percent'] <= discount_range[1])
]
 
if return_filter == "Non-returned Only":
    filtered = filtered[filtered['is_returned'] == 0]
elif return_filter == "Returned Only":
    filtered = filtered[filtered['is_returned'] == 1]

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("# 🛒 E-Commerce Sales Dashboard")
st.markdown(f"Showing **{len(filtered):,}** orders · {start_date.strftime('%b %d, %Y')} → {end_date.strftime('%b %d, %Y')}")
st.markdown("---")
 
if filtered.empty:
    st.warning("No data matches your current filters. Try adjusting the sidebar.")
    st.stop()

# ─────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────
total_revenue = filtered['revenue'].sum()
avg_order_value = filtered['revenue'].mean()
total_orders = len(filtered)
avg_rating = filtered['customer_rating'].mean()
return_rate = filtered['is_returned'].mean() * 100
avg_delivery = filtered['delivery_days'].mean()
 
col1, col2, col3, col4, col5, col6 = st.columns(6)
 
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">${total_revenue:,.0f}</div>
    </div>""", unsafe_allow_html=True)
 
with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-value">{total_orders:,}</div>
    </div>""", unsafe_allow_html=True)
 
with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">${avg_order_value:,.2f}</div>
    </div>""", unsafe_allow_html=True)
 
with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Rating</div>
        <div class="kpi-value">{avg_rating:.2f} ⭐</div>
    </div>""", unsafe_allow_html=True)
 
with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Return Rate</div>
        <div class="kpi-value">{return_rate:.1f}%</div>
    </div>""", unsafe_allow_html=True)
 
with col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Delivery</div>
        <div class="kpi-value">{avg_delivery:.1f}d</div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CHART THEME
# ─────────────────────────────────────────
CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#a0aec0", "family": "Inter, sans-serif"},
    "xaxis": {"gridcolor": "#1e2235", "linecolor": "#2e3047"},
    "yaxis": {"gridcolor": "#1e2235", "linecolor": "#2e3047"},
}
COLOR_PALETTE = ["#6c63ff", "#4ecdc4", "#f7b731", "#ff6b6b", "#a29bfe", "#fd79a8", "#00b894", "#e17055"]
 
def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a0aec0", family="Inter, sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2e3047"),
        margin=dict(t=40, b=20, l=10, r=10),
    )
    fig.update_xaxes(gridcolor="#1e2235", linecolor="#2e3047", showgrid=True)
    fig.update_yaxes(gridcolor="#1e2235", linecolor="#2e3047", showgrid=True)
    return fig

# ─────────────────────────────────────────
# SECTION 1 — REVENUE OVER TIME
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Revenue Over Time</div>', unsafe_allow_html=True)
 
time_group = st.radio("Timeframe", ["Month", "Quarter", "Year"], horizontal=True, key="time_group")
 
if time_group == "Month":
    rev_time = filtered.groupby('year_month')['revenue'].sum().reset_index()
    rev_time.columns = ['period', 'revenue']
    rev_time["period_label"] = pd.to_datetime(rev_time["period"]).dt.strftime("%b %Y")
elif time_group == "Quarter":
    filtered['quarter'] = filtered['order_date'].dt.to_period('Q').astype(str)
    rev_time = filtered.groupby('quarter')['revenue'].sum().reset_index()
    rev_time.columns = ['period', 'revenue']
    rev_time["period_label"] = rev_time["period"].apply(lambda x: f"Q{x[-1]} {x[:4]}")
else:
    rev_time = filtered.groupby('year')['revenue'].sum().reset_index()
    rev_time.columns = ['period', 'revenue']
    rev_time["period_label"] = rev_time["period"].astype(str)

rev_time["revenue_label"] = rev_time["revenue"].apply(lambda x: f"${x/1_000_000:.2f}M" if x >= 1_000_000 else f"${x/1_000:.2f}K")

fig_time = px.area(
    rev_time, x='period', y='revenue',
    title="Revenue Trend",
    color_discrete_sequence=["#6c63ff"],
    custom_data = ["period_label", "revenue_label"]
)

fig_time.update_traces(
    fill='tozeroy', 
    fillcolor='rgba(108,99,255,0.15)', 
    line=dict(width=2.5),
    hovertemplate="<b>Period:<b> %{customdata[0]}<br><b>Revenue:</b> %{customdata[1]}<extra></extra>"
)

apply_theme(fig_time)
fig_time.update_xaxes(title="Period")
fig_time.update_yaxes(title="Revenue ($)")
st.plotly_chart(fig_time, use_container_width=True)

# ─────────────────────────────────────────
# SECTION 2 — CATEGORY & REGION
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Sales Breakdown</div>', unsafe_allow_html=True)
 
col_a, col_b = st.columns(2)
 
with col_a:
    options = ["Revenue", "Quantity"]
    selected_label = st.selectbox("Metric", options, key="bkd_metric")
    breakdown_metric = selected_label.lower()

    x_axis_title = "Revenue ($)" if selected_label == "Revenue" else "Quantity"
 
    cat_data = filtered.groupby('product_category')[breakdown_metric].sum().sort_values(ascending=False).reset_index()
 
    # Reusable formatter
    def fmt(x, metric):
        if metric == "revenue":
            if x >= 1_000_000:
                return f"${x/1_000_000:.2f}M"
            elif x >= 1_000:
                return f"${x/1_000:.2f}K"
            else:
                return f"${x:.2f}"
        return f"{x/1_000:.2f}K" if x >= 1_000 else f"{x:,}"
 
    cat_data["display_label"] = cat_data[breakdown_metric].apply(lambda x: fmt(x, breakdown_metric))
 
    # Build full hover string per row — no custom_data needed
    cat_data["hover_text"] = cat_data.apply(
        lambda row: f"<b>Product Category:</b> {row['product_category']}<br><b>{selected_label}:</b> {row['display_label']}",
        axis=1
    )
 
    fig_cat = px.bar(
        cat_data, x=breakdown_metric, y='product_category',
        orientation='h', title=f"{selected_label} by Category",
        color="product_category",
        color_discrete_sequence=COLOR_PALETTE,
        hover_name="hover_text",
        labels={
            breakdown_metric: x_axis_title,
            "product_category": "Product Category"
        }
    )
    fig_cat.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    apply_theme(fig_cat)
    fig_cat.update_layout(showlegend=False)
    st.plotly_chart(fig_cat, use_container_width=True)
 
with col_b:
    region_data = filtered.groupby('region')[breakdown_metric].sum().reset_index()
    region_data["display_label"] = region_data[breakdown_metric].apply(lambda x: fmt(x, breakdown_metric))
 
    # Same approach for pie chart
    region_data["hover_text"] = region_data.apply(
        lambda row: f"<b>Region:</b> {row['region']}<br><b>{selected_label}:</b> {row['display_label']}",
        axis=1
    )
 
    fig_region = px.pie(
        region_data, values=breakdown_metric, names='region',
        title=f"{selected_label} by Region",
        color_discrete_sequence=COLOR_PALETTE,
        hole=0.45,
        hover_name="hover_text",
    )
    fig_region.update_traces(
        textfont_color="#e8e8e8",
        hovertemplate="%{hovertext}<extra></extra>"
    )
    apply_theme(fig_region)
    st.plotly_chart(fig_region, use_container_width=True)

# ─────────────────────────────────────────
# SECTION 3 — PAYMENT & RETURNS
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Payment & Returns</div>', unsafe_allow_html=True)
 
col_c, col_d = st.columns(2)
 
with col_c:
    pay_data = filtered.groupby('payment_method')['revenue'].sum().sort_values(ascending=False).reset_index()
    pay_data['hover_text'] = pay_data.apply(
        lambda row: f"<b>Payment Method:</b> {row['payment_method']}<br><b>Revenue:</b> {fmt(row['revenue'], 'revenue')}",
        axis=1
    )
    fig_pay = px.bar(
        pay_data, x='payment_method', y='revenue',
        title="Revenue by Payment Method",
        color='payment_method',
        color_discrete_sequence=COLOR_PALETTE,
        hover_name='hover_text',
        labels={
            "payment_method": "Payment Method",
            "revenue": "Revenue"
        }
    )
    fig_pay.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    apply_theme(fig_pay)
    fig_pay.update_yaxes(title="Revenue ($)")
    fig_pay.update_layout(showlegend=False)
    st.plotly_chart(fig_pay, use_container_width=True)
 
with col_d:
    return_data = filtered.groupby('product_category')['is_returned'].mean().mul(100).sort_values(ascending=False).reset_index()
    return_data.columns = ['category', 'return_rate']
    return_data['hover_text'] = return_data.apply(
        lambda row: f"<b>Category:</b> {row['category']}<br><b>Return Rate:</b> {row['return_rate']:.2f}%",
        axis=1
    )
    fig_ret = px.bar(
        return_data, x='category', y='return_rate',
        title="Return Rate (%) by Category",
        color_discrete_sequence=["#ff6b6b"],
        hover_name='hover_text',
        labels={
            "category": "Category",
            "return_rate": "Return Rate (%)"
        }
    )
    fig_ret.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    apply_theme(fig_ret)
    st.plotly_chart(fig_ret, use_container_width=True)

# ─────────────────────────────────────────
# SECTION 4 — PRICE vs REVENUE SCATTER + RATING DIST
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Product & Customer Insights</div>', unsafe_allow_html=True)
 
col_e, col_f = st.columns(2)
 
with col_e:
    sample = filtered.sample(min(2000, len(filtered)), random_state=42).copy()
    sample['revenue_fmt'] = sample['revenue'].apply(lambda x: fmt(x, 'revenue'))
    sample['price_fmt'] = sample['product_price'].apply(lambda x: f"${x:,.2f}")
    sample['hover_text'] = sample.apply(
        lambda row: (
            f"<b>Category:</b> {row['product_category']}<br>"
            f"<b>Price:</b> {row['price_fmt']}<br>"
            f"<b>Revenue:</b> {row['revenue_fmt']}<br>"
            f"<b>Region:</b> {row['region']}<br>"
            f"<b>Quantity:</b> {row['quantity']}<br>"
            f"<b>Discount:</b> {row['discount_percent']}%"
        ),
        axis=1
    )
    fig_scatter = px.scatter(
        sample, x='product_price', y='revenue',
        color='product_category',
        title="Product Price vs Revenue (sampled)",
        opacity=0.55,
        color_discrete_sequence=COLOR_PALETTE,
        hover_name='hover_text',
        labels={
            "product_price": "Product Price",
            "revenue": "Revenue"
        }
    )
    fig_scatter.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    apply_theme(fig_scatter)
    fig_scatter.update_yaxes(title="Revenue ($)")
    st.plotly_chart(fig_scatter, use_container_width=True)
 
with col_f:
    rating_data = filtered['customer_rating'].value_counts().sort_index().reset_index()
    rating_data.columns = ['rating', 'count']
    rating_data['hover_text'] = rating_data.apply(
        lambda row: f"<b>Rating:</b> {row['rating']}<br><b>Count:</b> {row['count']:,}",
        axis=1
    )
    fig_rating = px.bar(
        rating_data, x='rating', y='count',
        title="Customer Rating Distribution",
        color='rating',
        color_continuous_scale='Viridis',
        hover_name='hover_text',
        labels={
            "rating": "Rating",
            "count": "Count"
        }
    )
    fig_rating.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    apply_theme(fig_rating)
    fig_rating.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_rating, use_container_width=True) 

# ─────────────────────────────────────────
# SECTION 5 — DISCOUNT IMPACT
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Discount Impact</div>', unsafe_allow_html=True)

discount_data = filtered.groupby('discount_percent').agg(
    avg_revenue=('revenue', 'mean'),
    order_count=('order_id', 'count'),
    avg_rating=('customer_rating', 'mean')
).reset_index()

fig_disc = make_subplots(specs=[[{"secondary_y": True}]])
fig_disc.add_trace(
    go.Bar(x=discount_data['discount_percent'], y=discount_data['order_count'],
           name='Order Count', marker_color='rgba(108,99,255,0.5)',
           hovertemplate = "Discount Percent = %{x}%<br>Order Count = %{y:.2s}<extra></extra>"),
    secondary_y=False
)
fig_disc.add_trace(
    go.Scatter(x=discount_data['discount_percent'], y=discount_data['avg_revenue'],
               name='Avg Revenue', mode='lines+markers',
               line=dict(color='#f7b731', width=2.5),
               hovertemplate = "Discount Percent = %{x}%<br>Average Revenue = $%{y:,.2f}<extra></extra>"),
    secondary_y=True
)
fig_disc.update_layout(
    title="Discount % vs Order Volume & Avg Revenue",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#a0aec0"), legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=40, b=20),
    hoverlabel=dict(
        bgcolor="rgba(30, 34, 53, 0.8)",
        font_size=13,
        font_family="Inter, sans-serif",
        bordercolor="#2e3047"
    )
)
fig_disc.update_xaxes(gridcolor="#1e2235", title="Discount %")
fig_disc.update_yaxes(gridcolor="#1e2235", title="Order Count", secondary_y=False)
fig_disc.update_yaxes(title="Avg Revenue ($)", secondary_y=True)
st.plotly_chart(fig_disc, use_container_width=True)

# ─────────────────────────────────────────
# SECTION 6 — DELIVERY DAYS ANALYSIS
# ─────────────────────────────────────────
st.markdown('<div class="section-header">Delivery Performance</div>', unsafe_allow_html=True)
 
col_g, col_h = st.columns(2)
 
with col_g:
    delivery_region = filtered.groupby('region')['delivery_days'].mean().sort_values().reset_index()
    delivery_region['hover_text'] = delivery_region.apply(
        lambda row: f"<b>Region:</b> {row['region']}<br><b>Avg Delivery:</b> {row['delivery_days']:.1f} days",
        axis=1
    )
    fig_del = px.bar(
        delivery_region, x='delivery_days', y='region',
        orientation='h', title="Avg Delivery Days by Region",
        color="region",
        color_discrete_sequence=COLOR_PALETTE,
        hover_name='hover_text',
        labels={
            "delivery_days": "Delivery Days",
            "region": "Region"
        }
    )
    fig_del.update_traces(hovertemplate="%{hovertext}<extra></extra>")
    apply_theme(fig_del)
    st.plotly_chart(fig_del, use_container_width=True)
 
with col_h:
    fig_del_hist = px.histogram(
        filtered, x='delivery_days',
        title="Delivery Days Distribution",
        color_discrete_sequence=["#4ecdc4"],
        nbins=20,
        labels={
            "delivery_days": "Delivery Days",
        }
    )
    fig_del_hist.update_traces(
        hovertemplate="<b>Delivery Days:</b> %{x}<br><b>Order Count:</b> %{y:,}<extra></extra>"
    )
    apply_theme(fig_del_hist)
    fig_del_hist.update_yaxes(title="Order Count")
    st.plotly_chart(fig_del_hist, use_container_width=True)

# ─────────────────────────────────────────
# RAW DATA VIEW (optional)
# ─────────────────────────────────────────
if show_raw:
    st.markdown('<div class="section-header">Raw Dataset</div>', unsafe_allow_html=True)
    st.markdown(f"Showing **{len(filtered):,}** filtered rows")
 
    search = st.text_input("🔎 Search (filter any text column)", "")
    display_df = filtered.copy()
 
    if search:
        mask = display_df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
        st.caption(f"{len(display_df):,} rows match your search")
 
    st.dataframe(
        display_df.sort_values('order_date', ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=500
    )
 
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download filtered data as CSV", csv, "filtered_sales.csv", "text/csv")

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#4a5568; font-size:13px'>E-Commerce Sales Dashboard</div>",
    unsafe_allow_html=True
)