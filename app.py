import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -------------------- PAGE STYLE --------------------
st.set_page_config(page_title="Havlena–Odeh Dashboard", layout="wide")

# CSS styling
st.markdown("""
    <style>
        .big-title {
            font-size: 42px;
            font-weight: 700;
            color: #2b2b2b;
            text-align: center;
            margin-bottom: 10px;
        }
        .sub-title {
            font-size: 20px;
            color: #555;
            text-align: center;
            margin-bottom: 30px;
        }
        .card {
            padding: 20px;
            border-radius: 12px;
            background-color: #fafafa;
            border: 1px solid #e5e5e5;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.markdown("<div class='big-title'>🛢️ Havlena–Odeh Reservoir Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Interactive Material Balance Analysis</div>", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.header("📂 Upload Excel File")
uploaded = st.sidebar.file_uploader("Upload (.xlsx) file", type=["xlsx"])

st.sidebar.markdown("---")
st.sidebar.info("Make sure your Excel file contains sheets: **Production** & **Initial**")


# -------------------- MAIN LOGIC --------------------
if uploaded:
    prod = pd.read_excel(uploaded, sheet_name="Production")
    init_df = pd.read_excel(uploaded, sheet_name="Initial")

    init = pd.Series(init_df["Value"].values, index=init_df["Parameter"].values)

    Boi = init["Boi"]
    Bgi = init["Bgi"]
    Rsi = init["Rsi"]

    prod["Eo"] = prod["Bo"] - Boi + (prod["Rs"] - Rsi) * prod["Bg"]
    prod["Eg"] = prod["Bg"] - Bgi
    prod["F"] = prod["Np"] * (prod["Bo"] - Boi) + (prod["Gp"] - prod["Np"] * Rsi) * prod["Bg"]

    prod["x"] = prod["Eo"] / prod["Eg"]
    prod["y"] = prod["F"] / prod["Eg"]

    prod = prod.replace([np.inf, -np.inf, np.nan], 0).dropna()

    coeffs = np.polyfit(prod["x"], prod["y"], 1)
    N, m = coeffs[1], coeffs[0]

    # -------------------- METRIC CARDS --------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Original Oil in Place (N)", f"{N:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Gas Cap Gas in Place (m)", f"{m:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Gas Cap Ratio (m/N)", f"{m/N:.4f}")
        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------- PLOT --------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=prod["x"], 
        y=prod["y"],
        mode="markers",
        marker=dict(size=9, color="#1f77b4"),
        name="Data Points"
    ))

    fig.add_trace(go.Scatter(
        x=prod["x"], 
        y=m*prod["x"] + N,
        mode="lines",
        line=dict(color="#d62728", width=3),
        name="Best Fit Line"
    ))

    fig.update_layout(
        title="Havlena–Odeh Plot (F/Eg vs. Eo/Eg)",
        xaxis_title="Eo/Eg",
        yaxis_title="F/Eg",
        template="simple_white",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("⬅️ Upload an Excel file from the sidebar to get started.")
