# wait_times_dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Dashboard title
# ----------------------------
st.set_page_config(page_title="🎢 Disney Wait Time Dashboard", layout="wide")
st.title("📊 Disney Wait Time Dashboard")

# ----------------------------
# Load & cache data
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/clean/cleandata.csv", parse_dates=['date'])

df = load_data()

# ----------------------------
# Sidebar Filters
# ----------------------------
attractions = df['attraction'].unique()
selected_attraction = st.sidebar.selectbox("🎠 Choose an Attraction", attractions)

date_range = st.sidebar.date_input(
    "📅 Select Date Range", 
    value=(df['date'].min(), df['date'].max())
)

# ----------------------------
# Filtered Data
# ----------------------------
if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered = df[
        (df['attraction'] == selected_attraction) &
        (df['date'] >= pd.to_datetime(date_range[0])) &
        (df['date'] <= pd.to_datetime(date_range[1]))
    ]
else:
    st.warning("Please select a valid date range.")
    filtered = df[df['attraction'] == selected_attraction]

# ----------------------------
# Group by date for plotting
# ----------------------------
if not filtered.empty:
    daily = filtered.groupby('date')[['SPOSTMIN_interp', 'SACTMIN_filled']].mean().reset_index()

    # ----------------------------
    # Line Chart
    # ----------------------------
    st.subheader(f"📈 Daily Wait Time Trend: {selected_attraction}")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(daily['date'], daily['SPOSTMIN_interp'], label='Posted Wait Time')
    ax.plot(daily['date'], daily['SACTMIN_filled'], label='Actual Wait Time', linestyle='--')
    ax.set_ylabel("Minutes")
    ax.set_title("Daily Average Wait Time")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # ----------------------------
    # Avg Overestimation Metric
    # ----------------------------
    daily['gap'] = daily['SPOSTMIN_interp'] - daily['SACTMIN_filled']
    avg_gap = daily['gap'].mean()
    st.metric("📉 Avg Overestimation", f"{avg_gap:.1f} minutes" if pd.notna(avg_gap) else "N/A")
else:
    st.warning("No data found for this attraction and date range.")

# ----------------------------
# ⚡ Guest Tip: Busy vs Chill Ride
# ----------------------------
st.subheader("⚡ Guest Tip of the Moment")

attraction_avgs = df.groupby('attraction')[['SACTMIN_filled']].mean().reset_index()
attraction_avgs = attraction_avgs.dropna().sort_values('SACTMIN_filled', ascending=False)

if len(attraction_avgs) >= 2:
    top_busy = attraction_avgs.iloc[0]
    top_chill = attraction_avgs.iloc[-1]

    busy_name = top_busy['attraction'].replace("_", " ").title()
    chill_name = top_chill['attraction'].replace("_", " ").title()

    busy_wait = round(top_busy['SACTMIN_filled'])
    chill_wait = round(top_chill['SACTMIN_filled'])

    st.markdown(f"""
    > 🕐 The average wait for **{busy_name}** is **{busy_wait} mins**.  
    > 🎯 Consider riding **{chill_name}** instead — it's just **{chill_wait} mins**!
    """)
else:
    st.warning("⚠️ Not enough data to generate a guest tip.")
