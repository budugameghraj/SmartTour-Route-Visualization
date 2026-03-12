# SmartTour Route Visualization Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://budugameghraj-smarttour-route-visualization-dashboard.streamlit.app)

> 🔗 **Live demo:** https://budugameghraj-smarttour-route-visualization-dashboard.streamlit.app
> *(Replace this URL with your actual Streamlit app URL once deployment is complete)*

An interactive dashboard for exploring smart tour routes across India, built with **Streamlit** and **Plotly**.

## Features

The dashboard contains **5 interactive tabs**:

| Tab | Content |
|-----|---------|
| 🚦 Traffic & Time | Line chart — Impact of Traffic Density on Estimated Travel Time · Violin chart — Traffic density distribution by day type |
| 📊 Demand & Preferences | Animated density heatmap — Travel Demand by Day Type & Season · Sunburst — Season → Transport Mode → Destination Type |
| 💰 Budget & Satisfaction | Scatter — User Budget vs Satisfaction Rating by Transport Mode · Radar — Traveler Preference Comparison across transport modes |
| 🔀 Cost Breakdown | Sankey — Travel Cost Flow Distribution (Entry Fee, Accommodation, Food) |
| 🗺️ Route Map | Interactive Folium map of India showing all routes colour-coded by transport mode |

## Dataset

`SmartTourRoutePlanner.csv` — 500 rows, 19 columns covering routes, costs, ratings, and travel preferences across 10 Indian cities.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub (public repo).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**.
4. Select your repository, branch (`main`), and set the main file path to `dashboard.py`.
5. Click **Deploy** — your dashboard will be live within a minute at a URL like `https://your-username-smarttour.streamlit.app`.

Streamlit Community Cloud automatically re-deploys on every push to `main`.

## Project Structure

```
SmartTour-Route-Visualization/
├── dashboard.py               # Streamlit dashboard (all charts + map)
├── SmartTourRoutePlanner.csv  # Dataset (500 rows, 19 columns)
├── SmartTourRoutePlan.ipynb   # Original analysis notebook
├── travel_route_map.html      # Static Folium map export
├── requirements.txt           # Python dependencies
└── .streamlit/
    └── config.toml            # Streamlit theme & server config
```
