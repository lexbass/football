import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration
st.set_page_config(page_title="European Footballer Height Tracker", layout="wide")
st.title("⚽ Professional Footballer Height Visualization")
st.markdown("Compare and analyze comprehensive rosters across top European professional football leagues.")

# 2. Automated Deep Data Scraper via GitHub REST API
@st.cache_data(ttl=86400) # Cache the dataset for 24 hours to prevent API rate limits
def load_all_european_players():
    # Target the API endpoint for the 'europe' folder structure
    api_url = "https://github.com"
    parsed_players = []
    
    try:
        # Step A: Request a registry of all sub-directories (countries)
        response = requests.get(api_url)
        if response.status_code != 200:
            st.error(f"GitHub API Error: {response.status_code}. Using emergency backup dataset.")
            return get_backup_dataset()
            
        items = response.json()
        country_folders = [item["name"] for item in items if item["type"] == "dir"]
        
        # Step B: Loop through every found national folder dynamically
        for country in country_folders:
            # Check for the two common filenames used across this repository
            for filename in ["squads.txt", "players.txt"]:
                raw_url = f"https://githubusercontent.com{country}/{filename}"
                file_res = requests.get(raw_url)
                
                if file_res.status_code == 200:
                    lines = file_res.text.split("\n")
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('=') or line.startswith('#'):
                            continue
                        
                        # Process comma-separated tokens: Name, Position, Height, Birthdate
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 3:
                            name = parts[0]
                            pos_tag = parts[1].upper()
                            height_str = parts[2]
                            
                            # Standardize shorthand position annotations
                            pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                                       'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                                       'F': 'Forward', 'FW': 'Forward'}
                            position = pos_map.get(pos_tag, pos_tag)
                            
                            try:
                                # Convert the text metric into a continuous numeric variable
                                if 'm' in height_str:
                                    height_val = float(height_str.replace('m', '').strip())
                                    parsed_players.append({
                                        "Name": name,
                                        "Country": country.replace('-', ' ').title(),
                                        "Position": position,
                                        "Height (m)": height_val
                                    })
                            except ValueError:
                                continue
                    break # Break file loop if squads.txt or players.txt was successfully processed
                    
    except Exception as e:
        st.error(f"Connection failure: {e}")
        return get_backup_dataset()

    if not parsed_players:
        return get_backup_dataset()
        
    return pd.DataFrame(parsed_players)

def get_backup_dataset():
    # Emergency fallback array to ensure the app functions even if GitHub undergoes maintenance
    fallback = [
        {"Name": "Eduardo Camavinga", "Country": "France", "Position": "Midfielder", "Height (m)": 1.82},
        {"Name": "Kylian Mbappé", "Country": "France", "Position": "Forward", "Height (m)": 1.78},
        {"Name": "Dayot Upamecano", "Country": "France", "Position": "Defender", "Height (m)": 1.88},
        {"Name": "Jude Bellingham", "Country": "England", "Position": "Midfielder", "Height (m)": 1.80},
        {"Name": "Jordan Pickford", "Country": "England", "Position": "Goalkeeper", "Height (m)": 1.85},
        {"Name": "Harry Kane", "Country": "England", "Position": "Forward", "Height (m)": 1.88},
        {"Name": "Manuel Neuer", "Country": "Germany", "Position": "Goalkeeper", "Height (m)": 1.93},
        {"Name": "Jamal Musiala", "Country": "Germany", "Position": "Midfielder", "Height (m)": 1.84},
        {"Name": "Rodri", "Country": "Spain", "Position": "Midfielder", "Height (m)": 1.91},
        {"Name": "Lamine Yamal", "Country": "Spain", "Position": "Forward", "Height (m)": 1.78}
    ]
    return pd.DataFrame(fallback)

df = load_all_european_players()

# 3. Custom Metric Converter Helper
def meters_to_ft_in(m):
    total_inches = m * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}' {inches}\""

# 4. Interactive Dropdown Selection (Side-by-Side View)
st.header("🆚 Head-to-Head Player Comparison")
st.markdown("Select any two players from the comprehensive European registry to compare their height profiles.")

all_player_names = sorted(df["Name"].unique())

select_col1, select_col2 = st.columns(2)
with select_col1:
    p1 = st.selectbox("Select Player 1", all_player_names, index=0)
with select_col2:
    p2 = st.selectbox("Select Player 2", all_player_names, index=min(1, len(all_player_names)-1))

compare_df = df[df["Name"].isin([p1, p2])].copy()

if not compare_df.empty:
    compare_df["Height Label"] = compare_df["Height (m)"].apply(lambda x: f"{x:.2f}m ({meters_to_ft_in(x)})")
    compare_df["Display Name"] = compare_df["Name"] + "<br>" + compare_df["Height Label"]

    fig = px.bar(
        compare_df,
        x="Display Name",
        y="Height (m)",
        color="Country",
        text="Height Label",
        labels={"Height (m)": "Height Range", "Display Name": "Roster Entity"},
        title="Physical Scale Layout Model",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_traces(
        width=0.35, 
        textposition="outside", 
        textfont_size=13,
        marker_line_width=1.5
    )

    fig.update_layout(
        yaxis=dict(range=[0, 2.25], dtick=0.10, title="Height Baseline (Meters)"),
        xaxis=dict(title=""),
        plot_bgcolor="rgba(0,0,0,0)",
        height=550
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 5. Global Roster Browser Panel
st.header("🌍 League Explorer & Search Panel")

st.sidebar.header("Roster Filtering Dashboard")
league_countries = sorted(df["Country"].unique())
selected_leagues = st.sidebar.multiselect("Select Leagues/Nations", league_countries, default=league_countries[:4])

available_positions = sorted(df["Position"].unique())
selected_positions = st.sidebar.multiselect("Select Positions", available_positions, default=available_positions)

filtered_df = df[df["Country"].isin(selected_leagues) & df["Position"].isin(selected_positions)]

col1, col2, col3 = st.columns(3)
col1.metric("Total Match Records Found", len(filtered_df))
col2.metric("Group Average Height", f"{filtered_df['Height (m)'].mean():.2f} m" if not filtered_df.empty else "N/A")
col3.metric("Peak Target Benchmark", f"{filtered_df['Height (m)'].max():.2f} m" if not filtered_df.empty else "N/A")

if not filtered_df.empty:
    st.subheader("📋 Searchable Data Grid Registry")
    st.dataframe(filtered_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
