#####################################################
###########  ENVIRONMENTAL FACTORS II    ############

""" 
This script makes heatmaps to consider how many birds were seen during different conditions (weather and sea state).
"""

# load the modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define file paths using raw string literals
stationary_survey_path = r'data/stationary_platform_data.xlsx'

# Load the stationary survey data
stationary_survey = pd.read_excel(stationary_survey_path)

# load the metadata files for weather, sea state, and glare
sea_state = pd.read_excel('ECSAS_tables\\lkpSeaState.xlsx')
weather = pd.read_excel('ECSAS_tables\\lkpWeather.xlsx')

# find the most common Weather and SeaState codes for each species
most_common_weather = stationary_survey.groupby('Alpha')['Weather'].agg(lambda x: x.mode()[0] if not x.mode().empty else np.nan).reset_index()
most_common_sea_state = stationary_survey.groupby('Alpha')['SeaState'].agg(lambda x: x.mode()[0] if not x.mode().empty else np.nan).reset_index()

# merge with metadata to get descriptive labels
most_common_weather = most_common_weather.merge(weather, left_on='Weather', right_on='Weather', how='left')
most_common_sea_state = most_common_sea_state.merge(sea_state, left_on='SeaState', right_on='SeaState', how='left')

# create full pivot tables with all possible codes as indices and columns
weather_codes = weather['Weather'].unique()
sea_state_codes = sea_state['SeaState'].unique()

# create empty dataframes with all possible codes as indices and columns
# this way all of the codes will display on the plot, not only ones used during the survey
pivot_weather = pd.DataFrame(index=most_common_weather['Alpha'].unique(), columns=weather_codes)
pivot_sea_state = pd.DataFrame(index=most_common_sea_state['Alpha'].unique(), columns=sea_state_codes)

# popoulate the pivot tables with the codes
for _, row in most_common_weather.iterrows():
    pivot_weather.loc[row['Alpha'], row['Weather']] = row['Weather']

for _, row in most_common_sea_state.iterrows():
    pivot_sea_state.loc[row['Alpha'], row['SeaState']] = row['SeaState']

# replace non-numeric values with NaN for heatmap compatibility
pivot_weather = pivot_weather.apply(pd.to_numeric, errors='coerce')
pivot_sea_state = pivot_sea_state.apply(pd.to_numeric, errors='coerce')

# plot sizing
plt.figure(figsize=(18, 6))

# plot the heatmaps for:

# Weather:
plt.subplot(1, 2, 1)
sns.heatmap(pivot_weather, cmap='Greys', annot=True, fmt='.1f', cbar=True, linewidths=.3, linecolor='grey')
plt.xlabel('Weather Code')
plt.ylabel('Species')

# Sea State:
plt.subplot(1, 2, 2)
sns.heatmap(pivot_sea_state, cmap='Greys', annot=True, fmt='.1f', cbar=True, linewidths=.3, linecolor='grey')
plt.xlabel('Sea State Code')
plt.ylabel('')  # Clear ylabel for better layout

# then adjust layout
plt.tight_layout()


# save the plot as a PNG file
plt.savefig('figures/heatmaps.png')



# Filter the data for Alpha = 'GBBG' and SeaState = 10
filtered_data = stationary_survey[(stationary_survey['Alpha'] == 'GBBG') & (stationary_survey['SeaState'] == 10)]

# Calculate the number of times GBBG was observed
observation_count = filtered_data.shape[0]

# Calculate the total count of GBBG observed
total_gbbg_count = filtered_data['Count'].sum()

# Print the results
print(f"Number of observations where Alpha is 'GBBG' and Sea State is 10: {observation_count}")
print(f"Total count of 'GBBG' when Sea State is 10: {total_gbbg_count}")



# Filter the data for Alpha = 'GBBG' and SeaState = 10
filtered_data = stationary_survey[(stationary_survey['Alpha'] == 'COMU') & (stationary_survey['SeaState'] == 7)]

# Calculate the number of times GBBG was observed
observation_count = filtered_data.shape[0]

# Calculate the total count of GBBG observed
total_gbbg_count = filtered_data['Count'].sum()

# Print the results
print(f"Number of observations where Alpha is 'COMU' and Sea State is 7: {observation_count}")
print(f"Total count of 'COMU' when Sea State is 7: {total_gbbg_count}")