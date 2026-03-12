import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="SmartTour Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("SmartTourRoutePlanner.csv")

df = load_data()

st.title("SmartTour Route Visualization Dashboard")
st.markdown("Interactive overview of routes, demand patterns, and traveler preferences.")

tab1, tab2, tab3, tab4 = st.tabs([
    "Traffic & Time",
    "Demand & Preferences",
    "Budget & Satisfaction",
    "Cost Breakdown"
])

with tab1:
    df["traffic_density_bin"] = pd.cut(
        df["traffic_density"],
        bins=[0,0.2,0.4,0.6,0.8,1],
        labels=["Very Low","Low","Medium","High","Very High"]
    )

    traffic_time = (
        df.groupby("traffic_density_bin")["estimated_travel_time_hr"]
        .mean()
        .reset_index()
    )

    fig1 = px.line(
        traffic_time,
        x="traffic_density_bin",
        y="estimated_travel_time_hr",
        markers=True,
        title="Impact of Traffic Density on Estimated Travel Time"
    )

    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.violin(
        df,
        x="day_type",
        y="traffic_density",
        color="day_type",
        box=True,
        points="all"
    )

    st.plotly_chart(fig2, use_container_width=True)


with tab2:
    fig3 = px.density_heatmap(
        df,
        x="season",
        y="day_type",
        z="popularity_score",
        histfunc="avg",
        title="Heatmap of Travel Demand"
    )

    st.plotly_chart(fig3, use_container_width=True)

    sunburst_data = (
        df.groupby(["season","transport_mode","destination_type"])["popularity_score"]
        .sum()
        .reset_index()
    )

    fig4 = px.sunburst(
        sunburst_data,
        path=["season","transport_mode","destination_type"],
        values="popularity_score"
    )

    st.plotly_chart(fig4, use_container_width=True)


with tab3:
    fig5 = px.scatter(
        df,
        x="user_budget",
        y="satisfaction_rating",
        color="transport_mode",
        symbol="season",
        title="User Budget vs Satisfaction"
    )

    st.plotly_chart(fig5, use_container_width=True)

    radar = df.groupby("transport_mode")[
        ["user_budget","user_time_constraint_hr","popularity_score","traffic_density","satisfaction_rating"]
    ].mean()

    scaler = MinMaxScaler()
    radar_scaled = scaler.fit_transform(radar)

    categories = ["Budget","Time","Popularity","Traffic","Satisfaction"]

    fig6 = go.Figure()

    for i, mode in enumerate(radar.index):
        values = radar_scaled[i].tolist()
        values += values[:1]

        fig6.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=mode
        ))

    fig6.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])))

    st.plotly_chart(fig6, use_container_width=True)


with tab4:
    entry = df["entry_fee"].mean()
    accom = df["accommodation_cost"].mean()
    food = df["food_cost"].mean()

    fig7 = go.Figure(data=[go.Sankey(
        node=dict(label=["Total Cost","Entry","Accommodation","Food"]),
        link=dict(
            source=[0,0,0],
            target=[1,2,3],
            value=[entry,accom,food]
        )
    )])

    fig7.update_layout(title="Travel Cost Distribution")

    st.plotly_chart(fig7, use_container_width=True)
