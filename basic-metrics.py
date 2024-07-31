#####################################################
###############   BASIC METRICS   ###################
"""
I start by making a table to show some basic metrics on the stationary and moving platform surveys.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from prettytable import PrettyTable

# Define file paths using raw string literals
stationary_survey_path = r'C:\Users\BoschJ\Desktop\ECSAS_analysis\data\stationary_platform_data.xlsx'
moving_survey_path = r'C:\Users\BoschJ\Desktop\ECSAS_analysis\data\moving_platform_data.xlsx'

# Load the stationary and moving survey data
stationary_survey = pd.read_excel(stationary_survey_path)
moving_survey = pd.read_excel(moving_survey_path)

# Convert the 'Date' column to datetime format in both moving and stationary survey DataFrames
moving_survey['Date'] = pd.to_datetime(moving_survey['Date'])
stationary_survey['Date'] = pd.to_datetime(stationary_survey['Date'])

# Find the minimum and maximum dates in the 'Date' column of both DataFrames to determine the cruise start and end dates
cruise_start_date = min(moving_survey['Date'].min(), stationary_survey['Date'].min())
cruise_end_date = max(moving_survey['Date'].max(), stationary_survey['Date'].max())

# Calculate the duration of the cruise in days
cruise_duration_days = (cruise_end_date - cruise_start_date).days + 1  # Add 1 to include both start and end dates

# Calculate the total number of watches conducted for moving and stationary platforms
total_surveys_moving = moving_survey['WatchID'].nunique()
total_surveys_stationary = stationary_survey['WatchID'].nunique()

# Calculate the total number of different species observed in moving and stationary surveys respectively
total_species_moving = moving_survey['Alpha'].nunique()
total_species_stationary = stationary_survey['Alpha'].nunique()

# Count occurrences of each species for the moving platform survey
moving_species_counts = moving_survey.groupby('Alpha')['Count'].sum()

# Identify the species with the highest and lowest count in the moving survey
most_seen_moving_species = moving_species_counts.idxmax()  # Get the species name with the maximum count
most_seen_moving_count = moving_species_counts.max()       # Get the maximum count

least_seen_moving_species = moving_species_counts.idxmin()  # Get the species name with the minimum count
least_seen_moving_count = moving_species_counts.min()       # Get the minimum count


# Count occurrences of each species for the stationary platform survey
stationary_species_counts = stationary_survey.groupby('Alpha')['Count'].sum()

# Identify the species with the highest and lowest count in the stationary survey
most_seen_stationary_species = stationary_species_counts.idxmax()  # Get the species name with the maximum count
most_seen_stationary_count = stationary_species_counts.max()       # Get the maximum count

least_seen_stationary_species = stationary_species_counts.idxmin()  # Get the species name with the minimum count
least_seen_stationary_count = stationary_species_counts.min()       # Get the minimum count

# Load metadata from Excel files for additional cruise info
df_cruise = pd.read_excel(r'C:\Users\BoschJ\Desktop\ECSAS_analytics_app\ECSAS_tables\tblCruise.xlsx')
df_platform = pd.read_excel(r'C:\Users\BoschJ\Desktop\ECSAS_analytics_app\ECSAS_tables\lkpPlatform.xlsx')
df_observer = pd.read_excel(r'C:\Users\BoschJ\Desktop\ECSAS_analytics_app\ECSAS_tables\lkpObserver.xlsx')

# Specify the CruiseID for my cruise
cruise_id = 1715529814

# Extract relevant info for the specified CruiseID
cruise_info = df_cruise[df_cruise['CruiseID'] == cruise_id].iloc[0]  # assuming CruiseID is unique

# Get Observer and platform names
observer_id = cruise_info['Observer']
observer_name = df_observer[df_observer['ObserverID'] == observer_id]['ObserverName'].iloc[0]

platform_id = cruise_info['PlatformName']
platform_name = df_platform[df_platform['PlatformID'] == platform_id]['PlatformText'].iloc[0]


########################################
#Haversine function to calculate distance

# Define the Haversine function to calculate distance between two points on the Earth
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)) 
    km = 6371 * c # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return km

# Port coordinates
start_coords = [47.569575, -52.698024]

# Calculate the distance from the port to each watch point
stationary_survey['DistanceFromPort'] = stationary_survey.apply(
    lambda row: haversine(start_coords[1], start_coords[0], row['LongStart'], row['LatStart']), axis=1
)

# Identify the furthest watch point
furthest_watch_point = stationary_survey.loc[stationary_survey['DistanceFromPort'].idxmax()]

# Display the furthest watch point and the distance
furthest_distance = furthest_watch_point['DistanceFromPort']
furthest_watch_point_data = furthest_watch_point[['WatchID', 'LatStart', 'LongStart', 'DistanceFromPort']]

# Create a PrettyTable object
results_table = PrettyTable()

# Add columns
results_table.field_names = ["Metric", "Moving Platforms", "Stationary Platforms"]

# Add data rows
results_table.add_row(["", "", ""])  # Add an empty row with placeholders

results_table.add_row(["Total surveys conducted", total_surveys_moving, total_surveys_stationary])
results_table.add_row(["Species or bird types observed", total_species_moving, total_species_stationary])

results_table.add_row(["", "", ""])  # Add an empty row with placeholders

results_table.add_row(["Most seen species", most_seen_moving_species, most_seen_stationary_species])
results_table.add_row(["Count of most seen species", most_seen_moving_count, most_seen_stationary_count])

results_table.add_row(["", "", ""])  # Add an empty row with placeholders

results_table.add_row(["Least seen species", least_seen_moving_species, least_seen_stationary_species])
results_table.add_row(["Count of least seen species", least_seen_moving_count, least_seen_stationary_count])

results_table.add_row(["", "", ""])  # Add an empty row with placeholders



# Print the table and information block:

print("_____________________________________________________________")
print()
print("Cruise Information:")
print()
print("      Cruise ID:", cruise_id)
print("      Observer:", observer_name)
print("      Start date: " + cruise_start_date.strftime("%Y-%m-%d"))
print("      End date: " + cruise_end_date.strftime("%Y-%m-%d"))
print()
print("      Total trip length:", str(cruise_duration_days) + " days")
print(f"      Distance offshore from port: {furthest_distance:.2f} km.")
print()


print("_____________________________________________________________")
print()
print("Table 1. Species data from cruise surveys")
print(results_table)