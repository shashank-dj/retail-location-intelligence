import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("🗺️ Retail Location Intelligence (MVP)")

MAPPLS_KEY = st.secrets["MAPPLS_KEY"]

# Sidebar
city = st.sidebar.selectbox("City", ["Bangalore", "Mumbai", "Delhi"])
category = st.sidebar.selectbox("Category", ["beauty", "salon", "mall", "shopping"])
radius = st.sidebar.slider("Radius (meters)", 500, 3000, 1500)

city_coords = {
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090)
}

lat, lng = city_coords[city]

# Fetch POIs
def fetch_pois(query, lat, lng, radius):
    url = "https://atlas.mappls.com/api/places/search/json"
    params = {
        "query": query,
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": MAPPLS_KEY
    }
    res = requests.get(url, params=params)
    return res.json().get("suggestedLocations", [])

pois = fetch_pois(category, lat, lng, radius)

# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("POIs Found", len(pois))
c2.metric("Competition Score", round(len(pois) / 10, 2))
c3.metric("Demand Score", min(10, len(pois) * 0.2))

# Build JS markers
markers_js = ""
heatmap_js = ""

for p in pois:
    markers_js += f"""
    new mappls.Marker({{
        map: map,
        position: [{p['latitude']}, {p['longitude']}],
        title: "{p['placeName']}"
    }});
    """
    heatmap_js += f"""
    heatData.push({{
        lat: {p['latitude']},
        lng: {p['longitude']},
        count: 1
    }});
    """

# ✅ IFRAME-BASED MAP (KEY FIX)
map_iframe = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    html, body, #map {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
    }}
  </style>
</head>
<body>

<div id="map"></div>

<script src="https://apis.mappls.com/advancedmaps/api/{MAPPLS_KEY}/map_sdk?layer=vector"></script>
<script>
  var map = new mappls.Map("map", {{
    center: [{lat}, {lng}],
    zoom: 13
  }});

  {markers_js}

  var heatData = [];
  {heatmap_js}

  mappls.HeatmapLayer({{
    map: map,
    data: heatData,
    radius: 40
  }});
</script>

</body>
</html>
"""

st.components.v1.iframe(
    srcdoc=map_iframe,
    height=650,
    scrolling=False
)
