import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Configuration ---
st.set_page_config(page_title="Reservoir Dashboard", layout="wide")

# Add custom CSS for theme and smaller unit fonts
st.markdown("""
<style>
    /* Theme Colors: White and #f6bf0c */
    :root {
        --primary-color: #f6bf0c;
        --background-color: #ffffff;
        --secondary-background: #f8f9fa;
        --text-color: #262730;
    }
    
    /* Main background */
    .stApp {
        background-color: var(--background-color) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background) !important;
        border-right: 2px solid var(--primary-color) !important;
    }
    
    /* Sidebar header */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        color: var(--primary-color) !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: var(--background-color) !important;
        padding-top: 2rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-color) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #e0ab0a !important;
        color: #000000 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background) !Important;
        color: var(--text-color) !important;
        border-radius: 5px 5px 0 0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: var(--secondary-background) !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        border-left: 4px solid var(--primary-color) !important;
    }
    
    /* Make metric values smaller - this affects both numbers and units */
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        line-height: 1.2 !important;
        color: var(--text-color) !important;
    }
    
    /* Make metric labels smaller */
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        color: var(--text-color) !important;
    }
    
    /* Additional styling for metric delta (if any) */
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }
    
    /* Target sidebar metrics specifically for smaller units */
    .sidebar [data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: var(--secondary-background) !important;
        border: 2px dashed var(--primary-color) !important;
        border-radius: 8px !important;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background-color: var(--secondary-background) !important;
        border: 1px solid var(--primary-color) !important;
        border-radius: 5px !important;
    }
    
    [data-testid="stExpander"] summary {
        color: var(--primary-color) !important;
        font-weight: 600 !important;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        background-color: var(--background-color) !important;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        border-left: 4px solid var(--primary-color) !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: var(--text-color) !important;
    }
    
    /* Horizontal rule */
    hr {
        border-color: var(--primary-color) !important;
        opacity: 0.3;
    }
    
    /* Selectbox and other inputs */
    [data-baseweb="select"] {
        border-color: var(--primary-color) !important;
    }
    
    /* Focus states */
    *:focus {
        outline-color: var(--primary-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Title/Header
st.sidebar.title("🛢 Havlena–Odeh Analysis") 
st.sidebar.markdown("---")
st.title("Reservoir Material Balance Dashboard")
st.markdown("""
This dashboard is an interactive analytical tool designed to perform Havlena-Odeh material balance calculations for reservoir engineering applications.
""")

st.markdown("---")

st.subheader("📊 What This Dashboard Provides")
st.markdown("""
Provides estimations of:
- **Original oil in place**
- **Gas cap in place**
- **Gas cap ratio**
""")

st.markdown("---")

st.subheader("📥 Input Requirements")
st.markdown("""
Upload an Excel file (.xlsx) containing **2 sheets**.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Sheet 1: **"Production"** (Required Columns)
    - **Bo** - Oil FVF  
    - **Bg** - Gas FVF  
    - **Rs** - Solution GOR  
    - **Np** - Cumulative oil production  
    - **Gp** - Cumulative gas production  
    - **p** - Reservoir pressure
        """)


with col2:
    st.markdown("""
    #### Sheet 2: **"Initial"** (Required Parameters)
    - **Boi** - Initial oil FVF  
    - **Bgi** - Initial gas FVF  
    - **Rsi** - Initial solution GOR  
    - **Swc** - Connate water saturation  
    - **Cf** - Formation compressibility  
    - **Cw** - Water compressibility  
    - **Pi** - Initial pressure
    """)

st.markdown("---")

st.info("""
**Note:** 
- Accuracy depends on PVT and production data quality, some values may appear with an error due to the unaccounted water influx in this model.
- The assigned sheets structure **MUST** be followed specifically, including capital and small letters such as **p** in production sheet, to avoid errors.
""")

st.markdown("---")


# --- Sidebar for Input and Guide ---
st.sidebar.header("📥 Data Upload and Instructions")
uploaded = st.sidebar.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

with st.sidebar.expander("📝 User Guide: Excel File Format"):
    st.markdown("""
        The uploaded Excel file **must** contain two sheets:
        1. **'Production' Sheet:** Contains time-dependent PVT and production data.  
           * **Required Columns:** `p`, `Np`, `Gp`, `Bo`, `Bg`, `Rs`.  
        2. **'Initial' Sheet:** Contains initial reservoir parameters.  
           * **Required Parameters (Parameter, Value):** `Boi`, `Bgi`, `Rsi`, `Swc`, `Cf`, `Cw`, `Pi`.
    """)


if uploaded:
    # --- Data Loading and Initial Parameter Processing ---
    try:
        prod = pd.read_excel(uploaded, sheet_name="Production")
        init_df = pd.read_excel(uploaded, sheet_name="Initial")
        
        # Clean production sheet
        prod.columns = prod.columns.str.strip()
        prod = prod.dropna(axis=1, how="all")
        numeric_cols = ["p", "Np", "Gp", "Bo", "Bg", "Rs"]
        for col in numeric_cols:
            if col in prod.columns:
                prod[col] = pd.to_numeric(prod[col], errors="coerce")

        # Clean initial sheet and make parameters case-insensitive
        init_df.columns = init_df.columns.str.strip()
        parameters = init_df["Parameter"].str.strip().str.lower()
        values = init_df["Value"]
        init = pd.Series(values.values, index=parameters.values)

        def to_float(x):
            if isinstance(x, str):
                x = x.replace("−", "-")
            return float(x)

        Boi = to_float(init["boi"])
        Bgi = to_float(init["bgi"])
        Rsi = to_float(init["rsi"])
        Pi  = to_float(init.get("pi", prod["p"].iloc[0]))
        Swc = to_float(init["swc"])
        Cf  = to_float(init["cf"])
        Cw  = to_float(init["cw"])

    except Exception as e:
        st.error(f"Error loading data. Check your 'Production' and 'Initial' sheets and parameters. Details: {e}")
        st.stop()

    # --- Input Validation Check ---
    required_prod_cols = ["p", "Np", "Gp", "Bo", "Bg", "Rs"]
    missing_prod_cols = [col for col in required_prod_cols if col not in prod.columns]

    if missing_prod_cols:
        st.error(f"Input Error: The 'Production' sheet is missing the required columns: {', '.join(missing_prod_cols)}. Please check your Excel column headers for typos!")
        st.stop()

    # Display Initial Parameters in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Initial Parameters Used:")
    st.sidebar.metric("Initial $B_{oi}$ (bbl/STB)", f"{Boi:.4f}")
    st.sidebar.metric("Initial $R_{si}$ (SCF/STB)", f"{Rsi:,.0f}")
    st.sidebar.metric("Initial $P_i$ (psia)", f"{Pi:,.0f}")
    st.sidebar.markdown("---")

    # --- Material Balance Calculations (Corrected) ---

    # ΔP = Pi - P  (pressure drop)
    prod["dP"] = Pi - prod["p"]

    # Efw term: rock + water compressibility
    prod["Efw"] = Boi * ((Cf + Cw * Swc) / (1.0 - Swc)) * prod["dP"]

    # Eo term: oil expansion + liberated solution gas
    prod["Eo"] = (prod["Bo"] - Boi) + (Rsi - prod["Rs"]) * prod["Bg"]

    # Eg term: gas-cap gas expansion (simple form)
    prod["Eg"] = prod["Bg"] - Bgi

    # Rp (production GOR)
    prod["Rp"] = prod["Gp"] / prod["Np"]
    prod["Rp"] = prod["Rp"].replace([np.inf, -np.inf], np.nan).fillna(0)

    # F term (cumulative underground withdrawal)
    prod["F"] = prod["Np"] * prod["Bo"] + (prod["Gp"] - prod["Np"] * prod["Rs"]) * prod["Bg"]
    # Havlena–Odeh straight-line variables
    denom = prod["Eo"] + prod["Efw"]
    prod["x"] = prod["Eg"] / denom
    prod["y"] = prod["F"] / denom

    # Clean data for regression and plotting
    prod_clean = prod.replace([np.inf, -np.inf], np.nan).dropna()

    # --- Linear Regression (Straight-Line Fit) ---
    if len(prod_clean) > 1:
        reg_data = prod_clean.sort_values("x", ascending=True).iloc[-6:]
       # --- Straight-Line Fit (Polyfit) ---
        coeffs = np.polyfit(reg_data["x"], reg_data["y"], 1)
        Nm = coeffs[0]          # slope
        N = coeffs[1]           # intercept
        m = Nm / N              # gas-cap ratio
        G = N * m * (Boi / Bgi) # gas in place estimate

        # --- Detect if Gas Cap Physically Exists ---
        if m < 0:
            m = 0
            G = 0
            flat_case = True
            gas_status = "No gas cap detected — reservoir is undersaturated"
        else:
            flat_case = False
            gas_status = "Gas cap present"

        # --- Choose the Correct Line Fit ---
        if flat_case:
          # Flat line at N ONLY
            y_fit = np.full_like(prod_clean["x"], N)
            R_squared = 1.0  # perfect match for undersaturated reservoir
        else:
            y_fit = Nm * prod_clean["x"] + N
            ss_total = ((prod_clean["y"] - prod_clean["y"].mean()) ** 2).sum()
            ss_residual = ((prod_clean["y"] - y_fit) ** 2).sum()
            R_squared = 1 - (ss_residual / ss_total)

        st.header("📈 Analysis Results and Visualizations")
        tab1, tab2, tab3 = st.tabs(["📊 Regression Plot", "📚 Supporting Data", "📝 Equations & Metrics"])

        # Tab 3: Equations & Metrics
        with tab3:
            st.subheader("Final Calculated Parameters")
            col_N, col_G, col_m, col_R2 = st.columns(4)

            with col_N:
                st.metric("Oil in Place (N)", f"{N:,.2f} MMSTB")
            with col_G:
                st.metric("Gas in Place (G)", f"{G:,.2f} MMMSCF")
            with col_m:
                st.metric("Gas Cap Ratio (m)", f"{m:.4f}")
            with col_R2:
                st.metric("Goodness of Fit ($R^2$)", f"{R_squared:.4f}")

            st.markdown("---")
            st.info(gas_status)
            st.subheader("Havlena–Odeh Equation and Fit")
            st.latex(r'\\frac{F}{E_o+E_{fw}} = N + mN \\frac{E_g}{E_o+E_{fw}}')
            st.markdown(f"""
                The resulting straight-line fit equation is:
                $$ Y = ({Nm:,.2f}) X + ({N:,.2f}) $$
            """)

        # Tab 1: Regression Plot
        with tab1:
            st.subheader(r"Havlena–Odeh Straight-Line Plot F/(E_o+E_{fw}) vs E_g/(E_o+E_{fw})")
            
            fig = make_subplots(rows=2, cols=1, 
                                row_heights=[0.8, 0.2], 
                                shared_xaxes=True, 
                                vertical_spacing=0.1,
                                subplot_titles=("Main Plot", "Residuals"))

            fig.add_trace(go.Scatter(
                x=prod_clean["x"],
                y=prod_clean["y"],
                mode="markers",
                name="Production Data",
                marker=dict(
                    size=8,
                    color="#E69F00",
                    symbol="circle-open"
                ),
                hovertemplate="<b>P:</b> %{customdata[0]:,.0f} psia<br><b>Np:</b> %{customdata[1]:,.2f} STB<br><b>X:</b> %{x:.4f}<br><b>Y:</b> %{y:.4f}<extra></extra>",
                customdata=prod_clean[["p", "Np"]]
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=prod_clean["x"],
                y=y_fit,
                mode="lines",
                name="Linear Fit",
                line=dict(color="#0072B2", width=3)
            ), row=1, col=1)

            fig.update_yaxes(title_text="F / (Eo + Efw)", row=1, col=1)
            fig.update_xaxes(showticklabels=False, row=1, col=1)

            residuals = prod_clean["y"] - y_fit
            residual_color = np.where(residuals >= 0, "#0072B2", "#D55E00")

            fig.add_trace(go.Scatter(
                x=prod_clean["x"],
                y=residuals,
                mode="markers",
                name="Residuals",
                marker=dict(size=6, color=residual_color)
            ), row=2, col=1)

            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
            fig.update_yaxes(title_text="Residuals", row=2, col=1)
            fig.update_xaxes(title_text="E_g / (E_o + E_fw)", row=2, col=1)

            fig.update_layout(height=600, showlegend=True, hovermode="x unified")

            st.plotly_chart(fig, use_container_width=True)

        # Tab 2: Supporting Data
        with tab2:
            st.subheader("Calculated Variables and Plot Data")
            display_cols = ['p', 'Np', 'Gp', 'Rp', 'F', 'Eo', 'Eg', 'Efw', 'x', 'y']
            if not prod_clean.empty:
                st.dataframe(prod_clean[display_cols].style.format(precision=4))
                st.subheader("Input Production Data (First 5 Rows)")
                st.dataframe(prod.head(5))
            else:
                st.warning("No clean data points to display.")
    else:
        st.warning("Not enough clean data points (at least 2) remaining after filtering to perform linear regression. Check the data in your Excel file.")
else:
    st.info("Upload an Excel file to start the Havlena-Odeh analysis.")
