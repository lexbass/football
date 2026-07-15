import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration (Must remain the first active Streamlit line)
st.set_page_config(page_title="Global Footballer Height Tracker", layout="wide")
st.title("⚽ Comprehensive Professional Footballer Height Visualization")
st.markdown("Compare and analyze all players from all available countries registered in the openfootball repository.")

# 2. Complete Automated Global Database Loader
@st.cache_data(ttl=86400) # Cache for 24 hours to ensure high speed
def load_comprehensive_global_players():
    # Target raw data text file from the openfootball player database
    url = "https://githubusercontent.com"
    parsed_players = []
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            lines = response.text.split("\n")
            current_country = "Unknown"
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Dynamic Country Header Detector (e.g., = England =, = France =)
                if line.startswith('='):
                    current_country = line.replace('=', '').strip()
                    continue
                
                # Expected text format: Player Name, Position, Height, Birth Info
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    name = parts[0]
                    pos_tag = parts[1].upper()
                    height_str = parts[2]
                    
                    # Map position keys cleanly
                    pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                               'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                               'F': 'Forward', 'FW': 'Forward'}
                    position = pos_map.get(pos_tag, pos_tag)
                    
                    try:
                        if 'm' in height_str:
                            height_val = float(height_str.replace('m', '').strip())
                            parsed_players.append({
                                "Name": name,
                                "Country": current_country,
                                "Position": position,
                                "Height (m)": height_val
                            })
                    except ValueError:
                        continue
                        
    except Exception as e:
        st.error(f"Network error trying to stream the massive database: {e}")
        
    return pd.DataFrame(parsed_players)

df = load_comprehensive_global_players()

# Helper standard imperial math conversion utility
def meters_to_ft_in(m):
    total_inches = m * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}' {inches}\""

if df.empty:
    st.error("Failed to compile global player datasets. Check your repository connectivity parameters.")
else:
    # 3. Dynamic Filtering Sidebar Setup
    st.sidebar.header("Global Roster Controls")
    
    # Filter the entire list down to specific subsets if desired
    all_available_countries = sorted(df["Country"].unique())
    selected_countries = st.sidebar.multiselect(
        "Filter Database by Country:", 
        options=all_available_countries, 
        default=all_available_countries[:4] # Presets a few regions to avoid over-crowding charts
    )
    
    # Filter global dataset row selection
    filtered_roster = df[df["Country"].isin(selected_countries)]
    
    # 4. Multi-Select Player Specific Selector Dashboard
    st.subheader("📊 Choose Multiple Competitors Side-by-Side")
    selectable_players = sorted(filtered_roster["Name"].unique())
    
    selected_players = st.multiselect(
        "Search and select multiple players by name to overlay on the chart below:",
        options=selectable_players,
        default=selectable_players[:5] if len(selectable_players) >= 5 else selectable_players
    )
    
    comparison_df = filtered_roster[filtered_roster["Name"].isin(selected_players)].copy()

    if not comparison_df.empty:
        # Construct metrics descriptions above bars
        comparison_df["Height Label"] = comparison_df["Height (m)"].apply(lambda x: f"{x:.2f}m ({meters_to_ft_in(x)})")
        comparison_df["Display Name"] = comparison_df["Name"] + "<br>(" + comparison_df["Country"] + ")"

        # 5. Render Expanded Height Grid Layout
        fig = px.bar(
            comparison_df,
            x="Display Name",
            y="Height (m)",
            color="Country",
            text="Height Label",
            labels={"Height (m)": "Physical Elevation (Meters)", "Display Name": "Selected Athletes"},
            title="Custom Height Comparison Chart",
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(
            width=0.45, 
            textposition="outside", 
            textfont_size=12,
            marker_line_width=1
        )

        fig.update_layout(
            yaxis=dict(
                range=[1.40, 2.15], # Keeps zoom bounds functional to trace relative height differences
                dtick=0.05, 
                title="Height in Meters"
            ),
            xaxis=dict(title=""),
            plot_bgcolor="rgba(0,0,0,0)",
            height=550
        )
        st.plotly_chart(fig, use_container_width=True)

        # 6. Detailed Raw Numeric Breakdown Grid
        st.subheader("📋 Searchable Data Registry")
        st.dataframe(comparison_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
    else:
        st.info("Use the search selection box above to map out player names.")
