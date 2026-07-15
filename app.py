import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration
st.set_page_config(page_title="Football Player Height Comparison", layout="wide")
st.title("⚽ Professional Footballer Height Visualization")
st.markdown("Select multiple professional football players across Europe to compare their heights side-by-side.")

# 2. Automated Deep Data Scraper for Top European Leagues
@st.cache_data(ttl=86400)  # Cache results for 24 hours to keep the app blazing fast
def load_all_european_players():
    # Top European leagues as structured inside the openfootball/players repository
    leagues = ["england", "france", "germany", "italy", "spain", "netherlands", "portugal"]
    parsed_players = []
    
    for country in leagues:
        # Check both common naming conventions used in this dataset (squads.txt and players.txt)
        for filename in ["squads.txt", "players.txt"]:
            url = f"https://githubusercontent.com{country}/{filename}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    lines = response.text.split("\n")
                    for line in lines:
                        line = line.strip()
                        # Skip blank lines and headers
                        if not line or line.startswith('=') or line.startswith('#'):
                            continue
                        
                        # Expected format: Eduardo Camavinga, M, 1.82 m, b. 10 Nov 2002 @ Miconje
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 3:
                            name = parts[0]
                            pos_tag = parts[1].upper()
                            height_str = parts[2]
                            
                            # Clean up position shorthands
                            pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                                       'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                                       'F': 'Forward', 'FW': 'Forward'}
                            position = pos_map.get(pos_tag, pos_tag)
                            
                            try:
                                if 'm' in height_str:
                                    height_val = float(height_str.replace('m', '').strip())
                                    parsed_players.append({
                                        "Name": name,
                                        "Country": country.title(),
                                        "Position": position,
                                        "Height (m)": height_val
                                    })
                            except ValueError:
                                continue
                    break # Stop checking filenames if the country's file was successfully read
            except Exception:
                continue

    return pd.DataFrame(parsed_players)

df = load_all_european_players()

# Helper math function to convert meters to feet/inches
def meters_to_ft_in(m):
    total_inches = m * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}' {inches}\""

if df.empty:
    st.error("Could not parse data from the repository files. Verify the repository path layout.")
else:
    # 3. Sidebar Selection Panel for Custom Comparison
    st.sidebar.header("Comparison Settings")
    
    # Allows selection of multiple players
    all_players = sorted(df["Name"].unique())
    selected_players = st.sidebar.multiselect(
        "Choose Players to Compare:",
        options=all_players,
        default=["Kylian Mbappé", "Harry Kane", "Eduardo Camavinga"]  # Preset examples across different leagues
    )

    # Apply selection filter
    comparison_df = df[df["Name"].isin(selected_players)].copy()

    if not comparison_df.empty:
        # Create descriptive visual labels for the bars
        comparison_df["Height Label"] = comparison_df["Height (m)"].apply(lambda x: f"{x:.2f}m ({meters_to_ft_in(x)})")
        comparison_df["Display Name"] = comparison_df["Name"] + "<br>" + comparison_df["Height Label"]

        # 4. Multi-Bar Height Visualizer Chart
        st.subheader("📊 Side-by-Side Multi-Player Comparison")
        
        fig = px.bar(
            comparison_df,
            x="Display Name",
            y="Height (m)",
            color="Country",
            text="Height Label",
            labels={"Height (m)": "Height (Meters)", "Display Name": "Players Selected"},
            title="Height Comparison Chart",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig.update_traces(
            width=0.4, 
            textposition="outside", 
            textfont_size=12,
            marker_line_width=1
        )

        fig.update_layout(
            yaxis=dict(
                range=[1.5, 2.10],  # Zoomed-in scale to make relative height gaps visually noticeable
                dtick=0.05, 
                title="Height in Meters"
            ),
            xaxis=dict(title=""),
            plot_bgcolor="rgba(0,0,0,0)",
            height=550
        )
        st.plotly_chart(fig, use_container_width=True)

        # 5. Full Stats Grid View
        st.subheader("📋 Detailed Metrics View")
        st.dataframe(comparison_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
    else:
        st.info("Please select multiple football players from the sidebar drop-down menu to display the grid chart.")
