# Add the necessary imports
import pandas as pd
import folium
from branca.colormap import linear
from folium.plugins import MarkerCluster, MeasureControl
import geopy.distance

# Define file paths using raw strings
stationary_survey_path = r'data\stationary_platform_data.xlsx'
cruise_metadata_path = r'ECSAS_tables\tblCruise.xlsx'
watch_notes_path = r'ECSAS_tables\tblWatchNotes.xlsx'

# Load the stationary survey data file
stationary_survey = pd.read_excel(stationary_survey_path)

# Clean up StartTime column to extract only time
stationary_survey['StartTime'] = pd.to_datetime(stationary_survey['StartTime']).dt.time

# Clean up Date column to remove time component
stationary_survey['Date'] = pd.to_datetime(stationary_survey['Date']).dt.strftime('%Y-%m-%d')

# Load metadata from Excel files for additional cruise info
df_cruise = pd.read_excel(cruise_metadata_path)
watch_notes = pd.read_excel(watch_notes_path)

df_observer = pd.read_excel(r'ECSAS_tables\lkpObserver.xlsx')
df_platform = pd.read_excel(r'ECSAS_tables\lkpPlatform.xlsx')
df_company = pd.read_excel(r'ECSAS_tables\lkpCompany.xlsx')

# Merge metadata files to get observer, platform names, and watch notes
stationary_survey = pd.merge(stationary_survey, df_cruise[['CruiseID', 'Observer', 'PlatformName', 'Start Date', 'End Date', 'Company']], 
                             left_on='CruiseID', right_on='CruiseID', how='left')

stationary_survey = pd.merge(stationary_survey, watch_notes[['WatchID', 'Note']], 
                             left_on='WatchID', right_on='WatchID', how='left')

# Merge company details
stationary_survey = pd.merge(stationary_survey, df_company[['CompanyID', 'CompanyText']], 
                             left_on='Company', right_on='CompanyID', how='left')

# Aggregate species and counts for each WatchID
aggregated_data = stationary_survey.groupby('WatchID').agg({
    'LatStart': 'first', 
    'LongStart': 'first', 
    'Alpha': lambda x: x.dropna().tolist(),
    'Count': lambda x: x.dropna().tolist(),
    'Observer_x': 'first',  
    'PlatformName': 'first',
    'Date': 'first',
    'StartTime': 'first',
    'Note': 'first'
}).reset_index()

# Merge observer and platform names
aggregated_data = pd.merge(aggregated_data, df_observer[['ObserverID', 'ObserverName']], 
                           left_on='Observer_x', right_on='ObserverID', how='left')
aggregated_data = pd.merge(aggregated_data, df_platform[['PlatformID', 'PlatformText']], 
                           left_on='PlatformName', right_on='PlatformID', how='left')

# Calculate total birds observed per watch for color scaling points on our map
aggregated_data['TotalBirds'] = aggregated_data['Count'].apply(lambda x: sum(map(int, x)))

# Create a color scale for colors between the minimum and maximum number of birds
min_total_birds = aggregated_data['TotalBirds'].min()
max_total_birds = aggregated_data['TotalBirds'].max()
colormap = linear.YlOrRd_09.scale(min_total_birds, max_total_birds)
colormap.caption = 'Total Birds'

# Initialize the map
m = folium.Map(location=[47.569575, -52.698024], zoom_start=10)

# Create a MarkerCluster object
marker_cluster = MarkerCluster().add_to(m)

# Add survey points to the MarkerCluster object
for _, row in aggregated_data.iterrows():
    if row['Alpha']:
        # Create a table for species and counts, ELSE make a note there were no birds
        species_table = "<table style='width:100%; border-collapse: collapse; border: 1px solid #ddd;'><tr><th style='padding: 8px; border: 1px solid #ddd;'>Species</th><th style='padding: 8px; border: 1px solid #ddd;'>Count</th></tr>"
        for species, count in zip(row['Alpha'], row['Count']):
            species_table += f"<tr><td style='padding: 8px; border: 1px solid #ddd;'>{species}</td><td style='padding: 8px; border: 1px solid #ddd;'>{count}</td></tr>"
        species_table += "</table>"
    else:
        species_table = '<p>No birds observed during this watch</p>'
    
    # Find observer name and platform name
    observer_name = row['ObserverName']
    platform_name = row['PlatformText']

    # Construct popup HTML
    popup_html = f"""
<div style="font-family: Arial, sans-serif; width: 260px; text-align: left;">
    <h6 style="color: #008CBA; font-weight: bold;">WATCH AND SIGHTINGS INFO</h6>
    <p><strong>Watch ID:</strong> {row['WatchID']}</p>
    <p><strong>Date:</strong> {row['Date']}</p>
    <p><strong>Start Time:</strong> {row['StartTime']}</p>
    <p><strong>Watch Table: </strong> the count of seabird species sighted per watch</p>
    {species_table}
    <p><strong>Total birds:</strong> {sum(map(int, row['Count']))}</p>
    {"<p><strong>Observer's Notes:</strong> " + row['Note'] + "</p>" if pd.notnull(row['Note']) else ""}
</div>
"""

    popup = folium.Popup(popup_html, max_width=300)
    
    # Get color based on total birds
    color = colormap(row['TotalBirds'])
    
    # Create CircleMarker for each survey point
    folium.CircleMarker(
        location=[row['LatStart'], row['LongStart']],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=popup,
    ).add_to(marker_cluster)

