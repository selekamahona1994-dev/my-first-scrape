import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Global ESG Gap Tracker", layout="wide", page_icon="🌍")

# Initialize Search History
if 'history' not in st.session_state:
    st.session_state.history = []


# --- 2. DATA FETCHING LOGIC ---
def fetch_world_bank_data(country_code, indicator):
    if not country_code or len(country_code) < 2:
        return None, None

    # per_page=50 ensures we look back deep enough into history
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=50"

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Handle API errors or empty results
            if isinstance(data[0], dict) and 'message' in data[0]:
                return None, None
            if len(data) > 1 and isinstance(data[1], list):
                for entry in data[1]:
                    if entry['value'] is not None:
                        return round(entry['value'], 2), entry['date']
    except Exception:
        pass
    return None, None


# --- 3. SIDEBAR: SEARCH SETTINGS ---
with st.sidebar:
    st.header("🌍 Global Search")
    st.write("Enter 2-letter codes (e.g., US, TZ, IN, CN).")

    c1 = st.text_input("First Country Code", "US").upper().strip()
    c2 = st.text_input("Second Country Code", "TZ").upper().strip()

    metrics = {
        "CO2 Emissions (Metric Tons Per Capita)": "EN.ATM.CO2E.PC",
        "Renewable Energy Share (% of Total)": "EG.ELC.RNEW.ZS",
        "Forest Area (% of Total Land)": "AG.LND.FRST.ZS"
    }
    selected_metric = st.selectbox("Select ESG Metric", list(metrics.keys()))
    indicator_code = metrics[selected_metric]

    # Dynamic target goal setting
    default_target = 0.0 if "CO2" in selected_metric else 80.0
    target_val = st.number_input("Sustainable Target Goal", value=default_target)

    st.divider()
    st.subheader("📜 Search History")
    for item in st.session_state.history[-5:]:
        st.caption(f"• {item}")

# --- 4. MAIN INTERFACE ---
st.title("🌱 Sustainability & ESG Gap Analysis Tool")
st.markdown("This tool calculates the **Sustainability Gap** and visualizes it on a global scale.")

if st.button("Run Global Analysis"):
    if not c1 or not c2:
        st.error("⚠️ Please enter both country codes before analyzing.")
    else:
        with st.spinner('Querying World Bank Global Database...'):
            v1, y1 = fetch_world_bank_data(c1, indicator_code)
            v2, y2 = fetch_world_bank_data(c2, indicator_code)

        if v1 is not None and v2 is not None:
            # Update History
            search_key = f"{c1} vs {c2} ({selected_metric})"
            if search_key not in st.session_state.history:
                st.session_state.history.append(search_key)

            # --- SECTION 1: KEY METRICS ---
            col1, col2 = st.columns(2)
            gap1 = round(v1 - target_val, 2)
            gap2 = round(v2 - target_val, 2)

            # Inverse color for CO2 (negative gap is good), normal for others
            d_color = "inverse" if "CO2" in selected_metric else "normal"

            col1.metric(f"{c1} ({y1})", v1, delta=gap1, delta_color=d_color)
            col2.metric(f"{c2} ({y2})", v2, delta=gap2, delta_color=d_color)

            # --- SECTION 2: THE MAP ---
            st.divider()
            st.subheader("🗺️ Global Gap Map")

            map_df = pd.DataFrame({
                'CountryCode': [c1, c2],
                'MetricValue': [v1, v2],
                'Gap': [gap1, gap2]
            })

            fig_map = px.choropleth(
                map_df,
                locations="CountryCode",
                color="Gap",
                hover_name="CountryCode",
                hover_data=["MetricValue", "Gap"],
                color_continuous_scale=px.colors.sequential.Reds if "CO2" in selected_metric else px.colors.sequential.Greens,
                projection="natural earth",
                title=f"Regional Gap Analysis: {selected_metric}"
            )

            fig_map.update_geos(showcountries=True, countrycolor="LightGrey")
            st.plotly_chart(fig_map, use_container_width=True)

            # --- SECTION 3: STATISTICAL CHART & DOWNLOAD ---
            st.divider()
            col_chart, col_down = st.columns([2, 1])

            with col_chart:
                st.subheader("📊 Bar Comparison")
                fig_bar, ax = plt.subplots(figsize=(10, 5))
                ax.bar([c1, c2, "Target"], [v1, v2, target_val], color=['#3498db', '#e67e22', '#2ecc71'])
                ax.set_ylabel(selected_metric)
                st.pyplot(fig_bar)

            with col_down:
                st.subheader("📥 Download Data")
                # Create DataFrame for CSV
                export_df = pd.DataFrame({
                    "Country": [c1, c2],
                    "Year": [y1, y2],
                    "Metric": [selected_metric, selected_metric],
                    "Value": [v1, v2],
                    "Target": [target_val, target_val],
                    "Gap": [gap1, gap2]
                })

                csv = export_df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name=f"esg_report_{c1}_{c2}.csv",
                    mime="text/csv",
                )
                st.write("The CSV includes the current data values, target goals, and calculated gaps.")

        else:
            if v1 is None: st.error(f"❌ Could not find data for '{c1}'.")
            if v2 is None: st.error(f"❌ Could not find data for '{c2}'.")
            st.warning("Hint: Try common codes like US, IN, CN, DE, or BR.")

st.divider()
st.info("💡 Data is provided by the World Bank. Mapping powered by Plotly.")