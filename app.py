import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Must remain the first active Streamlit line)
st.set_page_config(page_title="Transfermarkt Height Analyzer", layout="wide")
st.title("⚽ Comprehensive Footballer Height Visualization")
st.markdown("Select and compare professional football players side-by-side using the Transfermarkt Datalake registry.")

# 2. Automated Transfermarkt Datalake Connector
@st.cache_data(ttl=86400) # Cache dataset for 24 hours to ensure high dashboard speeds
def load_transfermarkt_dataset():
    # Targets the exact data lake partition file directly from the repo asset block
    url = "https://github.com"
    
    try:
        # Pandas reads parquet structural data formats flawlessly over direct links
        raw_df = pd.read_parquet(url)
        
        # Mapping/Renaming the data lake database columns to clean application terminology
        # Expected core columns: name, primary_position, height_in_cm, country_of_citizenship
        clean_df = pd.DataFrame()
        clean_df["Name"] = raw_df["name"] if "name" in raw_df.columns else raw_df["player_name"]
        clean_df["Country"] = raw_df["country_of_citizenship"] if "country_of_citizenship" in raw_df.columns else "Unknown"
        clean_df["Position"] = raw_df["primary_position"] if "primary_position" in raw_df.columns else "Unknown"
        
        # Handle conversion from data lake centimeter tracking to meters
        if "height_in_cm" in raw_df.columns:
            clean_df["Height (m)"] = raw_df["height_in_cm"] / 100.0
        elif "height" in raw_df.columns:
            clean_df["Height (m)"] = raw_df["height"] / 100.0 if raw_df["height"].max() > 10 else raw_df["height"]
        else:
            clean_df["Height (m)"] = 1.80 # Fallback safety default value
            
        # Clean out any records with missing metadata or corrupted height listings
        clean_df = clean_df.dropna(subset=["Name", "Height (m)"])
        clean_df = clean_df[clean_df["Height (m)"] > 1.20] # Removes bad placeholder values
        
        return clean_df
    except Exception as e:
        st.error(f"Failed to access the Transfermarkt datalake file branch: {e}")
        # Local emergency backup matrix if GitHub data lake path undergoes maintenance
        fallback = [
            {"Name": "Kylian Mbappé", "Country": "France", "Position": "Forward", "Height (m)": 1.78},
            {"Name": "Harry Kane", "Country": "England", "Position": "Forward", "Height (m)": 1.88},
            {"Name": "Erling Haaland", "Country": "Norway", "Position": "Forward", "Height (m)": 1.94},
            {"Name": "Virgil van Dijk", "Country": "Netherlands", "Position": "Defender", "Height (m)": 1.93}
        ]
        return pd.DataFrame(fallback)

df = load_transfermarkt_dataset()

# Helper conversion math formula to output standard feet/inches labels
def meters_to_ft_in(m):
    total_inches = m * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}' {inches}\""

if df.empty:
    st.error("Roster parsing matrix returned blank views. Verify parquet data mapping configurations.")
else:
    # 3. Sidebar Selection Panel for broad country filters
    st.sidebar.header("Global Roster Filters")
    all_countries = sorted(df["Country"].dropna().unique())
    selected_countries = st.sidebar.multiselect(
        "Active Nations in Database Search:",
        options=all_countries,
        default=all_countries[:5] # Presets a few nations to keep charts responsive
    )

    # Filter main dataset to match active countries
    filtered_df = df[df["Country"].isin(selected_countries)]

    # 4. Multi-Select Player Picker Dashboard 
    st.subheader("📊 Choose Multiple Competitors Side-by-Side")
    selectable_players = sorted(filtered_df["Name"].unique())

    selected_players = st.multiselect(
        "Search and select multiple players by name to overlay on the chart below:",
        options=selectable_players,
        default=selectable_players[:4] if len(selectable_players) >= 4 else selectable_players
    )

    comparison_df = filtered_df[filtered_df["Name"].isin(selected_players)].copy()

    if not comparison_df.empty:
        # Build layout description parameters directly above the chart rows
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
                range=[1.5, 2.15], # Precision zoom range settings to clearly show height changes
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
