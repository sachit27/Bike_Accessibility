import osmnx as ox
import pandas as pd
import networkx as nx
from shapely.geometry import Point
import numpy as np
import os
import warnings
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
from pyproj import CRS
import seaborn as sns
import geopandas as gpd

city_names = [
    'Almaty', 'Austin', 'Bergen', 'Bern','Dortmund', 'Exeter', 'Gent',
    'Glasgow City', 'Guadalajara', 'Hamilton', 'Hiroshima', 'Innsbruck', 'Los Angeles', 'Lausanne',
    'Lisbon', 'London', 'Lugano', 'Luzern', 'Mexico City', 'Madrid', 'Manhattan', 'Marseille',
    'Milan', 'Montreal', 'Naha', 'Nice', 'Oslo', 'Philadelphia',
    'Portland', 'Riga', 'Rio de Janeiro', 'Rosario', 'San Antonio', 'Taipei', 'Toronto', 'Turku',
    'Washington', 'Zurich', 'Osaka Prefecture', 'Bogota'
]

file_names = [
    'almaty', 'austin', 'bergen', 'bern','dortmund', 'exeter', 'gent',
    'glasgow','guadalajara', 'hamilton', 'hiroshima', 'innsbruck', 'los angeles', 'lausanne',
    'lisbon', 'london', 'lugano', 'luzern', 'mexico city', 'madrid', 'manhattan', 'marseille',
    'milan', 'montreal', 'naha', 'nice', 'oslo', 'philadelphia',
    'portland', 'riga', 'rio de janeiro', 'rosario', 'sanantonio', 'taipei', 'toronto', 'turku',
    'washington', 'zurich', 'osaka', 'bogota'
]

def get_utm_epsg(lat, lon):
    """
    Calculate UTM zone and its EPSG code from latitude and longitude.
    """
    utm_band = str(int((np.floor((lon + 180) / 6) % 60) + 1))
    if len(utm_band) == 1:
        utm_band = '0' + utm_band
    if lat >= 0:
        epsg_code = f"326{utm_band}"  # Northern hemisphere
    else:
        epsg_code = f"327{utm_band}"  # Southern hemisphere
    return epsg_code


warnings.filterwarnings("ignore")
# Assuming 'city_names' and 'file_names' are defined
median_distances = {}

for city_name, file_name in zip(city_names, file_names):
    # Download the boundary of the city as a polygon
    city_boundary = ox.geocode_to_gdf(city_name)

    # Approximate central point of the city boundary
    center_point = city_boundary.geometry.centroid.iloc[0]
    lat, lon = center_point.y, center_point.x

    # Determine the EPSG code for the UTM zone of the city
    epsg_code = get_utm_epsg(lat, lon)

    # Reproject the city boundary to the determined UTM zone
    city_boundary = city_boundary.to_crs(epsg=epsg_code)

    # Download and reproject public transit stops
    public_transit_stops = ox.geometries_from_place(city_name, tags={
        'public_transport': ['station', 'stop_area'],
        'railway': 'station',
        'highway': 'bus_stop'
    }).to_crs(epsg=epsg_code)

    # Filter to point geometries and within the city boundary
    public_transit_stops = public_transit_stops[public_transit_stops.geometry.geom_type == 'Point']
    public_transit_stops = gpd.sjoin(public_transit_stops, city_boundary, how="inner", op='intersects').drop(columns=['index_right'])

    # Load, convert, and reproject bike station data
    df = pd.read_csv(f'{file_name}.csv')
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs='EPSG:4326').to_crs(epsg=epsg_code)
    df = gpd.sjoin(df, city_boundary, how="inner", op='intersects').drop(columns=['index_right'])

    # Calculate distances and median
    nearest_stop_distance_m = df.geometry.apply(lambda x: public_transit_stops.geometry.distance(x).min())
    median_distances[city_name] = nearest_stop_distance_m.median()

median_distances = pd.Series(median_distances)


# New DataFrame to collect all distances
all_distances = []

