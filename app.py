import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Reservoir Dashboard", layout="wide")

# ------------------------------
# Upload File
# ------------------------------
st.title("Havlena–Odeh Material Balance (Excel-Matching Version)")
uploaded = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded:

    # ------------------------------
    # Load Production and Initial
    # ------------------------------
    prod = pd.read_excel(uploaded, sheet_name="Production")
    init = pd.read_excel(uploaded, sheet_name="Initial")

    init = pd.Series(init["Value"].values, index=init["Parameter"].values)

    # Initial values
    Boi = float(init["Boi"])
    Bgi = float(init["Bgi"])
    Rsi = float(init["Rsi"])
    Swc = float(init["Swc"])
    Cw  = float(init["Cw"])
    Cf  = float(init["Cf"])

    # ------------------------------
    # Clean Production Columns
    # ------------------------------
    prod.columns = prod.columns.str.strip()

    # Convert required columns
    for c in ["p","Np","Gp","Bo","Bg","Rs"]:
        prod[c] = pd.to_numeric(prod[c], errors="coerce")

    # ------------------------------
    # Compute EXACT Excel Values
    # ------------------------------

    # 1) deltaP
    Pi = prod["p"].iloc[0]
    prod["dP"] = Pi - prod["p"]

    # 2) Efw  (same as excel)
    prod["Efw"] = ((Cw * Swc) + Cf) / (1 - Swc) * (Pi - prod["p"])

    # 3) Eo , Eg
    prod["Eo"] = (prod["Bo"] - Boi) + (prod["Rs"] - Rsi) * prod["Bg"]
    prod["Eg"] = prod["Bg"] - Bgi

    # 4) Rp EXACTLY like Excel
    prod["Rp"] = prod["Gp"] / prod["Np"]
    prod["Rp"] = prod["Rp"].replace([np.inf, -np.inf], 0).fillna(0)

    # 5) F EXACT like Excel
    prod["F"] = (
        prod["Np"] * (prod["Bo"] - Boi)
        + (prod["Gp"] - prod["Np"] * Rsi) * prod["Bg"]
    )

    # 6) X and Y like Excel
    prod["x"] = (prod["Eg"] + prod["Efw"]) / (prod["Eo"] + prod["Efw"])
    prod["y"] = prod["F"] / (prod["Eo"] + prod["Efw"])

    # Clean
    prod_clean = prod.replace([np.inf, -np.inf], np.nan).dropna()

    # ------------------------------
    # Regression ONLY 6 highest pressures
    # ------------------------------
    reg_data = prod_clean.sort_values("p", ascending=False).iloc[:6]

    coeffs = np.polyfit(reg_data["x"], reg_data["y"], 1)

    Nm = coeffs[0]   # slope = N*m
    N  = coeffs[1]   # intercept = N
    m  = Nm / N
    G  = N * m * (Boi / Bgi)

    # ------------------------------
    # Compute Fit Line (for plotting)
    # ------------------------------
    y_fit = Nm * prod_clean["x"] + N

    # ------------------------------
    # Display Results
    # ------------------------------

    st.subheader("📌 Final Results (Matches Excel)")
    col1, col2, col3 = st.columns(3)

    col1.metric("STOIIP (N)", f"{N:,.4e}")
    col2.metric("Gas Cap Ratio (m)", f"{m:,.4f}")
    col3.metric("GIIP (G)", f"{G:,.4e}")

    st.markdown("---")

    # ------------------------------
    # Plot
    # ------------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=prod_clean["x"], y=prod_clean["y"],
        mode="markers",
        marker=dict(size=9, color="gold"),
        name="Data"
    ))

    fig.add_trace(go.Scatter(
        x=prod_clean["x"], y=y_fit,
        mode="lines",
        line=dict(color="blue", width=3),
        name="Fit Line"
    ))

    fig.update_layout(
        title="Havlena–Odeh Straight Line",
        xaxis_title="(Eg + Efw) / (Eo + Efw)",
        yaxis_title="F / (Eo + Efw)",
        template="simple_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # Table
    # ------------------------------
    st.subheader("Data Table")
    st.dataframe(prod_clean[["p","Np","Gp","Eo","Eg","Efw","F","x","y"]])
