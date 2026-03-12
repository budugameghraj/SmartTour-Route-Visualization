import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
import folium
from streamlit_folium import st_folium


def load_data(csv_path: str = "SmartTourRoutePlanner.csv") -> pd.DataFrame:
    """Load the dataset used in the notebook."""
    df = pd.read_csv(csv_path)
    return df


def build_traffic_time_line(df: pd.DataFrame) -> go.Figure:
    """Line plot: Impact of Traffic Density on Estimated Travel Time."""
    df = df.copy()
    df["traffic_density_bin"] = pd.cut(
        df["traffic_density"],
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1],
        labels=["Very Low", "Low", "Medium", "High", "Very High"],
    )

    traffic_time = (
        df.groupby("traffic_density_bin")["estimated_travel_time_hr"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        traffic_time,
        x="traffic_density_bin",
        y="estimated_travel_time_hr",
        markers=True,
        title="Impact of Traffic Density on Estimated Travel Time",
        labels={
            "traffic_density_bin": "Traffic Density Level",
            "estimated_travel_time_hr": "Average Travel Time (hours)",
        },
    )

    fig.update_layout(
        title_x=0.5,
        xaxis_title="Traffic Density Level",
        yaxis_title="Average Travel Time (Hours)",
    )
    return fig


def build_demand_heatmap(df: pd.DataFrame) -> go.Figure:
    """Density heatmap: Travel Demand (Day Type vs Season) with transport animation."""
    fig = px.density_heatmap(
        df,
        x="season",
        y="day_type",
        z="popularity_score",
        histfunc="avg",
        animation_frame="transport_mode",
        text_auto=True,
        title="Heatmap of Travel Demand (Day Type vs Season)",
        color_continuous_scale=[
            [0, "#f7fbff"],
            [0.2, "#c6dbef"],
            [0.4, "#6baed6"],
            [0.6, "#3182bd"],
            [0.8, "#08519c"],
            [1, "#08306b"],
        ],
    )

    # Match notebook behaviour (remove animation buttons, keep slider)
    fig["layout"].pop("updatemenus", None)

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        xaxis_title="Season",
        yaxis_title="Day Type",
        coloraxis_colorbar=dict(title="Travel Demand"),
    )

    fig.update_traces(
        hovertemplate=(
            "Season: %{x}<br>"
            "Day Type: %{y}<br>"
            "Demand: %{z}<extra></extra>"
        )
    )
    return fig


