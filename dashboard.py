import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# Backend API configuration
# ---------------------------
API_BASE = "http://localhost:5001"  # Flask backend URL

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard (Streamlit + Flask API)")

st.markdown("This dashboard connects to the Flask API running at port 5001.")

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.header("🔍 Filters")

source = st.sidebar.selectbox("Data Source", ["xlsx", "sql"])
product = st.sidebar.text_input("Product Line")
city = st.sidebar.text_input("City")
gender = st.sidebar.selectbox("Gender", ["", "Male", "Female"])
payment = st.sidebar.text_input("Payment")
limit = st.sidebar.number_input("Limit", min_value=0, value=0)
offset = st.sidebar.number_input("Offset", min_value=0, value=0)

if st.sidebar.button("Fetch Data"):
    params = {"source": source}
    if product:
        params["product"] = product
    if city:
        params["city"] = city
    if gender:
        params["gender"] = gender
    if payment:
        params["payment"] = payment
    if limit > 0:
        params["limit"] = limit
    if offset > 0:
        params["offset"] = offset

    try:
        resp = requests.get(f"{API_BASE}/api/sales", params=params, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            if not data:
                st.warning("⚠️ No records found with these filters.")
            else:
                df = pd.DataFrame(data)
                st.success(f"✅ Fetched {len(df)} records from API")

                # ---------------------------
                # KPI Metrics
                # ---------------------------
                total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
                avg_rating = df["Rating"].mean() if "Rating" in df.columns else 0
                total_orders = len(df)
                avg_cogs = df["cogs"].mean() if "cogs" in df.columns else 0

                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("💰 Total Sales", f"${total_sales:,.2f}")
                kpi2.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
                kpi3.metric("🛒 Orders", f"{total_orders}")
                kpi4.metric("🏭 Avg COGS", f"${avg_cogs:,.2f}")

                # ---------------------------
                # Show Raw Data
                # ---------------------------
                with st.expander("📂 Show Raw Data"):
                    st.dataframe(df, use_container_width=True)

                # ---------------------------
                # Tabs for Visualizations
                # ---------------------------
                st.subheader("📊 Interactive Visualizations")
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "By Product Line", "By Payment", "Over Time", "By City", "Quantity vs Sales"
                ])

                # 1. Sales by Product Line
                with tab1:
                    if "Product line" in df.columns and "Sales" in df.columns:
                        sales_by_product = df.groupby("Product line", as_index=False)["Sales"].sum()
                        fig1 = px.bar(
                            sales_by_product, x="Product line", y="Sales",
                            color="Sales", text_auto=True,
                            title="Total Sales by Product Line",
                            color_continuous_scale="Blues"
                        )
                        fig1.update_layout(xaxis_title="", yaxis_title="Sales", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig1, use_container_width=True)

                # 2. Sales Distribution by Payment Method
                with tab2:
                    if "Payment" in df.columns and "Sales" in df.columns:
                        fig2 = px.pie(
                            df, names="Payment", values="Sales",
                            title="Sales Distribution by Payment Method",
                            hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                # 3. Sales Over Time
                with tab3:
                    for col in ["Date", "Invoice Date", "date"]:
                        if col in df.columns and "Sales" in df.columns:
                            df[col] = pd.to_datetime(df[col], errors="coerce")
                            sales_over_time = df.groupby(col, as_index=False)["Sales"].sum()
                            fig3 = px.line(
                                sales_over_time, x=col, y="Sales",
                                title=f"Sales Over Time ({col})",
                                markers=True, color_discrete_sequence=["#1f77b4"]
                            )
                            st.plotly_chart(fig3, use_container_width=True)
                            break

                # 4. Sales by City
                with tab4:
                    if "City" in df.columns and "Sales" in df.columns:
                        sales_by_city = df.groupby("City", as_index=False)["Sales"].sum()
                        fig4 = px.bar(
                            sales_by_city, x="City", y="Sales",
                            color="City", text_auto=True,
                            title="Total Sales by City"
                        )
                        fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig4, use_container_width=True)

                # 5. Quantity vs Sales
                with tab5:
                    if "Quantity" in df.columns and "Sales" in df.columns:
                        fig5 = px.scatter(
                            df, x="Quantity", y="Sales",
                            size="Sales", color="Product line",
                            hover_data=["City", "Payment"],
                            title="Quantity vs Sales by Product Line"
                        )
                        st.plotly_chart(fig5, use_container_width=True)

        else:
            st.error(f"❌ API request failed ({resp.status_code}): {resp.text}")