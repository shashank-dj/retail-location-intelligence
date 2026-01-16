import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Retail Location Intelligence (Map-less MVP)")

MAPPLS_KEY = st.secrets["MAPPLS_KEY"]

# ---------------- Sidebar ----------------
city = st.sidebar.selectbox("City", ["Bangalore", "Mumbai", "Delhi"])
category = st.sidebar.selectbox(
    "Business Category",
    ["beauty", "salon", "mall", "restaurant", "shopping"]
)
radius = st.sidebar.slider("Catchment Radius (meters)", 500, 3000, 1500)

city_coords = {
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090)
}

lat, lng = city_coords[city]

# ---------------- Mappls API (CORRECT AUTH) ----------------
def fetch_pois(query, lat, lng, radius):
    url = "https://atlas.mappls.com/api/places/search/json"

    headers = {
        "X-Mappls-REST-Key": MAPPLS_KEY
    }

    params = {
        "query": query,
        "location": f"{lat},{lng}",
        "radius": radius
    }

    r = requests.get(url, headers=headers, params=params, timeout=10)

    # ---- DEBUG PROOF (for demo) ----
    st.write(f"API Status for '{query}':", r.status_code)

    data = r.json()
    return data.get("suggestedLocations", [])

# ---------------- Data Fetch ----------------
business_pois = fetch_pois(category, lat, lng, radius)
restaurants = fetch_pois("restaurant", lat, lng, radius)
malls = fetch_pois("mall", lat, lng, radius)
gyms = fetch_pois("gym", lat, lng, radius)

# ---------------- Metrics ----------------
competition_count = len(business_pois)

demand_score = (
    len(restaurants) * 2 +
    len(malls) * 3 +
    len(gyms) * 1
)

accessibility_score = round(
    (len(restaurants) + len(malls) + len(gyms)) / (radius / 1000), 2
)

final_score = round(
    (demand_score * 0.4) +
    (accessibility_score * 0.3) -
    (competition_count * 0.3),
    2
)

# ---------------- KPI Cards ----------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Competitors Nearby", competition_count)
c2.metric("Demand Score", demand_score)
c3.metric("Accessibility Score", accessibility_score)
c4.metric("Final Location Score", final_score)

# ---------------- Recommendation ----------------
st.subheader("📍 Location Recommendation")

if final_score >= 8:
    st.success("✅ STRONG LOCATION – High demand, manageable competition")
elif final_score >= 6:
    st.warning("⚠️ MODERATE LOCATION – Viable with differentiation")
else:
    st.error("❌ WEAK LOCATION – High risk, low return")

# ---------------- Ecosystem Breakdown ----------------
st.subheader("🏙️ Nearby Ecosystem (within radius)")

eco_df = pd.DataFrame({
    "POI Type": ["Restaurants", "Malls", "Gyms", f"{category.title()} (Competitors)"],
    "Count": [
        len(restaurants),
        len(malls),
        len(gyms),
        competition_count
    ]
})

st.dataframe(eco_df, use_container_width=True)

# ---------------- Sample POIs ----------------
st.subheader("📌 Sample Nearby Places (from Mappls API)")

sample = business_pois[:10]

if sample:
    sample_df = pd.DataFrame(sample)[["placeName", "address"]]
    st.dataframe(sample_df, use_container_width=True)
else:
    st.info("No POIs returned. Try increasing radius or changing category.")

# ---------------- Key Validation ----------------
st.divider()
st.caption(
    "✅ Data above is fetched live using Mappls Places REST API "
    "with X-Mappls-REST-Key authentication."
)
