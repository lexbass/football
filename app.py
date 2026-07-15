import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration
st.set_page_config(page_title="European Footballer Height Tracker", layout="wide")
st.title("⚽ Comprehensive Professional Footballer Height Visualization")
st.markdown("Select and compare multiple professional football players across Europe side-by-side.")

# 2. Automated Multi-Country Raw Data Loader
@st.cache_data(ttl=86400) # Cache the results for 24 hours so your app loads instantly
def load_all_european_players():
    # These match the exact subfolder names in openfootball/players
    countries = ["england", "france", "germany", "italy", "spain", "netherlands", "portugal"]
    parsed_players = []
    
    for country in countries:
        # Step A: Each country has a specific squad file named 'squads.txt'
        url = f"https://githubusercontent.com{country}/squads.txt"
        try:
            response = requests.get(url)
            
            # Step B: Fallback to alternative naming 'players.txt' if squads.txt isn't used
            if response.status_code != 200:
                url = f"https://githubusercontent.com{country}/players.txt"
                response = requests.get(url)
                
            if response.status_code == 200:
                lines = response.text.split("\n")
                for line in lines:
                    line = line.strip()
                    # Skip blank lines and section headers
                    if not line or line.startswith('=') or line.startswith('#'):
                        continue
                    
                    # Target layout: Name, Position, Height, Birthdate
                    # Example: Eduardo Camavinga, M, 1.82 m, b. 10 Nov 2002 @ Miconje
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        name = parts[0]
                        pos_tag = parts[1].upper()
                        height_str = parts[2]
                        
                        # Clean up shorthand position keywords
                        pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                                   'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                                   'F': 'Forward', 'FW': 'Forward'}
                        position = pos_map.get(pos_tag, pos_tag)
                        
                        try:
                            # Isolate the float height decimal by stripping 'm'
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
        except Exception:
            continue

    return pd.DataFrame(parsed_players)

df = load_all_european_players()

# Helper conversion math formula
def meters_to_ft_in(m):
    total_inches = m * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}' {inches}\""

if df.empty:
    st.error("Failed to fetch data from the openfootball repository. Please try rebooting the application cloud link.")
else:
    # 3. Sidebar Selection Panel for grouping filters
    st.sidebar.header("Global Roster Controls")
    all_countries = sorted(df["Country"].unique())
    selected_countries = st.sidebar.multiselect(
        "Filter Available Player Roster by Country:",
        options=all_countries,
        default=all_countries
    )

    # Filter data matrix to match selected countries
    filtered_df = df[df["Country"].isin(selected_countries)]

    # 4. Multi-Select Player Specific Selector Dashboard
    st.subheader("📊 Choose Multiple Competitors Side-by-Side")
    selectable_players = sorted(filtered_df["Name"].unique())

    selected_players = st.multiselect(
        "Search and select multiple players by name to add them to your chart view:",
        options=selectable_players,
        default=selectable_players[:5] if len(selectable_players) >= 5 else selectable_players
    )

    comparison_df = filtered_df[filtered_df["Name"].isin(selected_players)].copy()

    if not comparison_df.empty:
        # Build text labels to attach directly above the chart rows
        comparison_df["Height Label"] = comparison_df["Height (m)"].apply(lambda x: f"{x:.2f}m ({meters_to_ft_in(x)})")
        comparison_df["Display Name"] = comparison_df["Name"] + "<br>(" + comparison_df["Country"] + ")"

        # 5. Multi-Bar Custom Height Comparison Chart Layout
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
                range=[1.5, 2.15], # Keeps zoom bounds functional to trace relative height differences
                dtick=0.05, 
                title="Height in Meters"
            ),
            xaxis=dict(title=""),
            plot_bgcolor="rgba(0,0,0,0)",
            height=550
        )
        st.plotly_chart(fig, use_container_width=True)

        # 6. Searchable Raw Stats Breakdown Registry
        st.subheader("📋 Detailed Metrics View")
        st.dataframe(comparison_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
    else:
        st.info("Please select multiple football players from the drop-down menu above to populate the comparison chart.")
