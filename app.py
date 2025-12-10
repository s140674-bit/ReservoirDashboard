


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
        
        # Check if conversion was successful
        if pd.isna(Boi) or pd.isna(Bgi) or pd.isna(Rsi):
            st.error("Error: Initial parameters (Boi, Bgi, Rsi) must be numeric values.")
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


    # --- Material Balance Calculations (F = N * Eo + G * Eg) ---
    prod["Eo"] = prod["Bo"] - Boi + (prod["Rs"] - Rsi) * prod["Bg"]
    prod["Eg"] = prod["Bg"] - Bgi
    prod["F"]  = prod["Np"] * (prod["Bo"] - Boi) + (prod["Gp"] - prod["Np"] * Rsi) * prod["Bg"]

    # Calculate X and Y for the straight line (Y = N*X + G)
    prod["x"] = prod["Eo"] / prod["Eg"]
    prod["y"] = prod["F"] / prod["Eg"]

    # Handle division by zero/inf values
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
            st.latex(r'F = N E_o + G E_g \quad \Rightarrow \quad \frac{F}{E_g} = N \frac{E_o}{E_g} + G')
            st.markdown(f"""
                The resulting straight-line fit equation is:
                $$ Y = ({N:,.2f}) X + ({G:,.2f}) $$
            """)


        # --- Tab 1: Interactive Plot with Residuals (Custom Colors/Shapes/Hover Data) ---
        with tab1:
            st.subheader("Havlena–Odeh Straight-Line Plot (F/Eg vs Eo/Eg)")
            
            fig = make_subplots(rows=2, cols=1, 
                                row_heights=[0.8, 0.2], 
                                shared_xaxes=True, 
                                vertical_spacing=0.1,
                                subplot_titles=(r'Main Plot: $\frac{F}{E_g}$ vs $\frac{E_o}{E_g}$', 'Residuals Analysis'))

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
            fig.update_yaxes(title_text=r"$\frac{F}{E_g}$", row=1, col=1)
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
            fig.update_xaxes(title_text=r"$\frac{E_o}{E_g}$ (X-Axis)", row=2, col=1)
            
            fig.update_layout(height=600, showlegend=True, hovermode="x unified")
            
            st.plotly_chart(fig, width='stretch')

        # --- Tab 2: Supporting Data Tables ---
        with tab2:
            st.subheader("Calculated Variables ($F, E_o, E_g$) and Plot Data ($X, Y$)")
            display_cols = ['p', 'Np', 'Gp', 'F', 'Eo', 'Eg', 'x', 'y']
            
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