def build_budget_satisfaction_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter: User Budget vs Satisfaction Rating by Transport Mode."""
    fig = px.scatter(
        df,
        x="user_budget",
        y="satisfaction_rating",
        color="transport_mode",
        symbol="season",
        title="User Budget vs Satisfaction Rating by Transport Mode",
        labels={
            "user_budget": "User Budget",
            "satisfaction_rating": "Satisfaction Rating",
            "transport_mode": "Transport Mode",
            "season": "Season",
        },
        color_discrete_map={
            "Car": "#1f77b4",
            "Train": "#2ca02c",
            "Bike": "#ff7f0e",
            "Walk": "#9467bd",
            "Bus": "#d62728",
        },
        hover_data=[
            "start_location",
            "end_location",
            "season",
            "transport_mode",
            "satisfaction_rating",
        ],
    )

    fig.update_layout(
        title_x=0.5,
        xaxis_title="User Budget",
        yaxis_title="Satisfaction Rating",
    )
    return fig


def build_cost_sankey(df: pd.DataFrame) -> go.Figure:
    """Sankey: Travel Cost Flow Distribution."""
    entry_fee = df["entry_fee"].mean()
    accommodation = df["accommodation_cost"].mean()
    food = df["food_cost"].mean()

    labels = [
        "Total Travel Cost",
        f"Entry Fee ({entry_fee:.2f})",
        f"Accommodation ({accommodation:.2f})",
        f"Food ({food:.2f})",
    ]

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=25,
                    thickness=30,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color=["#4C78A8", "#F58518", "#54A24B", "#B279A2"],
                ),
                link=dict(
                    source=[0, 0, 0],
                    target=[1, 2, 3],
                    value=[entry_fee, accommodation, food],
                    color=[
                        "rgba(245,133,24,0.5)",
                        "rgba(84,162,75,0.5)",
                        "rgba(178,121,162,0.5)",
                    ],
                ),
            )
        ]
    )

    fig.update_layout(
        title="Travel Cost Flow Distribution",
        font_size=13,
        width=900,
        height=500,
    )
    return fig


def build_travel_preference_sunburst(df: pd.DataFrame) -> go.Figure:
    """Sunburst: Season → Transport Mode → Destination Type."""
    sunburst_data = (
        df.groupby(["season", "transport_mode", "destination_type"])["popularity_score"]
        .sum()
        .reset_index()
    )

    season_order = ["Winter", "Spring", "Summer", "Monsoon", "Autumn"]

    sunburst_data["season"] = pd.Categorical(
        sunburst_data["season"],
        categories=season_order,
        ordered=True,
    )

    sunburst_data = sunburst_data.sort_values("season")

    fig = px.sunburst(
        sunburst_data,
        path=["season", "transport_mode", "destination_type"],
        values="popularity_score",
        color="season",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Travel Preference Hierarchy: Season → Transport Mode → Destination Type",
    )

    fig.update_layout(
        title_x=0.5,
        margin=dict(t=50, l=25, r=25, b=25),
        template="plotly_white",
    )

    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Popularity Score: %{value}<extra></extra>"
    )
    return fig


def build_transport_radar(df: pd.DataFrame) -> go.Figure:
    """Radar chart comparing transport modes across travel factors."""
    radar = df.groupby("transport_mode")[
        [
            "user_budget",
            "user_time_constraint_hr",
            "popularity_score",
            "traffic_density",
            "satisfaction_rating",
        ]
    ].mean()

    scaler = MinMaxScaler()
    radar_scaled = pd.DataFrame(
        scaler.fit_transform(radar),
        columns=radar.columns,
        index=radar.index,
    )

    categories = ["Budget", "Travel Time", "Popularity", "Traffic", "Satisfaction"]

    fig = go.Figure()

    for mode in radar_scaled.index:
        values = radar_scaled.loc[mode].tolist()
        values += values[:1]

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill="toself",
                line=dict(width=3),
                opacity=0.7,
                name=mode,
            )
        )

    fig.update_layout(
        title=dict(
            text="Traveler Preference Comparison",
            x=0.5,
            font=dict(size=22),
        ),
        polar=dict(
            bgcolor="#f7f7f7",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="lightgray",
                gridwidth=1,
            ),
            angularaxis=dict(gridcolor="lightgray"),
        ),
        width=900,
        height=700,
        legend=dict(
            x=1.05,
            y=1,
            font=dict(size=12),
        ),
    )
    return fig


def build_traffic_violin(df: pd.DataFrame) -> go.Figure:
    """Violin: Traffic density distribution by day_type."""
    fig = px.violin(
        df,
        x="day_type",
        y="traffic_density",
        color="day_type",
        box=True,
        points="all",
        color_discrete_sequence=["#00A8E8", "#FF6B6B"],
    )

    fig.update_layout(
        title={
            "text": "Traffic Density Distribution: Weekdays vs Weekends",
            "x": 0.5,
            "xanchor": "center",
            "font": dict(size=24),
        },
        xaxis_title="Day Type",
        yaxis_title="Traffic Density",
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=14),
        xaxis=dict(showgrid=False, linecolor="black"),
        yaxis=dict(gridcolor="lightgray"),
        legend_title="Day Type",
    )

    fig.update_traces(opacity=0.75)
    return fig


def build_route_map(df: pd.DataFrame) -> folium.Map:
    """Folium map: India route visualisation — exact replica of notebook code."""
    city_coords = {
        "Delhi": (28.6139, 77.2090),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Chennai": (13.0827, 80.2707),
        "Kolkata": (22.5726, 88.3639),
        "Agra": (27.1767, 78.0081),
        "Goa": (15.2993, 74.1240),
        "Shimla": (31.1048, 77.1734),
        "Ooty": (11.4064, 76.6932),
        "Mahabalipuram": (12.6208, 80.1937),
    }

    df = df.copy()
    df["start_lat"] = df["start_location"].map(lambda x: city_coords.get(x, (None, None))[0])
    df["start_lon"] = df["start_location"].map(lambda x: city_coords.get(x, (None, None))[1])
    df["end_lat"] = df["end_location"].map(lambda x: city_coords.get(x, (None, None))[0])
    df["end_lon"] = df["end_location"].map(lambda x: city_coords.get(x, (None, None))[1])

    m = folium.Map(location=[22.5, 80], zoom_start=5, tiles="cartodbpositron")

    mode_colors = {
        "car": "blue",
        "train": "green",
        "bike": "orange",
        "walk": "purple",
        "bus": "brown",
    }

    for _, row in df.iterrows():
        if pd.notnull(row["start_lat"]) and pd.notnull(row["end_lat"]):
            start = (row["start_lat"], row["start_lon"])
            end = (row["end_lat"], row["end_lon"])
            color = mode_colors.get(str(row["transport_mode"]).lower(), "black")

            folium.PolyLine(
                locations=[start, end],
                color=color,
                weight=3,
                opacity=0.8,
                tooltip=f"{row['start_location']} → {row['end_location']} ({row['transport_mode']})",
            ).add_to(m)

            folium.CircleMarker(
                location=start,
                radius=row["popularity_score"] / 20,
                color="blue",
                fill=True,
                fill_opacity=0.7,
                popup=f"Start: {row['start_location']}",
            ).add_to(m)

            folium.CircleMarker(
                location=end,
                radius=row["popularity_score"] / 20,
                color="orange",
                fill=True,
                fill_opacity=0.7,
                popup=f"End: {row['end_location']}",
            ).add_to(m)

    return m


def main():
    st.set_page_config(
        page_title="SmartTour Route Visualization Dashboard",
        layout="wide",
    )

    st.title("SmartTour Route Visualization Dashboard")
    st.markdown(
        "Interactive overview of SmartTour routes, demand patterns, costs, and traveler preferences."
    )

    df = load_data()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🚦 Traffic & Time",
            "📊 Demand & Preferences",
            "💰 Budget & Satisfaction",
            "🔀 Cost Breakdown",
            "🗺️ Route Map",
        ]
    )

    with tab1:
        st.plotly_chart(build_traffic_time_line(df), use_container_width=True)
        st.plotly_chart(build_traffic_violin(df), use_container_width=True)

    with tab2:
        st.plotly_chart(build_demand_heatmap(df), use_container_width=True)
        st.plotly_chart(build_travel_preference_sunburst(df), use_container_width=True)

    with tab3:
        st.plotly_chart(build_budget_satisfaction_scatter(df), use_container_width=True)
        st.plotly_chart(build_transport_radar(df), use_container_width=True)

    with tab4:
        st.plotly_chart(build_cost_sankey(df), use_container_width=True)

    with tab5:
        st.subheader("India Travel Route Map")
        st.markdown(
            "Routes are colour-coded by transport mode: "
            "🔵 Car · 🟢 Train · 🟠 Bike · 🟣 Walk · 🟤 Bus"
        )
        m = build_route_map(df)
        st_folium(m, width=900, height=600)


if __name__ == "__main__":
    main()

