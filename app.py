import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page configuration must be the absolute first streamlit command
st.set_page_config(page_title="Football Player Height Comparison", layout="wide")
st.title("⚽ Professional Footballer Height Visualization")
st.markdown("Compare and analyze professional football player heights across different nations.")

# 2. Data Fetching and Parsing from the CORRECT repository
@st.cache_data
def load_player_data():
    # Points to the actual player profile data repository, using the correct raw sub-domain
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
        
        # Check for Country headers
        if line.startswith('='):
            current_country = line.replace('=', '').strip()
            continue
        
        # Parse player attributes: Name, Position, Height, Birthdate
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 3:
            name = parts[0]
            position = parts[1]
            height_str = parts[2]
            
            # Map position letters to expanded words
            pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                       'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                       'F': 'Forward', 'FW': 'Forward'}
            clean_position = pos_map.get(position.upper(), position)
            
            try:
                # Convert "1.82 m" string directly to a sortable float metric
                height_val = float(height_str.replace('m', '').strip())
                parsed_players.append({
                    "Name": name,
                    "Country": current_country,
                    "Position": clean_position,
                    "Height (m)": height_val
                })
            except ValueError:
                continue

    return pd.DataFrame(parsed_players)

df = load_player_data()

if df.empty:
    st.warning("No dataset loaded. Check repository connection.")
else:
    # Sidebar Filters
    st.sidebar.header("Filter Roster")
    countries = sorted(df["Country"].unique())
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries[:3])
    
    positions = sorted(df["Position"].unique())
    selected_positions = st.sidebar.multiselect("Select Positions", positions, default=positions)

    # Apply data constraints
    filtered_df = df[df["Country"].isin(selected_countries) & df["Position"].isin(selected_positions)]

    # Dynamic metrics display
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Players Displayed", len(filtered_df))
    col2.metric("Average Height", f"{filtered_df['Height (m)'].mean():.2f} m" if not filtered_df.empty else "N/A")
    col3.metric("Tallest Player", f"{filtered_df['Height (m)'].max():.2f} m" if not filtered_df.empty else "N/A")


    if not filtered_df.empty:
        st.subheader("📊 Height Distributions and Trends")
        
        # Interactive Scatter Plot
        fig_scatter = px.scatter(
            filtered_df,
            x="Position",
            y="Height (m)",
            color="Country",
            hover_data=["Name"],
            title="Player Heights Segmented by Position & Country",
            labels={"Height (m)": "Height in Meters"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Searchable Data Grid
        st.subheader("📋 Searchable Data Registry")
        st.dataframe(filtered_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
    else:
        st.info("Select options in the sidebar to populate dashboard widgets.")
