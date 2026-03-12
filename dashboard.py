import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="SmartTour Dashboard", layout="wide")

# -------------------------
# STYLING
# -------------------------
st.markdown("""
<style>

.block-container{
max-width:1300px;
padding-top:1rem;
}

.hero{
background: linear-gradient(120deg,#0f172a,#1e293b,#334155);
border-radius:18px;
padding:45px;
color:white;
margin-bottom:25px;
transition:0.3s;
}

.hero:hover{
transform:scale(1.01);
}

.hero-title{
font-size:40px;
font-weight:700;
}

.hero-sub{
opacity:0.85;
margin-top:10px;
}

.control-bar{
background:#f8fafc;
padding:20px;
border-radius:12px;
margin-bottom:25px;
box-shadow:0 2px 10px rgba(0,0,0,0.05);
}

.section{
background:white;
padding:25px;
border-radius:14px;
margin-bottom:20px;
box-shadow:0 4px 18px rgba(0,0,0,0.06);
}

.desc{
color:#64748b;
font-size:14px;
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    return pd.read_csv("SmartTourRoutePlanner.csv")

df = load_data()

# -------------------------
# HERO SECTION
# -------------------------
st.markdown('<div class="hero">', unsafe_allow_html=True)

left,right = st.columns([3,1])

with left:
    st.markdown('<div class="hero-title">SmartTour Route Intelligence</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-sub">Analyze travel demand, route preferences, and tourism patterns across India.</div>',
        unsafe_allow_html=True
    )

with right:
    st.metric("Total Routes", len(df))
    st.metric("Avg Satisfaction", round(df["satisfaction_rating"].mean(),2))

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# FILTER BAR
# -------------------------
st.markdown('<div class="control-bar">', unsafe_allow_html=True)

f1,f2,f3 = st.columns(3)

with f1:
    season_filter = st.multiselect(
        "Season",
        df["season"].unique(),
        default=df["season"].unique()
    )

with f2:
    transport_filter = st.multiselect(
        "Transport Mode",
        df["transport_mode"].unique(),
        default=df["transport_mode"].unique()
    )

with f3:
    day_filter = st.multiselect(
        "Day Type",
        df["day_type"].unique(),
        default=df["day_type"].unique()
    )

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# FILTER DATA
# -------------------------
filtered_df = df[
    (df["season"].isin(season_filter)) &
    (df["transport_mode"].isin(transport_filter)) &
    (df["day_type"].isin(day_filter))
]

# -------------------------
# TABS
# -------------------------
tab1,tab2,tab3,tab4,tab5 = st.tabs([
"Traffic Analysis",
"Demand Patterns",
"Budget & Preferences",
"Cost Breakdown",
"India Route Map"
])

# -------------------------
# TRAFFIC
# -------------------------
with tab1:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("Traffic Density vs Travel Time")

    st.markdown(
    '<div class="desc">Uses traffic_density and estimated_travel_time_hr to show how congestion impacts travel duration.</div>',
    unsafe_allow_html=True)

    filtered_df["traffic_density_bin"]=pd.cut(
        filtered_df["traffic_density"],
        bins=[0,0.2,0.4,0.6,0.8,1],
        labels=["Very Low","Low","Medium","High","Very High"]
    )

    traffic_time=filtered_df.groupby("traffic_density_bin")["estimated_travel_time_hr"].mean().reset_index()

    fig=px.line(
        traffic_time,
        x="traffic_density_bin",
        y="estimated_travel_time_hr",
        markers=True
    )

    st.plotly_chart(fig,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# DEMAND
# -------------------------
with tab2:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("Travel Demand Heatmap")

    st.markdown(
    '<div class="desc">Uses season, day_type and popularity_score to identify peak tourism demand.</div>',
    unsafe_allow_html=True)

    fig=px.density_heatmap(
        filtered_df,
        x="season",
        y="day_type",
        z="popularity_score",
        histfunc="avg"
    )

    st.plotly_chart(fig,use_container_width=True)

    sunburst_data=filtered_df.groupby(
        ["season","transport_mode","destination_type"]
    )["popularity_score"].sum().reset_index()

    fig2=px.sunburst(
        sunburst_data,
        path=["season","transport_mode","destination_type"],
        values="popularity_score"
    )

    st.plotly_chart(fig2,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# BUDGET
# -------------------------
with tab3:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("Budget vs Satisfaction")

    st.markdown(
    '<div class="desc">Explores how user_budget correlates with satisfaction_rating across transport modes.</div>',
    unsafe_allow_html=True)

    fig=px.scatter(
        filtered_df,
        x="user_budget",
        y="satisfaction_rating",
        color="transport_mode"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Traveler Preference Radar")

    radar=filtered_df.groupby("transport_mode")[[
        "user_budget",
        "user_time_constraint_hr",
        "popularity_score",
        "traffic_density",
        "satisfaction_rating"
    ]].mean()

    scaler=MinMaxScaler()
    radar_scaled=scaler.fit_transform(radar)

    categories=["Budget","Time","Popularity","Traffic","Satisfaction"]

    fig3=go.Figure()

    for i,mode in enumerate(radar.index):

        values=radar_scaled[i].tolist()
        values+=values[:1]

        fig3.add_trace(go.Scatterpolar(
            r=values,
            theta=categories+[categories[0]],
            fill="toself",
            name=mode
        ))

    fig3.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,1])))

    st.plotly_chart(fig3,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# COST
# -------------------------
with tab4:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    entry=filtered_df["entry_fee"].mean()
    accom=filtered_df["accommodation_cost"].mean()
    food=filtered_df["food_cost"].mean()

    fig=go.Figure(data=[go.Sankey(
        node=dict(label=["Total Cost","Entry Fee","Accommodation","Food"]),
        link=dict(source=[0,0,0],target=[1,2,3],value=[entry,accom,food])
    )])

    st.plotly_chart(fig,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# INDIA MAP
# -------------------------
with tab5:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    city_coords={
    "Delhi":(28.6139,77.2090),
    "Mumbai":(19.0760,72.8777),
    "Bangalore":(12.9716,77.5946),
    "Chennai":(13.0827,80.2707),
    "Kolkata":(22.5726,88.3639),
    "Agra":(27.1767,78.0081),
    "Goa":(15.2993,74.1240),
    "Shimla":(31.1048,77.1734),
    "Ooty":(11.4064,76.6932),
    "Mahabalipuram":(12.6208,80.1937)
    }

    filtered_df["start_lat"]=filtered_df["start_location"].map(lambda x:city_coords.get(x,(None,None))[0])
    filtered_df["start_lon"]=filtered_df["start_location"].map(lambda x:city_coords.get(x,(None,None))[1])

    filtered_df["end_lat"]=filtered_df["end_location"].map(lambda x:city_coords.get(x,(None,None))[0])
    filtered_df["end_lon"]=filtered_df["end_location"].map(lambda x:city_coords.get(x,(None,None))[1])

    m=folium.Map(location=[22.5,80],zoom_start=5,tiles="cartodbpositron")

    colors={
    "car":"blue",
    "train":"green",
    "bike":"orange",
    "walk":"purple",
    "bus":"brown"
    }

    for _,row in filtered_df.iterrows():

        if pd.notnull(row["start_lat"]) and pd.notnull(row["end_lat"]):

            start=(row["start_lat"],row["start_lon"])
            end=(row["end_lat"],row["end_lon"])

            color=colors.get(str(row["transport_mode"]).lower(),"black")

            folium.PolyLine(
                locations=[start,end],
                color=color,
                weight=3
            ).add_to(m)

    st_folium(m,width=1000,height=600)

    st.markdown('</div>', unsafe_allow_html=True)
