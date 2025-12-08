import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Configuration ---
st.set_page_config(page_title="Reservoir Dashboard", layout="wide")

st.title("🛢 Reservoir Dashboard — Havlena–Odeh Straight-Line Analysis")
st.markdown("""
    This application calculates the **Original Oil in Place (N)**, **Initial Gas-Cap Gas in Place (G)**,
    and the **Gas-Cap Ratio (m)** for a gas-cap oil reservoir using the **Havlena–Odeh Material Balance Method**.
""")

# --- Sidebar for Input and Guide ---
st.sidebar.header("📥 Data Upload and Instructions")
uploaded = st.sidebar.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

with st.sidebar.expander("📝 User Guide: Excel File Format"):
    st.markdown("""
        The uploaded Excel file **must** contain two sheets:
        1. **'Production' Sheet:** Contains time-dependent PVT and production data.
           * **Required Columns:** `p`, `Np`, `Gp`, `Bo`, `Bg`, `Rs`.
        2. **'Initial' Sheet:** Contains initial reservoir parameters.
           * **Required Parameters (Parameter, Value):** Must include `Boi`, `Bgi`, `Rsi`.
    """)
st.sidebar.markdown("---")


if uploaded:
    # --- Data Loading and Initial Parameter Processing ---
    try:
        prod = pd.read_excel(uploaded, sheet_name="Production")
        init_df = pd.read_excel(uploaded, sheet_name="Initial")
        
        # --- FIX 1: Clean up empty/unnamed columns immediately ---
        # Drop columns that are entirely NaN (like the leading blank columns)
        prod = prod.dropna(axis=1, how='all')
        
        init = pd.Series(init_df["Value"].values, index=init_df["Parameter"].values)
        
        Boi = init["Boi"]
        Bgi = init["Bgi"]
        Rsi = init["Rsi"]

    except Exception as e:
        st.error(f"Error loading data. Check your sheet names ('Production', 'Initial') or Initial parameters ('Boi', 'Bgi', 'Rsi'). Details: {e}")
        st.stop()


    # --- Input Validation Check (Robustness, using your uppercase 'P') ---
    required_prod_cols = ["P", "Np", "Gp", "Bo", "Bg", "Rs"]
    missing_prod_cols = [col for col in required_prod_cols if col not in prod.columns]

    if missing_prod_cols:
        st.error(f"Input Error: The 'Production' sheet is missing the required columns: {', '.join(missing_prod_cols)}. Please check your Excel column headers for typos!")
        st.stop()
    # ------------------------------------------------------------------

    # ... (Rest of the calculation code continues below) ...


    # --- Input Validation Check (Robustness) ---
    required_prod_cols = ["p", "Np", "Gp", "Bo", "Bg", "Rs"]
    missing_prod_cols = [col for col in required_prod_cols if col not in prod.columns]

    if missing_prod_cols:
        st.error(f"Input Error: The 'Production' sheet is missing the required columns: {', '.join(missing_prod_cols)}. Please check your Excel column headers for typos!")
        st.stop()
    # --------------------------------------------------

    # Display Initial Parameters in Sidebar
    st.sidebar.subheader("Initial Parameters Used:")
    st.sidebar.metric("Initial $B_{oi}$ (bbl/STB)", f"{Boi:.4f}")
    st.sidebar.metric("Initial $R_{si}$ (SCF/STB)", f"{Rsi:,.0f}")
    st.sidebar.markdown("---")


    # --- Material Balance Calculations (F = N * Eo + G * Eg) ---
    prod["Eo"] = prod["Bo"] - Boi + (prod["Rs"] - Rsi) * prod["Bg"]
    prod["Eg"] = prod["Bg"] - Bgi
    prod["F"]  = prod["Np"] * (prod["Bo"] - Boi) + (prod["Gp"] - prod["Np"] * Rsi) * prod["Bg"]

    # Calculate X and Y for the straight line (Y = N*X + G)
    prod["x"] = prod["Eo"] / prod["Eg"]
    prod["y"] = prod["F"] / prod["Eg"]

    # Handle division by zero/inf values (typically the initial pressure point)
    prod_clean = prod.replace([np.inf, -np.inf], np.nan).dropna()

    
    # --- Linear Regression (Straight-Line Fit) ---
    if len(prod_clean) > 1:
        coeffs = np.polyfit(prod_clean["x"], prod_clean["y"], 1)
        N, G = coeffs[0], coeffs[1]
        m = (G * Bgi) / (N * Boi)

        # Calculate R-squared for goodness of fit
        y_fit = N * prod_clean["x"] + G
        ss_total = ((prod_clean["y"] - prod_clean["y"].mean()) ** 2).sum()
        ss_residual = ((prod_clean["y"] - y_fit) ** 2).sum()
        R_squared = 1 - (ss_residual / ss_total)

        # --- Display Results ---
        st.header("📈 Analysis Results")
        
        # Use columns for a neat presentation of metrics
        col_N, col_G, col_m, col_R2 = st.columns(4)

        with col_N:
            # Assumes Np and Gp were given in MMSTB and MMMSCF, making N and G in those units.
            st.metric("Initial Oil in Place (N)", f"{N:,.2f} MMSTB")
        with col_G:
            st.metric("Initial Gas in Place (G)", f"{G:,.2f} MMMSCF")
        with col_m:
            st.metric("Gas Cap Ratio (m)", f"{m:.4f} (fraction)")
        with col_R2:
            st.metric("Goodness of Fit ($R^2$)", f"{R_squared:.4f}")

        st.markdown("---")
        
        # Display the fitted equation (using LaTeX for high quality)
        st.subheader("Havlena–Odeh Equation and Fit")
        st.latex(r'F = N E_o + G E_g \quad \Rightarrow \quad \frac{F}{E_g} = N \frac{E_o}{E_g} + G')
        st.markdown(f"""
            The resulting straight-line fit equation is:
            $$ Y = ({N:,.2f}) X + ({G:,.2f}) $$
        """)
        st.markdown("---")


        # --- Interactive Plot with Residuals (Bonus Feature) ---
        st.header("📊 Havlena–Odeh Straight-Line Plot")
        
        # Create a subplot for the main plot and residuals plot
        fig = make_subplots(rows=2, cols=1, 
                            row_heights=[0.8, 0.2], 
                            shared_xaxes=True, 
                            vertical_spacing=0.1,
                            subplot_titles=(r'Havlena–Odeh Plot: $\frac{F}{E_g}$ vs $\frac{E_o}{E_g}$', 'Residuals Analysis'))

        # 1. Main Plot
        fig.add_trace(go.Scatter(x=prod_clean["x"], y=prod_clean["y"], mode="markers", 
                                 name="Data Points", marker=dict(size=8, color='blue')),
                      row=1, col=1)
        
        # Add the fitted line
        fig.add_trace(go.Scatter(x=prod_clean["x"], y=y_fit, mode="lines", 
                                 name=f"Linear Fit", line=dict(color='red')),
                      row=1, col=1)
        
        # Labeling the main plot axes
        fig.update_yaxes(title_text=r"$\frac{F}{E_g}$", row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=1, col=1) # Hide X-ticks on top plot

        # 2. Residuals Plot
        residuals = prod_clean["y"] - y_fit
        fig.add_trace(go.Scatter(x=prod_clean["x"], y=residuals, mode='markers', 
                                 name='Residuals', marker=dict(size=5, color='green')),
                      row=2, col=1)
        
        # Add zero line for residuals
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        
        # Labeling the residuals plot axes
        fig.update_yaxes(title_text="Residuals", row=2, col=1)
        fig.update_xaxes(title_text=r"$\frac{E_o}{E_g}$ (X-Axis)", row=2, col=1)
        
        fig.update_layout(height=600, showlegend=True, title_text="Havlena-Odeh Analysis Plot", hovermode="x unified")
        
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # --- Display Data for Transparency ---
        st.header("🔍 Supporting Data Tables")
        
        # Display the calculated intermediate variables
        st.subheader("Calculated Variables ($F, E_o, E_g$) and Plot Data ($X, Y$)")
        display_cols = ['p', 'Np', 'Gp', 'F', 'Eo', 'Eg', 'x', 'y']
        
        # Use prod_clean for display (Fixes the KeyError)
        st.dataframe(prod_clean[display_cols].style.format(precision=4)) 

        st.subheader("Input Production Data (First 5 Rows)")
        st.dataframe(prod.head(5))

    else:
        st.warning("Not enough clean data points (at least 2) remaining after filtering to perform linear regression. Check the data in your Excel file.")

else:
    st.info("Upload an Excel file to start the Havlena-Odeh analysis.")
