# stock_monitor/dashboard.py

import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.express as px
import streamlit as st
from stock_monitor.config import STORE_NAMES
from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


# ── Logo ──────────────────────────────────────────────────────────────────────
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "guud_logo.png")
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #FFFFFF;
}

.dashboard-header {
    background: #FFFFFF;
    border-bottom: 3px solid #FF2D6B;
    padding: 20px 0px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.dashboard-header h1 {
    color: #1A1A1A;
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0;
}
.dashboard-header p {
    color: #999999;
    font-size: 0.78rem;
    margin: 4px 0 0 0;
    font-family: 'DM Mono', monospace;
}

.metric-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 20px 24px;
    border: 1px solid #F0F0F0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.metric-label {
    color: #999999;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.metric-value {
    color: #1A1A1A;
    font-size: 2rem;
    font-weight: 600;
    line-height: 1;
}
.metric-value.alert {
    color: #FF2D6B;
}
.metric-value.date {
    font-size: 1.1rem;
    font-family: 'DM Mono', monospace;
    color: #FF2D6B;
}

.section-header {
    color: #1A1A1A;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #FF2D6B;
}

.status-banner-critical {
    background: #FFF0F4;
    border: 1px solid #FF2D6B;
    border-left: 4px solid #FF2D6B;
    border-radius: 8px;
    padding: 12px 20px;
    color: #CC1A4F;
    font-weight: 500;
    font-size: 0.9rem;
    margin-bottom: 20px;
}
.status-banner-healthy {
    background: #F0FFF6;
    border: 1px solid #27AE60;
    border-left: 4px solid #27AE60;
    border-radius: 8px;
    padding: 12px 20px;
    color: #1A7A40;
    font-weight: 500;
    font-size: 0.9rem;
    margin-bottom: 20px;
}