# Add the colormap to the map
colormap.add_to(m)

# Function to add start/end port markers with cruise details
def add_port_marker(map_obj, start_coords, end_coords):
    # Fetch cruise details from df_cruise
    cruise_info = df_cruise.iloc[0]
    
    # Format popup HTML for port markers
    if start_coords == end_coords:
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 260px; text-align: left;">
            <h6 style="color: #008CBA; font-weight: bold;">Port: {cruise_info['PlatformName']}</h6>
            <p>Departed: {cruise_info['Start Date'].strftime('%Y-%m-%d')}</p>
            <p><strong>Cruise ID:</strong> {cruise_info['CruiseID']}</p>
            <p><strong>Company:</strong> {cruise_info['Company']}</p>
        </div>
        """
        # Create CircleMarker for start/end port
        folium.CircleMarker(
            location=start_coords,
            radius=4,
            color='#3186cc',  # Example color
            fill=True,
            fill_color='#3186cc',  # Example color
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(map_obj)
    else:
        # Format popup HTML for start and end ports separately
        start_popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 260px; text-align: left;">
            <h6 style="color: #008CBA; font-weight: bold;">Start Port: {cruise_info['PlatformName']}</h6>
            <p>Departed: {cruise_info['Start Date'].strftime('%Y-%m-%d')}</p>
            <p><strong>Cruise ID:</strong> {cruise_info['CruiseID']}</p>
            <p><strong>Company:</strong> {cruise_info['Company']}</p>
        </div>
        """
        end_popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 260px; text-align: left;">
            <h6 style="color: #008CBA; font-weight: bold;">End Port: {cruise_info['PlatformName']}</h6>
            <p>Arrived: {cruise_info['End Date'].strftime('%Y-%m-%d')}</p>
            <p><strong>Cruise ID:</strong> {cruise_info['CruiseID']}</p>
            <p><strong>Company:</strong> {cruise_info['Company']}</p>
        </div>
        """
        
        # Create CircleMarker for start port
        folium.CircleMarker(
            location=start_coords,
            radius=4,
            color='#3186cc',  # Example color
            fill=True,
            fill_color='#3186cc',  # Example color
            fill_opacity=0.7,
            popup=folium.Popup(start_popup_html, max_width=300),
        ).add_to(map_obj)
        
        # Create CircleMarker for end port
        folium.CircleMarker(
            location=end_coords,
            radius=4,
            color='#3186cc',  # Example color
            fill=True,
            fill_color='#3186cc',  # Example color
            fill_opacity=0.7,
            popup=folium.Popup(end_popup_html, max_width=300),
        ).add_to(map_obj)

start_coords = [47.569575, -52.698024]
end_coords = [47.569575, -52.698024]

add_port_marker(m, start_coords, end_coords)

# Add measure control to the map
measure_control = MeasureControl(
    position='topright',
    primary_length_unit='kilometers',
    secondary_length_unit='miles',
    primary_area_unit='sqmeters',
    secondary_area_unit='acres'
)
m.add_child(measure_control)

# Function to add a grid overlay
def add_grid(map_obj, start_coords, end_coords, grid_size_km=10):
        
    lat_start, lon_start = start_coords
    lat_end, lon_end = end_coords
    
    lat_steps = abs(lat_end - lat_start) / (grid_size_km / 110.574)
    lon_steps = abs(lon_end - lon_start) / (grid_size_km / (111.320 * abs(lat_start)))
    
    # Add latitude lines
    for i in range(int(lat_steps) + 1):
        lat = lat_start + i * (grid_size_km / 110.574)
        folium.PolyLine(locations=[(lat, lon_start), (lat, lon_end)], color='black', weight=0.5).add_to(map_obj)
    
    # Add longitude lines
    for j in range(int(lon_steps) + 1):
        lon = lon_start + j * (grid_size_km / (111.320 * abs(lat_start)))
        folium.PolyLine(locations=[(lat_start, lon), (lat_end, lon)], color='black', weight=0.5).add_to(map_obj)

# Add grid overlay to the map
add_grid(m, start_coords, end_coords, grid_size_km=10)

# Save the map to an HTML file
m.save(r'figures/survey_map.html')

print("Map has been created and saved as 'survey_map.html'. Open this file in a web browser to view the map.")