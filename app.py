import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page configuration must be the absolute first streamlit command
st.set_page_config(page_title="Football Player Height Comparison", layout="wide")
st.title("⚽ Professional Footballer Height Visualization")
st.markdown("Compare and analyze professional football player heights across European nations.")

# 2. Data Fetching and Parsing from individual country folders
@st.cache_data
def load_player_data():
    # List of countries matching the folder names in the openfootball/players repo
    countries = ["england", "france", "germany", "italy", "spain", "netherlands", "portugal"]
    parsed_players = []

    for country in countries:
        # Loop through each country folder to pull its specific squad text file
        url = f"https://githubusercontent.com{country}/squads.txt"
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                # Some repos use different filenames like players.txt instead of squads.txt
                url = f"https://githubusercontent.com{country}/players.txt"
                response = requests.get(url)
                
            if response.status_code == 200:
                lines = response.text.split("\n")
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('=') or line.startswith('#'):
                        continue
                    
                    # Expected line format: Eduardo Camavinga, M, 1.82 m, b. 10 Nov 2002 @ Miconje
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        name = parts[0]
                        position = parts[1]
                        height_str = parts[2]
                        
                        # Clean up shorthand position tags
                        pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                                   'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                                   'F': 'Forward', 'FW': 'Forward'}
                        clean_position = pos_map.get(position.upper(), position)
                        
                        try:
                            # Convert string "1.82 m" to a clear floating point metric
                            height_val = float(height_str.replace('m', '').strip())
                            parsed_players.append({
                                "Name": name,
                                "Country": country.title(),
                                "Position": clean_position,
                                "Height (m)": height_val
                            })
                        except ValueError:
                            continue # Skip row if height numbers are malformed or missing
        except Exception:
            continue # Pass over network glitches or missing national files silently

    return pd.DataFrame(parsed_players)

df = load_player_data()

if df.empty:
    st.error("Could not fetch data from any country folders. Double check repository links.")
else:
    # Sidebar Filtering Options
    st.sidebar.header("Filter Roster")
    available_countries = sorted(df["Country"].unique())
    selected_countries = st.sidebar.multiselect("Select Countries", available_countries, default=available_countries[:3])
    
    available_positions = sorted(df["Position"].unique())
    selected_positions = st.sidebar.multiselect("Select Positions", available_positions, default=available_positions)

    # Filter data matrix
    filtered_df = df[df["Country"].isin(selected_countries) & df["Position"].isin(selected_positions)]

    # Dynamic metrics display
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Players Displayed", len(filtered_df))
    col2.metric("Average Height", f"{filtered_df['Height (m)'].mean():.2f} m" if not filtered_df.empty else "N/A")
    col3.metric("Tallest Player", f"{filtered_df['Height (m)'].max():.2f} m" if not filtered_df.empty else "N/A")

    if not filtered_df.empty:
        st.subheader("📊 Height Distributions and Trends")
        
        # Interactive Scatter Graph Layout
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
        
        # Searchable Data Frame View
        st.subheader("📋 Searchable Data Registry")
        st.dataframe(filtered_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
    else:
        st.info("Select filters in the sidebar menu to populate visualization metrics.")
