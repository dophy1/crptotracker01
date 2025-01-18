import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Set the page configuration as the first Streamlit command
st.set_page_config(page_title="SEP Crypto Tracker", page_icon="💰")

st.header("SEP Crypto Tracker")
st.write("This is a crypto tracker for SEP")

# Use the secret API key
coincap_api_key = "your_actual_api_key_here"

@st.cache_data(ttl=60)
def get_crypto_prices(cryptos):
    try:
        url = "https://api.coincap.io/v2/assets"
        params = {"ids": ",".join(cryptos)}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {crypto['id']: float(crypto['priceUsd']) for crypto in data['data']}
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

def format_price(price):
    return f"${price:.2f}"

# Sidebar for user input
st.sidebar.header("Settings")
cryptos_input = st.sidebar.text_input(
    "Enter cryptocurrencies to track (comma-separated)",
    value="bitcoin,ethereum,dogecoin"
)
update_interval = st.sidebar.number_input(
    "Update interval (seconds)",
    min_value=60,
    value=60,
    step=10
)

# Main content
if st.sidebar.button("Start Tracking"):
    cryptos_to_track = [crypto.strip().lower() for crypto in cryptos_input.split(",")]
    
    # Initialize session state for historical data
    if 'historical_data' not in st.session_state:
        st.session_state.historical_data = {crypto: [] for crypto in cryptos_to_track}
    
    # Create placeholders for dynamic content
    time_placeholder = st.empty()
    price_table = st.empty()
    charts = st.empty()
    
    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time_placeholder.text(f"Last updated: {current_time}")
        
        prices = get_crypto_prices(cryptos_to_track)
        
        if prices:
            # Update price table
            df = pd.DataFrame({
                "Cryptocurrency": [crypto.capitalize() for crypto in cryptos_to_track],
                "Price (USD)": [format_price(prices.get(crypto, 0)) for crypto in cryptos_to_track]
            })
            price_table.dataframe(df, hide_index=True)
            
            # Update historical data
            for crypto in cryptos_to_track:
                if crypto in prices:
                    st.session_state.historical_data[crypto].append((current_time, prices[crypto]))
                    # Keep only the last 100 data points
                    st.session_state.historical_data[crypto] = st.session_state.historical_data[crypto][-100:]
            
            # Update charts
            with charts.container():
                for crypto in cryptos_to_track:
                    if st.session_state.historical_data[crypto]:
                        df = pd.DataFrame(st.session_state.historical_data[crypto], columns=['Time', 'Price'])
                        st.line_chart(df.set_index('Time'))
        else:
            st.error("Failed to fetch prices for all cryptocurrencies.")
        
        time.sleep(update_interval)
        st.experimental_rerun()
else:
    st.write("Click 'Start Tracking' in the sidebar to begin tracking cryptocurrencies.")