.login-container {
    max-width: 400px;
    margin: 80px auto;
    background: white;
    border-radius: 16px;
    padding: 48px 40px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    border: 1px solid #F0F0F0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stSelectbox > div > div {
    background: white;
    border: 1px solid #F0F0F0;
    border-radius: 8px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F7F7F7;
    padding: 4px;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    padding: 8px 20px;
    font-size: 0.85rem;
    font-weight: 500;
    color: #999999;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #FF2D6B !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)


# ── Auth ──────────────────────────────────────────────────────────────────────
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        logo_b64 = get_logo_base64()

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 48px 40px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                border: 1px solid #F0F0F0;
                border-top: 4px solid #FF2D6B;
                text-align: center;
                margin-top: 80px;
            ">
                <img src="data:image/png;base64,{logo_b64}" height="56" style="margin-bottom: 20px;">
                <div style="color: #1A1A1A; font-size: 1.2rem; font-weight: 600; margin-bottom: 4px;">Stock Monitor</div>
                <div style="color: #999999; font-size: 0.85rem; margin-bottom: 32px;">Secure access — authorised users only</div>
            </div>
            """, unsafe_allow_html=True)

            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter password")
            if st.button("Sign In", use_container_width=True):
                if password == st.secrets["APP_PASSWORD"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
        st.stop()


# ── Data fetching ─────────────────────────────────────────────────────────────
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


def get_all_snapshots(snapshot_type):
    all_rows = []
    page_size = 1000
    start = 0
    while True:
        response = (
            supabase.table("stock_snapshots")
            .select("*")
            .eq("snapshot_type", snapshot_type)
            .order("snapshot_date", desc=False)
            .range(start, start + page_size - 1)
            .execute()
        )
        if not response.data:
            break
        all_rows.extend(response.data)
        if len(response.data) < page_size:
            break
        start += page_size
    return pd.DataFrame(all_rows)


def get_thresholds():
    response = supabase.table("prescription_thresholds").select("*").execute()
    return {
        (row["sphere"], row["cylinder"]): row["threshold"]
        for row in response.data
    }


def get_latest_frame_snapshots():
    response = (
        supabase.table("frame_snapshots")
        .select("*")
        .order("snapshot_date", desc=True)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    latest_date = response.data[0]["snapshot_date"]
    response = (
        supabase.table("frame_snapshots")
        .select("*")
        .eq("snapshot_date", latest_date)
        .eq("snapshot_type", "morning")
        .execute()
    )
    return pd.DataFrame(response.data)


def calculate_consumption(all_snapshots_df):
    df = all_snapshots_df.copy()
    df["store_name"] = df["store_id"].astype(str).map(STORE_NAMES)
    df = df.sort_values("snapshot_date")
    df["consumed"] = df.groupby(
        ["store_id", "sphere", "cylinder"]
    )["quantity"].diff(-1)
    df["consumed"] = df["consumed"].clip(lower=0).fillna(0).astype(int)
    return df


# ── App ───────────────────────────────────────────────────────────────────────
check_password()

st.set_page_config(page_title="Guud Vision Stock Monitor", layout="wide")

# load data
df = get_latest_snapshots()
frames_df = get_latest_frame_snapshots()
all_snapshots_df = get_all_snapshots("morning")
consumption_df = calculate_consumption(all_snapshots_df)

if df is None:
    st.warning("No stock data available yet.")
    st.stop()

thresholds = get_thresholds()

df["store_name"] = df["store_id"].astype(str).map(STORE_NAMES)
df = df[df["store_name"].notna()]
df["threshold"] = df.apply(
    lambda row: thresholds.get((row["sphere"], row["cylinder"]), None), axis=1
)
df["below_threshold"] = df["quantity"] < df["threshold"]
df["to_reach_threshold"] = (df["threshold"] - df["quantity"]).clip(lower=0)
df["sphere"] = df["sphere"].round(2)
df["cylinder"] = df["cylinder"].round(2)
df["quantity"] = df["quantity"].fillna(0).astype(int)
df["threshold"] = df["threshold"].fillna(0).astype(int)
df["to_reach_threshold"] = df["to_reach_threshold"].fillna(0).astype(int)

total_alerts = len(df[df["below_threshold"] == True])
mobiles_affected = df[df["below_threshold"] == True]["store_name"].nunique()
last_updated = df["snapshot_date"].iloc[0]

# header
logo_b64 = get_logo_base64()
st.markdown(f"""
<div class="dashboard-header">
    <img src="data:image/png;base64,{logo_b64}" height="48">
    <div>
        <h1>Stock Monitor</h1>
        <p>Data refreshes every morning at 07:00 SAST · Last snapshot: {last_updated}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Alerts</div>
        <div class="metric-value alert">{total_alerts}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Mobiles Affected</div>
        <div class="metric-value">{mobiles_affected}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Last Updated</div>
        <div class="metric-value date">{last_updated}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 24px'></div>", unsafe_allow_html=True)

# status banner
if total_alerts > 0:
    st.markdown(f"""
    <div class="status-banner-critical">
        ⚠️ {total_alerts} prescriptions below reorder threshold across {mobiles_affected} mobile units — immediate restocking required
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-banner-healthy">
        ✅ All mobile units are within healthy stock levels
    </div>
    """, unsafe_allow_html=True)

# mobile selector
store_options = ["All Mobiles"] + [v for v in STORE_NAMES.values()]
selected_store = st.selectbox("Filter by Mobile", store_options)

# filter
if selected_store == "All Mobiles":
    filtered_df = df
    filtered_frames_df = frames_df if frames_df is not None else None
else:
    filtered_df = df[df["store_name"] == selected_store]
    if frames_df is not None:
        filtered_frames_df = frames_df[frames_df["store_id"].astype(str).map(STORE_NAMES) == selected_store]
    else:
        filtered_frames_df = None

st.markdown("<div style='margin-top: 8px'></div>", unsafe_allow_html=True)

# tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚠️ Alerts", "🔵 Lens Stock", "🟤 Frame Stock", "📈 Consumption Trends", "🗺️ Predictive Restocking"])

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
    st.markdown(f'<div class="section-header">Prescriptions Below Threshold — {len(alerts)} alerts</div>', unsafe_allow_html=True)

    if not alerts.empty:
        chart_data = alerts.groupby("Mobile")["Units to Order"].sum().reset_index()
        fig = px.bar(
            chart_data,
            x="Mobile",
            y="Units to Order",
            title="Total Units to Order by Mobile",
            color_discrete_sequence=["#FF2D6B"]
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_family="DM Sans",
            title_font_size=14,
            title_font_color="#1A1A1A",
            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
            margin=dict(t=40, b=40, l=20, r=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

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
    st.markdown(f'<div class="section-header">Lens Stock — {len(full)} prescriptions</div>', unsafe_allow_html=True)
    st.dataframe(
        full.style.apply(
            lambda row: ["background-color: #FDEAEA" if row["Below Threshold"] == True else "" for _ in row],
            axis=1
        ).format({"Sphere": "{:.2f}", "Cylinder": "{:.2f}"}),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    if filtered_frames_df is None or filtered_frames_df.empty:
        st.info("No frame stock data available.")
    else:
        frames = filtered_frames_df[[
            "store_id", "brand", "model", "color", "amount_on_hand"
        ]].copy()
        frames["store_id"] = frames["store_id"].astype(str).map(STORE_NAMES)
        frames = frames.rename(columns={
            "store_id": "Mobile",
            "brand": "Brand",
            "model": "Model",
            "color": "Color",
            "amount_on_hand": "Amount on Hand"
        })
        st.markdown(f'<div class="section-header">Frame Stock — {len(frames)} frames</div>', unsafe_allow_html=True)
        st.dataframe(frames, use_container_width=True, hide_index=True)

with tab4:
    st.markdown('<div class="section-header">Consumption Trends</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: #FFF8E1;
        border: 1px solid #F5A623;
        border-left: 4px solid #F5A623;
        border-radius: 8px;
        padding: 12px 20px;
        margin-bottom: 20px;
        color: #7A5800;
        font-size: 0.88rem;
        font-weight: 500;
    ">
        🔄 Consumption data is actively being collected — trends will populate as daily snapshots accumulate over the coming weeks.
    </div>
    """, unsafe_allow_html=True)

    if consumption_df is not None and not consumption_df.empty:
        if selected_store == "All Mobiles":
            filtered_consumption = consumption_df
        else:
            filtered_consumption = consumption_df[consumption_df["store_name"] == selected_store]

        trend_data = filtered_consumption.groupby(["snapshot_date", "store_name"])["quantity"].mean().reset_index()
        fig = px.line(
            trend_data,
            x="snapshot_date",
            y="quantity",
            color="store_name",
            title="Average Stock Level Over Time by Mobile",
            labels={"snapshot_date": "Date", "quantity": "Avg Stock Level", "store_name": "Mobile"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_family="DM Sans",
            title_font_size=14,
            title_font_color="#1A1A1A",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
            margin=dict(t=40, b=40, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3)
        )
        st.plotly_chart(fig, use_container_width=True)

        consumption_display = filtered_consumption[[
            "snapshot_date", "store_name", "sphere", "cylinder", "quantity", "consumed"
        ]].rename(columns={
            "snapshot_date": "Date",
            "store_name": "Mobile",
            "sphere": "Sphere",
            "cylinder": "Cylinder",
            "quantity": "Stock Level",
            "consumed": "Consumed"
        })
        st.markdown('<div class="section-header">Detail View</div>', unsafe_allow_html=True)
        st.dataframe(consumption_display, use_container_width=True, hide_index=True)

with tab5:
    st.markdown('<div class="section-header">Predictive Restocking — Coming Soon</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: #FFF0F4;
        border: 1px solid #FF2D6B;
        border-left: 4px solid #FF2D6B;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 24px;
    ">
        <div style="font-weight: 600; color: #CC1A4F; margin-bottom: 8px;">🚀 Phase 2 — In Development</div>
        <div style="color: #1A1A1A; font-size: 0.9rem; line-height: 1.6;">
            This module will use machine learning to predict how much stock each mobile unit requires
            based on its upcoming schedule and deployment location. By combining historical dispensing
            patterns with route data, the system will automatically recommend restocking quantities
            before each mobile departs — eliminating stock outages at the point of care.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Planned Capability</div>
            <div style="color: #1A1A1A; font-size: 0.9rem; line-height: 1.8; margin-top: 8px;">
                📍 Location-aware stock prediction<br>
                📅 Schedule-based restocking recommendations<br>
                📊 Per-mobile demand forecasting<br>
                ⚡ Proactive alerts before departure
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Data Pipeline</div>
            <div style="color: #1A1A1A; font-size: 0.9rem; line-height: 1.8; margin-top: 8px;">
                ✅ Daily stock snapshots — live<br>
                ✅ Historical dispensing records — in progress<br>
                🔄 Mobile schedule integration — planned<br>
                🔄 ML forecasting model — planned
            </div>
        </div>
        """, unsafe_allow_html=True)