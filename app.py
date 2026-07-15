import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup
st.set_page_config(page_title="Football Player Height Comparison", layout="wide")
st.title("🧍‍♂️ Head-to-Head Footballer Height Comparison")
st.markdown("Select specific professional football players to visualize their heights side-by-side.")

# 2. Roster Dataset
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

# 3. Dropdown Selection Panel
st.sidebar.header("Comparison Settings")

# Multi-select dropdown to pick specific players by name
all_players = sorted(df["Name"].unique())
selected_players = st.sidebar.multiselect(
    "Choose Players to Compare:",
    options=all_players,
    default=["Kylian Mbappé", "Manuel Neuer"] # Default preset to show off the visual immediately
)

# Filter dataset to match only the names picked by the user
comparison_df = df[df["Name"].isin(selected_players)]

if not comparison_df.empty:
    
    # 4. Helper math function to dynamically compute Feet and Inches labels
    def meters_to_ft_in(m):
        total_inches = m * 39.3701
        feet = int(total_inches // 12)
        inches = round(total_inches % 12)
        return f"{feet}' {inches}\""

    # Inject clean text strings for chart tooltips and labels
    comparison_df["Height Label"] = comparison_df["Height (m)"].apply(lambda x: f"{x:.2f}m ({meters_to_ft_in(x)})")
    comparison_df["Display Name"] = comparison_df["Name"] + "<br>" + comparison_df["Height Label"]

    st.subheader("📊 Side-by-Side Height Comparison")

    # 5. Build the visual profile block chart
    fig = px.bar(
        comparison_df,
        x="Display Name",
        y="Height (m)",
        color="Country",
        text="Height Label", # Prints the height measurement text directly on top of the bars
        labels={"Height (m)": "Height (Centimeters / Meters)", "Display Name": "Player"},
        title="Who is taller?",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # 6. Adjust the layout to mimic the reference image styling
    fig.update_traces(
        width=0.4, # Thicker, distinct bars to look like human silhouette columns
        textposition="outside", # Places the label values cleanly over the tops
        textfont_size=14,
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5
    )

    fig.update_layout(
        yaxis=dict(
            range=[0, 2.20], # Fixed grid boundaries stretching up past 2 meters
            dtick=0.10, # Draws scale marker grid lines every 10 centimeters
            title="Height in Meters"
        ),
        xaxis=dict(
            title=""
        ),
        showlegend=True,
        height=600,
        plot_bgcolor="rgba(0,0,0,0)" # Crystal clear, clean plot background
    )

    # Render the chart asset to your Streamlit screen layout
    st.plotly_chart(fig, use_container_width=True)

    # 7. Raw Stats breakdown matrix
    st.subheader("📋 Compare Metrics Detail")
    st.dataframe(comparison_df[["Name", "Country", "Position", "Height (m)"]], use_container_width=True)

else:
    st.info("Please select at least one football player from the sidebar menu to populate the visual comparison graph.")