for city_name, file_name in zip(city_names, file_names):
    city_boundary = ox.geocode_to_gdf(city_name)

    # Approximate central point of the city boundary
    center_point = city_boundary.geometry.centroid.iloc[0]
    lat, lon = center_point.y, center_point.x

    # Determine the EPSG code for the UTM zone of the city
    epsg_code = get_utm_epsg(lat, lon)

    # Reproject the city boundary to the determined UTM zone
    city_boundary = city_boundary.to_crs(epsg=epsg_code)

    # Download and reproject public transit stops
    public_transit_stops = ox.geometries_from_place(city_name, tags={
        'public_transport': ['station', 'stop_area'],
        'railway': 'station',
        'highway': 'bus_stop'
    }).to_crs(epsg=epsg_code)

    # Filter to point geometries and within the city boundary
    public_transit_stops = public_transit_stops[public_transit_stops.geometry.geom_type == 'Point']
    public_transit_stops = gpd.sjoin(public_transit_stops, city_boundary, how="inner", op='intersects').drop(columns=['index_right'])

    # Load, convert, and reproject bike station data
    df = pd.read_csv(f'{file_name}.csv')
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs='EPSG:4326').to_crs(epsg=epsg_code)
    df = gpd.sjoin(df, city_boundary, how="inner", op='intersects').drop(columns=['index_right'])


    # After filtering to points within the city's boundary, calculate individual distances
    df['nearest_stop_distance_m'] = df.geometry.apply(lambda x: public_transit_stops.geometry.distance(x).min())

    # Create a temporary DataFrame to store distances for the current city
    temp_df = pd.DataFrame({
        'City': city_name,
        'Distance': df['nearest_stop_distance_m']
    })

    # Append the temporary DataFrame to the list
    all_distances.append(temp_df)

# Concatenate all the temporary DataFrames to create a comprehensive DataFrame
distance_data = pd.concat(all_distances, ignore_index=True)

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Apply a log transformation to the 'Distance' column
# Note: Adding 1 to avoid log(0) which is undefined
distance_data['Log_Distance'] = np.log1p(distance_data['Distance'])

# Now we can plot the log-transformed distances
plt.figure(figsize=(12, 8))
sns.boxplot(x='City', y='Log_Distance', data=distance_data)
plt.xticks(rotation=90, fontsize=13)
#plt.title('Log-Transformed Distribution of Distances to Nearest Transit Stop by City')
plt.ylabel('Log Distance (log(meters))', fontsize=13)
plt.xlabel('')
plt.tight_layout()
#plt.savefig('log_distances_plot.png', dpi=400)
plt.show()

# Define the walking speed (in km/h) and time (in minutes)
walking_speed = 4.5
walking_time = 5

# Calculate the walking distance in kilometers
walking_distance_km = (walking_speed / 60) * walking_time

# Convert walking distance to meters for distance calculation in GeoPandas
walking_distance_m = walking_distance_km * 1000

# Initialize a dictionary to store the percentages for each city
percent_within_5min_walk = {}

for city_name, file_name in zip(city_names, file_names):
    city_boundary = ox.geocode_to_gdf(city_name)

    # Approximate central point of the city boundary
    center_point = city_boundary.geometry.centroid.iloc[0]
    lat, lon = center_point.y, center_point.x

    # Determine the EPSG code for the UTM zone of the city
    epsg_code = get_utm_epsg(lat, lon)

    # Reproject the city boundary to the determined UTM zone
    city_boundary = city_boundary.to_crs(epsg=epsg_code)

    # Download the locations of public transit stops and project them
    public_transit_stops = ox.geometries_from_place(city_name, tags={
        'public_transport': 'platform',
        'railway': ['station', 'tram_stop'],
        'bus': 'yes'
    })

    # Ensure CRS compatibility
    epsg_code = get_utm_epsg(center_point.y, center_point.x)  # Assuming get_utm_epsg() and center_point are defined as before
    public_transit_stops = public_transit_stops.to_crs(epsg=epsg_code)

    # Load and reproject bike station data
    df = pd.read_csv(f'{file_name}.csv')
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs='EPSG:4326').to_crs(epsg=epsg_code)

    # Filter bike stations to those within the city's boundary if not already filtered
    df = gpd.sjoin(df, city_boundary.to_crs(epsg=epsg_code), how="inner", op='intersects').drop(columns=['index_right'])

    # Calculate the distance to the nearest transit stop for each bike station
    df['nearest_stop_distance_m'] = df.geometry.apply(lambda x: public_transit_stops.geometry.distance(x).min())

    # Calculate the percentage of bike stations within the walking distance
    within_5min_walk = df[df['nearest_stop_distance_m'] <= walking_distance_m]
    percent_within = (len(within_5min_walk) / len(df)) * 100

    # Store the percentage for the city
    percent_within_5min_walk[city_name] = percent_within

# Convert the dictionary to a pandas Series for easier viewing and plotting
percent_within_5min_walk_series = pd.Series(percent_within_5min_walk)
