# wait_times_dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/clean/clean_dataset.csv", parse_dates=['date'])

df = load_data()

# Dashboard title
st.title("🎢 Disney Wait Time Dashboard")

# Sidebar filters
attractions = df['attraction'].unique()
selected_attraction = st.sidebar.selectbox("🎠 Choose an Attraction", attractions)

date_range = st.sidebar.date_input("📅 Select Date Range",
                                   [df['date'].min(), df['date'].max()])

# Filtered data
filtered = df[
    (df['attraction'] == selected_attraction) &
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1]))
]

# Group by date
daily = filtered.groupby('date')[['SPOSTMIN_interp', 'SACTMIN_filled']].mean().reset_index()

# Line chart
st.subheader(f"📈 Daily Wait Time Trend: {selected_attraction}")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(daily['date'], daily['SPOSTMIN_interp'], label='Posted Wait Time')
ax.plot(daily['date'], daily['SACTMIN_filled'], label='Actual Wait Time', linestyle='--')
ax.set_ylabel("Minutes")
ax.set_title("Daily Average Wait Time")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Avg overestimation
daily['gap'] = daily['SPOSTMIN_interp'] - daily['SACTMIN_filled']
st.metric("⏳ Avg Overestimation", f"{daily['gap'].mean():.1f} minutes")
