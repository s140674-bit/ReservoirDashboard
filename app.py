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
        background-color: var(--secondary-background) !important;
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
    - **Swc** - Cannot water saturation
    - **Cf** - formation compressibility
    - **Cw** - water comperssibility
    """)

st.markdown("---")

st.info("""
**Note:** 
- Accuracy depends on PVT and production data quality.
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
           * **Required Columns:** `p`, `Np`, `Gp`, `Bo`, `Bg`, `Rs`. (Using uppercase P for maximum compatibility with your data)
        2. **'Initial' Sheet:** Contains initial reservoir parameters.
           * **Required Parameters (Parameter, Value):** Must include `Boi`, `Bgi`, `Rsi`.
    """)


if uploaded:
    # --- Data Loading and Initial Parameter Processing ---
    try:
        prod = pd.read_excel(uploaded, sheet_name="Production")
        init_df = pd.read_excel(uploaded, sheet_name="Initial")
        
        # --- FIXES for Robustness (Addresses all previous KeyErrors/crashes) ---
        # 1. Strip whitespace from all column names (Solves hidden space issue)
        prod.columns = prod.columns.str.strip() 
        # 2. Drop columns that are entirely NaN (e.g., blank columns)
        prod = prod.dropna(axis=1, how='all')
        # 3. Convert numeric columns to numeric types (handles string values)
        numeric_cols = ["p", "Np", "Gp", "Bo", "Bg", "Rs"]
        for col in numeric_cols:
            if col in prod.columns:
                prod[col] = pd.to_numeric(prod[col], errors='coerce')
        # -----------------------------------------------------------------------

        init = pd.Series(init_df["Value"].values, index=init_df["Parameter"].values)
        
        # Convert initial parameters to numeric
        Boi = pd.to_numeric(init["Boi"], errors='coerce')
        Bgi = pd.to_numeric(init["Bgi"], errors='coerce')
        Rsi = pd.to_numeric(init["Rsi"], errors='coerce')
        Cw = pd.to_numeric(init["Cw"], errors='coerce')
        Cf = pd.to_numeric(init["Cf"], errors='coerce')
        Swc = pd.to_numeric(init["Swc"], errors='coerce')
        
        # Check if conversion was successful
        if pd.isna(Boi) or pd.isna(Bgi) or pd.isna(Rsi):
            st.error("Error: Initial parameters (Boi, Bgi, Rsi) must be numeric values.")
            st.stop()
        if pd.isna(Cw) or pd.isna(Cf) or pd.isna(Swc):
            st.error("Error: Initial parameters (Cw, Cf, Swc) must be numeric values.")
            st.stop()

    except Exception as e:
        st.error(f"Error loading data. Check your sheet names ('Production', 'Initial') or Initial parameters ('Boi', 'Bgi', 'Rsi'). Details: {e}")
        st.stop()


    # --- Input Validation Check (Using robust uppercase 'P') ---
    required_prod_cols = ["p", "Np", "Gp", "Bo", "Bg", "Rs"]
    missing_prod_cols = [col for col in required_prod_cols if col not in prod.columns]

    if missing_prod_cols:
        st.error(f"Input Error: The 'Production' sheet is missing the required columns: {', '.join(missing_prod_cols)}. Please check your Excel column headers for typos!")
        st.stop()
    # ------------------------------------------------------------------

    # Display Initial Parameters in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Initial Parameters Used:")
    st.sidebar.metric("Initial $B_{oi}$ (bbl/STB)", f"{Boi:.4f}")
    st.sidebar.metric("Initial $R_{si}$ (SCF/STB)", f"{Rsi:,.0f}")
    st.sidebar.markdown("---")


    # --- Material Balance Calculations (F = N * Eo + G * Eg +Efw) ---
    # ---Water & formation compressibilityterm(Efw)---
    #load extra parameters
    Swc = float(init.get("Swc", 0))
    Cw = float(init.get("Cw", 0))
    Cf = float(init.get("Cf", 0))
    #calculate deltaP
    Pi = prod["p"].iloc[0]
    prod["dP"] = Pi - prod["p"]
    prod["Efw"] = ((Cw * Swc)+ Cf) / (1- Swc) * (prod["p"].iloc[0] - (prod["p"]))
    prod["Eo"] = prod["Bo"] - Boi + (prod["Rs"] - Rsi) * prod["Bg"]
    prod["Eg"] = prod["Bg"] - Bgi
    prod["F"] = prod["Np"] * (prod["Bo"] - Boi) + (prod["Gp"] - prod["Np"] * Rsi) * prod["Bg"]

    # Calculate X and Y for the straight line (Y = N*X + G)
    prod["x"] = (prod["Eg"] + prod["Efw"])/ (prod["Eo"] + prod["Efw"])
    prod["y"] = prod["F"] / (prod["Eo"] + prod["Efw"])

    # Handle division by zero/inf values
    prod_clean = prod.replace([np.inf, -np.inf], np.nan).dropna()

    
    # --- Linear Regression (Straight-Line Fit) ---
   # --- Linear Regression (Straight-Line Fit Using High-Pressure Points Only) ---
if len(prod_clean) > 1:

    # Select first 5–6 points only (straight-line region)
    reg_data = prod_clean.sort_values("p", ascending=False).iloc[:6]

    coeffs = np.polyfit(reg_data["x"], reg_data["y"], 1)

    Nm = coeffs[0]     # slope = N*m
    N  = coeffs[1]     # intercept = N
    m  = Nm / N
    G  = N * m * (Boi / Bgi)

    # Calculate R-squared
    y_fit = Nm * reg_data["x"] + N
    ss_total = ((reg_data["y"] - reg_data["y"].mean()) ** 2).sum()
    ss_residual = ((reg_data["y"] - y_fit) ** 2).sum()
    R_squared = 1 - ss_residual / ss_total
        
        # --- Display Results in Tabs (Major Improvement for Organization) ---
        st.header("📈 Analysis Results and Visualizations")
        tab1, tab2, tab3 = st.tabs(["📊 Regression Plot", "📚 Supporting Data", "📝 Equations & Metrics"])


        # --- Tab 3: Equations & Metrics ---
        with tab3:
            st.subheader("Final Calculated Parameters")
            # Use columns for a neat presentation of metrics
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
            st.subheader("Havlena–Odeh Equation and Fit")
            st.latex(r"\frac{F}{E_o+E_{fw}} = N + Nm \frac{E_g+E_{fw}}{E_o+E_{fw}}")
            st.markdown(f"""
                The resulting straight-line fit equation is:
                $$ Y = ({N:,.2f}) X + ({Nm:,.2f}) $$
            """)


        # --- Tab 1: Interactive Plot with Residuals (Custom Colors/Shapes/Hover Data) ---
        with tab1:
            st.subheader("Havlena–Odeh Straight-Line Plot (F / (Eo + Efw) vs (Eg + Efw) / (Eo + Efw))")
            
            fig = make_subplots(rows=2, cols=1, 
                                row_heights=[0.8, 0.2], 
                                shared_xaxes=True, 
                                vertical_spacing=0.1,
                                subplot_titles=(r'Main Plot: $\frac{F}{E_{fw}+E_o}$ vs $\frac{E_g+E_{fw}}{E_{fw}+E_o}$',
                                        'Residuals Analysis'))
                                
            # 1. Main Plot
            fig.add_trace(go.Scatter(
                x=prod_clean["x"], 
                y=prod_clean["y"], 
                mode="markers", 
                name="Production Data", 
                marker=dict(
                    size=8, 
                    color='#E69F00', # Gold/Oil color
                    symbol='circle-open' 
                ),
                # Show Pressure and Np when hovering (High Interactivity Bonus!)
                hovertemplate="<b>P:</b> %{customdata[0]:,.0f} psia<br><b>Np:</b> %{customdata[1]:,.2f} MMSTB<br><b>X:</b> %{x:.4f}<br><b>Y:</b> %{y:.4f}<extra></extra>",
                customdata=prod_clean[['p', 'Np']] 
                ),
                row=1, col=1)
            
            # Add the fitted line
            fig.add_trace(go.Scatter(
                x=prod_clean["x"], 
                y=y_fit, 
                mode="lines", 
                name=f"Linear Fit", 
                line=dict(color='#0072B2', width=3) # Deep Blue for the line
                ),
                row=1, col=1)
            
            # Labeling the main plot axes
            fig.update_yaxes(title_text=r"$\frac{F}{E_o + E_{fw}}$", row=1, col=1)
            fig.update_xaxes(showticklabels=False, row=1, col=1) 

            # 2. Residuals Plot (Custom Coloring based on sign)
            residuals = prod_clean["y"] - y_fit
            residual_color = np.where(residuals >= 0, '#0072B2', '#D55E00') # Blue for positive, Orange for negative
            
            fig.add_trace(go.Scatter(x=prod_clean["x"], y=residuals, mode='markers', 
                                     name='Residuals', 
                                     marker=dict(size=6, color=residual_color)),
                          row=2, col=1)
            
            # Add zero line for residuals
            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
            
            # Labeling the residuals plot axes
            fig.update_yaxes(title_text="Residuals", row=2, col=1)
            fig.update_xaxes(title_text=r"$\frac{E_g + E_{fw}}{E_o + E_{fw}}$ (X-Axis)", row=2, col=1)
            
            fig.update_layout(height=600, showlegend=True, hovermode="x unified")
            
            st.plotly_chart(fig, ues_container_width=True)

        # --- Tab 2: Supporting Data Tables ---
        with tab2:
            st.subheader("Calculated Variables ($F, E_o, E_g, E_{fw}$) and Plot Data ($X, Y$)")
            display_cols = ['p', 'Np', 'Gp', 'F', 'Eo', 'Eg', 'Efw', 'x' , 'y']
            
            # Use prod_clean for display
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

