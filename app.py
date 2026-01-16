import streamlit as st
import requests
from streamlit.components.v1 import html

st.set_page_config(layout="wide")
st.title("🗺️ Retail Location Intelligence (MVP)")

MAPPLS_KEY = st.secrets["MAPPLS_KEY"]

# Sidebar
city = st.sidebar.selectbox("City", ["Bangalore", "Mumbai", "Delhi"])

# 🔧 FIX 1: Mappls-friendly categories
category = st.sidebar.selectbox(
    "Category",
    ["beauty", "salon", "mall", "shopping"]
)

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
col1, col2, col3 = st.columns(3)
col1.metric("POIs Found", len(pois))
col2.metric("Competition Score", round(len(pois) / 10, 2))
col3.metric("Demand Score", min(10, len(pois) * 0.2))

# Build JS for markers & heatmap
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

# 🔧 FIX 2: Delayed Mappls SDK loading (Streamlit Cloud fix)
map_html = f"""
<div id="map" style="width:100%; height:600px;"></div>

<script>
function loadMappls() {{
  var script = document.createElement("script");
  script.src = "https://apis.mappls.com/advancedmaps/api/{MAPPLS_KEY}/map_sdk?layer=vector";
  script.onload = function() {{
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
  }};
  document.body.appendChild(script);
}}

setTimeout(loadMappls, 1500);
</script>
"""

html(map_html, height=650)
