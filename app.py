import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Reservoir Dashboard", layout="wide")

st.title("🛢 Reservoir Dashboard — Havlena–Odeh")

uploaded = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded:
    prod = pd.read_excel(uploaded, sheet_name="Production")
    init_df = pd.read_excel(uploaded, sheet_name="Initial")

    init = pd.Series(init_df["Value"].values, index=init_df["Parameter"].values)

    Boi = init["Boi"]
    Bgi = init["Bgi"]
    Rsi = init["Rsi"]

    prod["Eo"] = prod["Bo"] - Boi + (prod["Rs"] - Rsi)*prod["Bg"]
    prod["Eg"] = prod["Bg"] - Bgi
    prod["F"]  = prod["Np"]*(prod["Bo"] - Boi) + (prod["Gp"] - prod["Np"]*Rsi)*prod["Bg"]

    prod["x"] = prod["Eo"] / prod["Eg"]
    prod["y"] = prod["F"] / prod["Eg"]

    prod = prod.replace([np.inf, -np.inf], np.nan).dropna()

    coeffs = np.polyfit(prod["x"], prod["y"], 1)
    N, G = coeffs[0], coeffs[1]
    m = (G * Bgi) / (N * Boi)

    st.metric("Original Oil in Place (N)", f"{N:,.2f}")
    st.metric("Gas Cap Gas in Place (G)", f"{G:,.2f}")
    st.metric("Gas Cap Ratio (m)", f"{m:.4f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prod["x"], y=prod["y"], mode="markers", name="Data"))
    fig.add_trace(go.Scatter(x=prod["x"], y=N*prod["x"] + G, mode="lines", name="Fit"))
    st.plotly_chart(fig)
else:
    st.info("Upload an Excel file to start.")
