import branca.colormap as cm
import folium
import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Point, Polygon
from geopandas import GeoDataFrame
from scipy.stats import chisquare
import math

# Define the city name
city_name = "Almaty"

# Get the city boundary as a GeoDataFrame using the city name
city_boundary_gdf = ox.geocode_to_gdf(city_name)

# Extract the polygon from the GeoDataFrame
city_boundary_polygon = city_boundary_gdf['geometry'].iloc[0]

G = ox.graph_from_polygon(city_boundary_polygon, network_type="walk", simplify=True)

gdf_nodes = ox.graph_to_gdfs(G, edges=False)

#Folium colormap
m = folium.Map(
    location=[43.242542214050474, 76.90496387893451],
    zoom_start=15,
    prefer_canvas=True,
)

for index, val in gdf_nodes.iterrows():
    folium.Circle(
        location=[val["y"], val["x"]],
        radius=10,
        stroke=False,
        fill=True,
        fill_opacity=0.5,
        interactive=True,
    ).add_to(m)

bike_data = pd.read_csv("almaty.csv") #Read bike data

def is_within_boundary(row):
    point = Point(row['lon'], row['lat'])
    return city_boundary_polygon.contains(point)  # Use city_boundary_polygon instead of city_boundary

bike_data['within_boundary'] = bike_data.apply(is_within_boundary, axis=1)
bike_data = bike_data[bike_data['within_boundary']]

# Function to find the nearest node for a given location
def get_nearest_node(lon, lat, graph):
    return ox.distance.nearest_nodes(graph, lon, lat)

# Finding the nearest nodes for each bike station
bike_data['nearest_node'] = bike_data.apply(lambda row: get_nearest_node(row['lon'], row['lat'], G), axis=1)

WALKING_SPEED_KMH = 4.5  # Average walking speed in km/h
from matplotlib.colors import LinearSegmentedColormap

# Create a custom "Reds" colormap
cmap = LinearSegmentedColormap.from_list("", ["yellow", "green", "red"])

# Constants for trip times and travel speed
trip_times = [5, 10, 15]  # in minutes
travel_speed = WALKING_SPEED_KMH  # walking speed in km/hour

# Add an edge attribute for time in minutes required to traverse each edge
meters_per_minute = travel_speed * 1000 / 60  # km per hour to m per minute
for orig, dest, data in G.edges(data=True):
    data["time"] = data["length"] / meters_per_minute

# Creating a new Folium map
m = folium.Map(
    location=[43.242542214050474, 76.90496387893451],
    zoom_start=15,
    prefer_canvas=False,
)

# Add city boundary to the map
folium.GeoJson(
    city_boundary_polygon,
    style_function=lambda x: {'fillColor': 'none', 'color': 'blue', 'weight': 2, 'fillOpacity': 0.5}
).add_to(m)

m

from shapely.geometry import MultiPoint

from shapely.geometry import MultiPolygon
import matplotlib.cm as cm
import matplotlib.colors as colors

# Create isochrone polygons for each bike station
for index, row in bike_data.iterrows():
    # Create a FeatureGroup for each bike station
    bike_station_group = folium.FeatureGroup(name=row['Station'])

    center_node = row['nearest_node']
    prev_polygon = None
    for trip_time in sorted(trip_times):
        subgraph = nx.ego_graph(G, center_node, radius=trip_time, distance="time")
        node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
        bounding_poly = MultiPoint(node_points).convex_hull

        # Intersect the bounding_poly with the city_boundary to keep only the land area
        bounding_poly = bounding_poly.intersection(city_boundary_polygon)

        # Get the color from the colormap
        color = colors.to_hex(cmap(trip_time / max(trip_times)))

        # If there is a previous polygon, subtract it to create a ring
        if prev_polygon:
            bounding_poly = bounding_poly.difference(prev_polygon)

        # Add the modified polygon to the bike station group
        folium.GeoJson(
            bounding_poly,
            style_function=lambda x: {'fillColor': color, 'color': color, 'weight': 1, 'fillOpacity': 1}
        ).add_to(bike_station_group)

        # Keep track of the previous polygon
        prev_polygon = MultiPoint(node_points).convex_hull

    # Add bike station marker to the group
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(str(row['Station']), parse_html=True),  # Ensure that the station name is a string
        icon=folium.Icon(icon="bicycle", prefix="fa")  # Removed icon_size as it's not a standard argument for folium.Icon
    ).add_to(bike_station_group)


    # Add the bike station group to the map
    bike_station_group.add_to(m)

