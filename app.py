import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration
st.set_page_config(page_title="Transfermarkt Height Analyzer", layout="wide")
st.title("⚽ Comprehensive Footballer Height Visualization")
st.markdown("Select and compare thousands of professional football players side-by-side using the Transfermarkt Registry.")

# 2. Optimized Reliable Global Database Loader
@st.cache_data(ttl=86400) # Cache for 24 hours so your app loads instantly
def load_all_players():
    # Direct access to the flat structural tracking file in the salimt repository
    url = "https://githubusercontent.com"
    
    try:
        # Resolve network stream blockers by adding custom user-agent headers to the fetch request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=15)
        
        # Open data byte stream cleanly via pandas storage engine
        import io
        raw_df = pd.read_parquet(io.BytesIO(response.content))
        
        # Build clean data structure schema
        clean_df = pd.DataFrame()
        clean_df["Name"] = raw_df["name"] if "name" in raw_df.columns else raw_df["player_name"]
        clean_df["Country"] = raw_df["country_of_citizenship"] if "country_of_citizenship" in raw_df.columns else "Unknown"
        clean_df["Position"] = raw_df["primary_position"] if "primary_position" in raw_df.columns else "Unknown"
        
        # Standardize height numbers
        if "height_in_cm" in raw_df.columns:
            clean_df["Height (m)"] = raw_df["height_in_cm"] / 100.0
        else:
            clean_df["Height (m)"] = raw_df["height"] / 100.0 if raw_df["height"].max() > 10 else raw_df["height"]
            
        return clean_df.dropna(subset=["Name", "Height (m)"])
        
    except Exception:
        # If GitHub completely blocks binary parquet traffic to your cloud workspace, 
        # this alternate endpoint reads the complete parsed player metadata registry flat-file
        try:
            alt_url = "https://githubusercontent.com"
            alt_res = requests.get(alt_url, timeout=15)
            parsed_players = []
            current_country = "Unknown"
            
            for line in alt_res.text.split("\n"):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('='):
                    current_country = line.replace('=', '').strip()
                    continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    if 'm' in parts[2]:
                        parsed_players.append({
                            "Name": parts[0],
                            "Country": current_country,
                            "Position": parts[1].upper(),
                            "Height (m)": float(parts[2].replace('m', '').strip())
                        })
            return pd.DataFrame(parsed_players)
        except Exception as err:
            st.error(f"Critical Connection Block: {err}")
            return pd.DataFrame()

df = load_all_players()

# Helper standard imperial math conversion utility
def meters_to_ft_in(m):
    total_inches = m * 39.3701
    feet = int(total_inches // 12)
    inches = round(total_inches % 12)
    return f"{feet}' {inches}\""

if df.empty:
    st.error("Roster parsing matrix returned blank views. Verify database paths.")
else:
    # 3. Sidebar Selection Panel for broad country filters
    st.sidebar.header("Global Roster Filters")
    all_countries = sorted(df["Country"].dropna().unique())
    selected_countries = st.sidebar.multiselect(
        "Active Nations in Database Search:",
        options=all_countries,
        default=all_countries[:5] # Keeps dropdown selection responsive
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
