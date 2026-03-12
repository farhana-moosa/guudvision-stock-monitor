# stock_monitor/dashboard.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st
from stock_monitor.config import SUPABASE_URL, SUPABASE_KEY, STORE_NAMES
from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("Guud Vision Stock Monitor")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()

def get_latest_snapshots():
    response = (
        supabase.table("stock_snapshots")
        .select("*")
        .order("snapshot_date", desc=True)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None

    latest_date = response.data[0]["snapshot_date"]

    response = (
        supabase.table("stock_snapshots")
        .select("*")
        .eq("snapshot_date", latest_date)
        .eq("snapshot_type", "morning")
        .execute()
    )
    return pd.DataFrame(response.data)


def get_thresholds():
    response = supabase.table("prescription_thresholds").select("*").execute()
    return {
        (row["sphere"], row["cylinder"]): row["threshold"]
        for row in response.data
    }

check_password()

st.set_page_config(page_title="Guud Vision Stock Monitor", layout="wide")
st.title("Guud Vision Stock Monitor")

df = get_latest_snapshots()

if df is None:
    st.warning("No stock data available yet.")
    st.stop()

thresholds = get_thresholds()

df["store_name"] = df["store_id"].astype(str).map(STORE_NAMES)
df["threshold"] = df.apply(
    lambda row: thresholds.get((row["sphere"], row["cylinder"]), None), axis=1
)
df["below_threshold"] = df["quantity"] < df["threshold"]
df["to_reach_threshold"] = (df["threshold"] - df["quantity"]).clip(lower=0)

df["sphere"] = df["sphere"].round(2)
df["cylinder"] = df["cylinder"].round(2)
df["quantity"] = df["quantity"].astype(int)
df["threshold"] = df["threshold"].astype(int)
df["to_reach_threshold"] = df["to_reach_threshold"].astype(int)

st.caption(f"Showing stock data for: {df['snapshot_date'].iloc[0]}")

# metrics row
col1, col2, col3 = st.columns(3)

total_alerts = len(df[df["below_threshold"] == True])
mobiles_affected = df[df["below_threshold"] == True]["store_name"].nunique()
last_updated = df["snapshot_date"].iloc[0]

with col1:
    st.metric("Total Alerts", total_alerts)
with col2:
    st.metric("Mobiles Affected", mobiles_affected)
with col3:
    st.metric("Last Updated", last_updated)

# mobile selector
store_options = ["All Mobiles"] + [v for v in STORE_NAMES.values()]
selected_store = st.selectbox("Select Mobile", store_options)

# filter by selected store
if selected_store == "All Mobiles":
    filtered_df = df
else:
    filtered_df = df[df["store_name"] == selected_store]

# tabs
tab1, tab2 = st.tabs(["Alerts", "Full Stock View"])

with tab1:
    alerts = filtered_df[filtered_df["below_threshold"] == True][[
        "store_name", "sphere", "cylinder", "quantity", "threshold", "to_reach_threshold"
    ]].rename(columns={
        "store_name": "Mobile",
        "sphere": "Sphere",
        "cylinder": "Cylinder",
        "quantity": "Current Stock",
        "threshold": "Threshold",
        "to_reach_threshold": "Units to Order"
    })
    st.subheader(f"Prescriptions Below Threshold ({len(alerts)})")
    st.dataframe(alerts, use_container_width=True, hide_index=True)

with tab2:
    full = filtered_df[[
        "store_name", "sphere", "cylinder", "quantity", "threshold", "below_threshold", "to_reach_threshold"
    ]].rename(columns={
        "store_name": "Mobile",
        "sphere": "Sphere",
        "cylinder": "Cylinder",
        "quantity": "Current Stock",
        "threshold": "Threshold",
        "below_threshold": "Below Threshold",
        "to_reach_threshold": "Units to Order"
    })
    st.subheader(f"Full Stock View ({len(full)} prescriptions)")
    st.dataframe(
        full.style.apply(
            lambda row: ["background-color: #FFCCCC" if row["Below Threshold"] == True else "" for _ in row],
            axis=1
        ),
        use_container_width=True,
        hide_index=True
    )
