import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Must remain the first active Streamlit line)
st.set_page_config(page_title="Footballer Height Analyzer", layout="wide")
st.title("⚽ Comprehensive Footballer Height Visualization")
st.markdown("Select and compare thousands of professional football players side-by-side using your uploaded database.")

# 2. Optimized Reliable Local Database Loader
#@st.cache_data(ttl=86400) # Cache for 24 hours so your app loads instantly
def load_all_players():
    import json
    import os
    
    file_path = "players.json"
    
    # Check if the dataset is present in the repository root directory
    if not os.path.exists(file_path):
        st.error("Missing 'players.json' file! Please ensure you uploaded it to the root of your GitHub repository.")
        return pd.DataFrame()
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        df = pd.DataFrame(data)
        
        # Standardize position classifications to match chart code requirements
        pos_map = {'G': 'Goalkeeper', 'GK': 'Goalkeeper', 'D': 'Defender', 
                   'DF': 'Defender', 'M': 'Midfielder', 'MF': 'Midfielder', 
                   'F': 'Forward', 'FW': 'Forward'}
        df["Position"] = df["Position"].map(pos_map).fillna(df["Position"])
        df = df.rename(columns={"Height": "Height (m)"})
        return df
    except Exception as e:
        st.error(f"Error reading local 'players.json' file: {e}")
        return pd.DataFrame()

df = load_all_players()

# Helper standard imperial math conversion utility
def meters_to_ft_in(m):
    total_inches = m * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}' {inches}\""

if df.empty:
    st.info("Upload your downloaded 'players.json' file to the root of your GitHub repository to initialize the app panels.")
else:
    # 3. Sidebar Selection Panel for broad country filters
    st.sidebar.header("Global Roster Filters")
    all_countries = sorted(df["Country"].dropna().unique())
    selected_countries = st.sidebar.multiselect(
        "Active Nations in Database Search:",
        options=all_countries,
        default=all_countries[:3] # Keeps dropdown selection responsive on startup
    )

    # Filter main dataset to match active countries
    filtered_df = df[df["Country"].isin(selected_countries)]

    # 4. Multi-Select Player Picker Dashboard 
    st.subheader("📊 Choose Multiple Competitors Side-by-Side")
    selectable_players = sorted(filtered_df["Name"].unique())

    selected_players = st.multiselect(
        "Search and select multiple players by name to overlay on the chart below:",
        options=selectable_players,
        default=selectable_players[:5] if len(selectable_players) >= 5 else selectable_players
    )

    comparison_df = filtered_df[filtered_df["Name"].isin(selected_players)].copy()

    if not comparison_df.empty:
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
                range=[1.5, 2.15], 
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
