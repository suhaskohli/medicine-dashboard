import streamlit as st
import requests
import pandas as pd

# Set your API Gateway GET endpoint here
API_URL = "https://your-api-url/medicines/{owner_id}"

st.set_page_config(page_title="Medicine Supply Chain Dashboard", layout="wide")

st.title("💊 Medicine Inventory Dashboard")
owner_id = st.text_input("Enter Distributor/Owner ID:", value="distributor123")

if owner_id:
    try:
        response = requests.get(API_URL.replace("{owner_id}", owner_id))
        if response.status_code == 200:
            data = response.json()

            if not data:
                st.warning("No data found for this owner.")
            else:
                df = pd.DataFrame(data)

                # Convert numeric columns if needed
                numeric_cols = ['price', 'stock', 'sales']
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                st.subheader("📦 Inventory Overview")
                st.dataframe(df.style.format({
                    'price': '₹{:.2f}',
                    'stock': '{:.0f}',
                    'sales': '{:.0f}'
                }), use_container_width=True)

                # Highlight low-stock items
                low_stock_df = df[df['stock'] < 50]
                if not low_stock_df.empty:
                    st.subheader("⚠️ Low Stock Alerts")
                    st.table(low_stock_df[['medicine_name', 'stock', 'price', 'top_usage_location']])

                # Visuals
                st.subheader("📈 Sales vs Stock")
                chart_data = df[['medicine_name', 'sales', 'stock']].set_index('medicine_name')
                st.bar_chart(chart_data)

                st.subheader("📍 Current Locations (Live GPS)")
                if 'current_location' in df.columns:
                    st.map(df[['current_location']].dropna().rename(columns={'current_location': 'lat_lng'}))

        else:
            st.error(f"Failed to fetch data: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