# Add a layer control to the map
folium.LayerControl().add_to(m)


# Display the map
m

# getting shape files
import geopandas as gpd

# Create a list to store all 5-minute polygons
polygons_5_min = []

for index, row in bike_data.iterrows():
    center_node = row['nearest_node']
    subgraph = nx.ego_graph(G, center_node, radius=5, distance="time")
    node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
    polygon = MultiPoint(node_points).convex_hull
    polygons_5_min.append(polygon)

# Create a map for 5 minutes area
m_5_min = folium.Map(
    location=[-8.060643100595167, -34.88794851639232], # Adjust this to the center of your city
    zoom_start=15,
    prefer_canvas=True,
)

# Iterate through the 5-minute polygons and add them individually to the map
for polygon in polygons_5_min:
    folium.GeoJson(polygon, style_function=lambda x: {'fillColor': 'lightpink', 'color': 'red', 'weight': 2, 'fillOpacity': 0.6}).add_to(m_5_min)

m_5_min

output_path = "./shapefiles/City"

# Filter out non-polygon geometries
polygons_5_min_filtered = [p for p in polygons_5_min if p.geom_type == 'Polygon']

# Convert the filtered list to a GeoDataFrame
gdf_5_min = gpd.GeoDataFrame(geometry=polygons_5_min_filtered)

# Export to GeoJSON
gdf_5_min.to_file(os.path.join(output_path, "polygons_5_min.geojson"), driver="GeoJSON")

# Export to Shapefile
gdf_5_min.to_file(os.path.join(output_path, "polygons_5_min.shp"))

########### 10 minutes

# Create a list to store all 10-minute polygons
polygons_10_min = []

for index, row in bike_data.iterrows():
    center_node = row['nearest_node']
    subgraph = nx.ego_graph(G, center_node, radius=10, distance="time")
    node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
    polygon = MultiPoint(node_points).convex_hull
    polygons_10_min.append(polygon)

# Create a map for 10 minutes area
m_10_min = folium.Map(
    location=[51.51345096041899, -0.12686340657065237], # Adjust this to the center of your city
    zoom_start=15,
    prefer_canvas=True,
)

# Iterate through the 10-minute polygons and add them individually to the map
for polygon in polygons_10_min:
    folium.GeoJson(polygon, style_function=lambda x: {'fillColor': 'yellow', 'color': 'red', 'weight': 1, 'fillOpacity': 0.6}).add_to(m_10_min)

# Show the map
m_10_min

# Convert the polygons_10_min list to a GeoDataFrame
gdf_10_min = gpd.GeoDataFrame(geometry=polygons_10_min)

# Export to GeoJSON
gdf_10_min.to_file(os.path.join(output_path, "polygons_10_min.geojson"), driver="GeoJSON")

# Export to Shapefile
gdf_10_min.to_file(os.path.join(output_path, "polygons_10_min.shp"))

########### 15 minutes

# Create a list to store all 15-minute polygons
polygons_15_min = []

for index, row in bike_data.iterrows():
    center_node = row['nearest_node']
    subgraph = nx.ego_graph(G, center_node, radius=15, distance="time")
    node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
    polygon = MultiPoint(node_points).convex_hull
    polygons_15_min.append(polygon)

# Create a map for 15 minutes area
m_15_min = folium.Map(
    location=[-8.060643100595167, -34.88794851639232], # Adjust this to the center of your city
    zoom_start=15,
    prefer_canvas=True,
)

# Iterate through the 15-minute polygons and add them individually to the map
for polygon in polygons_15_min:
    folium.GeoJson(polygon, style_function=lambda x: {'fillColor': 'blue', 'color': 'red', 'weight': 1, 'fillOpacity': 0.6}).add_to(m_15_min)

# Show the map
m_15_min

# Convert the polygons_15_min list to a GeoDataFrame
gdf_15_min = gpd.GeoDataFrame(geometry=polygons_15_min)

# Export to GeoJSON
gdf_15_min.to_file(os.path.join(output_path, "polygons_15_min.geojson"), driver="GeoJSON")

# Export to Shapefile
gdf_15_min.to_file(os.path.join(output_path, "polygons_15_min.shp"))
