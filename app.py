import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Must stay at the absolute top)
st.set_page_config(page_title="Football Player Height Comparison", layout="wide")
st.title("⚽ Professional Footballer Height Visualization")
st.markdown("Compare and analyze professional football player heights across different nations.")

# 2. Local Dataset (Hardcoded to completely avoid GitHub connection errors)
@st.cache_data
def load_player_data():
    raw_data = [
        # France
        {"Name": "Eduardo Camavinga", "Country": "France", "Position": "Midfielder", "Height (m)": 1.82},
        {"Name": "Kylian Mbappé", "Country": "France", "Position": "Forward", "Height (m)": 1.78},
        {"Name": "Dayot Upamecano", "Country": "France", "Position": "Defender", "Height (m)": 1.88},
        {"Name": "Benjamin Pavard", "Country": "France", "Position": "Defender", "Height (m)": 1.82},
        {"Name": "Antoine Griezmann", "Country": "France", "Position": "Forward", "Height (m)": 1.75},
        
        # England
        {"Name": "Jude Bellingham", "Country": "England", "Position": "Midfielder", "Height (m)": 1.80},
        {"Name": "Jordan Pickford", "Country": "England", "Position": "Goalkeeper", "Height (m)": 1.85},
        {"Name": "Harry Kane", "Country": "England", "Position": "Forward", "Height (m)": 1.88},
        {"Name": "Bukayo Saka", "Country": "England", "Position": "Forward", "Height (m)": 1.78},
        {"Name": "Declan Rice", "Country": "England", "Position": "Midfielder", "Height (m)": 1.85},
        
        # Germany
        {"Name": "Manuel Neuer", "Country": "Germany", "Position": "Goalkeeper", "Height (m)": 1.93},
        {"Name": "Jamal Musiala", "Country": "Germany", "Position": "Midfielder", "Height (m)": 1.84},
        {"Name": "Florian Wirtz", "Country": "Germany", "Position": "Midfielder", "Height (m)": 1.76},
        {"Name": "Antonio Rüdiger", "Country": "Germany", "Position": "Defender", "Height (m)": 1.90},
        
        # Spain
        {"Name": "Rodri", "Country": "Spain", "Position": "Midfielder", "Height (m)": 1.91},
        {"Name": "Lamine Yamal", "Country": "Spain", "Position": "Forward", "Height (m)": 1.78},
        {"Name": "Pedri", "Country": "Spain", "Position": "Midfielder", "Height (m)": 1.74},
        {"Name": "Dani Carvajal", "Country": "Spain", "Position": "Defender", "Height (m)": 1.73}
    ]
    return pd.DataFrame(raw_data)

df = load_player_data()

# 3. Sidebar Filtering Panels
st.sidebar.header("Filter Roster")

countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries)

positions = sorted(df["Position"].unique())
selected_positions = st.sidebar.multiselect("Select Positions", positions, default=positions)

# Dynamic filtering execution
filtered_df = df[df["Country"].isin(selected_countries) & df["Position"].isin(selected_positions)]

# 4. Summary Dash Tiles
col1, col2, col3 = st.columns(3)
col1.metric("Total Players Displayed", len(filtered_df))
col2.metric("Average Height", f"{filtered_df['Height (m)'].mean():.2f} m" if not filtered_df.empty else "N/A")
col3.metric("Tallest Player", f"{filtered_df['Height (m)'].max():.2f} m" if not filtered_df.empty else "N/A")

if not filtered_df.empty:
    # 5. Interactive Scatter Graph Layout
    st.subheader("📊 Height Distributions and Trends")
    
    fig_scatter = px.scatter(
        filtered_df,
        x="Position",
        y="Height (m)",
        color="Country",
        hover_data=["Name"],
        title="Player Heights Segmented by Position & Country",
        labels={"Height (m)": "Height in Meters"},
        height=500
    )
    # Increase marker size for readability
    fig_scatter.update_traces(marker=dict(size=12))
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 6. Searchable Matrix Table
    st.subheader("📋 Searchable Data Registry")
    st.dataframe(filtered_df.sort_values(by="Height (m)", ascending=False), use_container_width=True)
else:
    st.info("Select options inside the sidebar menu to view comparisons.")
