import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="SmartTour", layout="wide")

# ---------------------------------------------------
# GLOBAL CSS (Lovable Style UI)
# ---------------------------------------------------
st.markdown("""
<style>

.block-container{
padding-top:1rem;
padding-bottom:1rem;
max-width:1400px;
}

.hero{
background:linear-gradient(120deg,#0f172a,#1e293b,#334155);
border-radius:20px;
padding:45px;
color:white;
position:relative;
overflow:hidden;
margin-bottom:25px;
}

.hero:before{
content:"";
position:absolute;
top:-50%;
left:-50%;
width:200%;
height:200%;
background:radial-gradient(circle at center, rgba(255,255,255,0.12), transparent 60%);
transition:all .6s ease;
}

.hero:hover:before{
transform:scale(1.2);
}

.hero-title{
font-size:42px;
font-weight:700;
letter-spacing:-1px;
}

.hero-sub{
opacity:0.8;
font-size:17px;
margin-top:10px;
}

.kpi-card{
background:white;
padding:20px;
border-radius:14px;
text-align:center;
box-shadow:0 3px 12px rgba(0,0,0,0.08);
transition:all .2s ease;
}

.kpi-card:hover{
transform:translateY(-4px);
box-shadow:0 10px 22px rgba(0,0,0,0.15);
}

.section{
background:white;
padding:25px;
border-radius:18px;
margin-bottom:20px;
box-shadow:0 3px 12px rgba(0,0,0,0.08);
}

.section h3{
margin-top:0px;
}

.small-desc{
color:#6b7280;
font-size:14px;
margin-bottom:15px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("SmartTourRoutePlanner.csv")

df = load_data()

# ---------------------------------------------------
# HERO SECTION
# ---------------------------------------------------
st.markdown('<div class="hero">', unsafe_allow_html=True)

left,right = st.columns([2,1])

with left:
    st.markdown('<div class="hero-title">SmartTour Travel Intelligence</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-sub">Analyze travel demand, transportation patterns and tourism routes across India.</div>',
        unsafe_allow_html=True
    )

with right:
    season_filter = st.multiselect(
        "Season",
        df["season"].unique(),
        default=df["season"].unique()
    )

    transport_filter = st.multiselect(
        "Transport",
        df["transport_mode"].unique(),
        default=df["transport_mode"].unique()
    )

    day_filter = st.multiselect(
        "Day Type",
        df["day_type"].unique(),
        default=df["day_type"].unique()
    )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------
filtered_df = df[
    (df["season"].isin(season_filter)) &
    (df["transport_mode"].isin(transport_filter)) &
    (df["day_type"].isin(day_filter))
]

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------
k1,k2,k3,k4 = st.columns(4)

k1.markdown(f'<div class="kpi-card"><h3>{len(filtered_df)}</h3>Routes</div>',unsafe_allow_html=True)
k2.markdown(f'<div class="kpi-card"><h3>{round(filtered_df["satisfaction_rating"].mean(),2)}</h3>Avg Satisfaction</div>',unsafe_allow_html=True)
k3.markdown(f'<div class="kpi-card"><h3>{round(filtered_df["user_budget"].mean(),0)}</h3>Avg Budget</div>',unsafe_allow_html=True)
k4.markdown(f'<div class="kpi-card"><h3>{round(filtered_df["estimated_travel_time_hr"].mean(),2)}</h3>Travel Time</div>',unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------
# TABS
# ---------------------------------------------------
tab1,tab2,tab3,tab4,tab5 = st.tabs([
"Traffic",
"Demand",
"Budget",
"Costs",
"Map"
])

# ---------------------------------------------------
# TRAFFIC
# ---------------------------------------------------
with tab1:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.markdown("### Traffic Density vs Travel Time")
    st.markdown('<div class="small-desc">Uses traffic_density and estimated_travel_time_hr to show congestion impact.</div>', unsafe_allow_html=True)

    filtered_df["traffic_density_bin"]=pd.cut(
        filtered_df["traffic_density"],
        bins=[0,0.2,0.4,0.6,0.8,1],
        labels=["Very Low","Low","Medium","High","Very High"]
    )

    traffic_time = filtered_df.groupby("traffic_density_bin")["estimated_travel_time_hr"].mean().reset_index()

    fig=px.line(
        traffic_time,
        x="traffic_density_bin",
        y="estimated_travel_time_hr",
        markers=True
    )

    st.plotly_chart(fig,use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# DEMAND
# ---------------------------------------------------
with tab2:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.markdown("### Travel Demand Heatmap")
    st.markdown('<div class="small-desc">Season vs Day Type using popularity_score.</div>', unsafe_allow_html=True)

    fig=px.density_heatmap(
        filtered_df,
        x="season",
        y="day_type",
        z="popularity_score",
        histfunc="avg"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# BUDGET
# ---------------------------------------------------
with tab3:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.markdown("### Budget vs Satisfaction")

    fig=px.scatter(
        filtered_df,
        x="user_budget",
        y="satisfaction_rating",
        color="transport_mode"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# COST
# ---------------------------------------------------
with tab4:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    entry=filtered_df["entry_fee"].mean()
    accom=filtered_df["accommodation_cost"].mean()
    food=filtered_df["food_cost"].mean()

    fig=go.Figure(data=[go.Sankey(
        node=dict(label=["Total","Entry","Accommodation","Food"]),
        link=dict(source=[0,0,0],target=[1,2,3],value=[entry,accom,food])
    )])

    st.plotly_chart(fig,use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# MAP
# ---------------------------------------------------
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

    colors={"car":"blue","train":"green","bike":"orange","walk":"purple","bus":"brown"}

    for _,row in filtered_df.iterrows():

        if pd.notnull(row["start_lat"]) and pd.notnull(row["end_lat"]):

            start=(row["start_lat"],row["start_lon"])
            end=(row["end_lat"],row["end_lon"])

            color=colors.get(str(row["transport_mode"]).lower(),"black")

            folium.PolyLine(locations=[start,end],color=color,weight=3).add_to(m)

    st_folium(m,width=1000,height=600)

    st.markdown("</div>", unsafe_allow_html=True)
