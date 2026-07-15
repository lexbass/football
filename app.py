import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration
st.set_page_config(page_title="Football Player Height Comparison", layout="wide")
st.title("⚽ Professional Footballer Height Visualization")
st.markdown("Compare and analyze professional football player heights across different nations.")

# 2. Data Fetching and Parsing
@st.cache_data
def load_player_data():
    # URL to the raw source data in openfootball's player repository
    url = "https://githubusercontent.com"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.split("\n")
    except Exception as e:
        st.error(f"Failed to fetch data from GitHub: {e}")
        return pd.DataFrame()

    parsed_players = []
    current_country = "Unknown"

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect Country headers marked by '=' sign
        if line.startswith('='):
            current_country = line.replace('=', '').strip()
            continue
        
        # Parse individual player rows: Name, Position, Height, DOB @ Place
        # Format example: Eduardo Camavinga, M, 1.82 m, b. 10 Nov 2002 @ Miconje
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 3:
            name = parts[0]
            position = parts[1]
            height_str = parts[2]
            
            # Map shorthand positions to clean labels
            pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                       'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                       'F': 'Forward', 'FW': 'Forward'}
            clean_position = pos_map.get(position.upper(), position)
            
            # Extract and convert height metric
            try:
                height_val = float(height_str.replace('m', '').strip())
                parsed_players.append({
                    "Name": name,
                    "Country": current_country,
                    "Position": clean_position,
                    "Height (m)": height_val
                })
            except ValueError:
                continue # Skip records with missing or mangled height metrics

    return pd.DataFrame(parsed_players)

df = load_player_data()

if df.empty:
    st.warning("No dataset loaded. Check repository connection.")
else:
    # 3. Sidebar Filters
    st.sidebar.header("Filter Roster")
    
    countries = sorted(df["Country"].unique())
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries[:3])
    
    positions = sorted(df["Position"].unique())
    selected_positions = st.sidebar.multiselect("Select Positions", positions, default=positions)

    # Filtering dataframe based on input configuration
    filtered_df = df[df["Country"].isin(selected_countries) & df["Position"].isin(selected_positions)]

    # 4. Main Metrics Displays
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Players Displayed", len(filtered_df))
    col2.metric("Average Height", f"{filtered_df['Height (m)'].mean():.2f} m" if not filtered_df.empty else "N/A")
    col3.metric("Tallest Player", f"{filtered_df['Height (m)'].max():.2f} m" if not filtered_df.empty else "N/A")

    if not filtered_df.empty:
        # 5. Visualizations
        st.subheader("📊 Height Distributions and Trends")
        
        tab1, tab2 = st.tabs(["Interactive Scatter Plot", "Height Distribution Boxplot"])
        
        with tab1:
            fig_scatter = px.scatter(
                filtered_df,
                x="Position",
                y="Height (m)",
                color="Country",
                hover_data=["Name"],
                title="Player Heights Segmented by Position & Country",
                labels={"Height (m)": "Height in Meters"}
            )
            fig_scatter.update_layout(boxmode="group")
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with tab2:
            fig_box = px.box(
                filtered_df,
                x="Country",
                y="Height (m)",
                color="Position",
                title="Height Variation Ranges across Selections",
                labels={"Height (m)": "Height in Meters"}
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # 6. Detailed Data Matrix
        st.subheader("📋 Searchable Data Registry")
        st.dataframe(filtered_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
    else:
        st.info("Select filters in the sidebar to populate data views.")
