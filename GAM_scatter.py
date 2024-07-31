#####################################################
######   SPECIES PREVALENCE DURING SURVEY    ########

"""
To look at seabird prevalence during the cruise period, I create a scatter plot of the counts per species during each watch period.
I align the watches in chronological order and then apply a Generalized Additive Model (GAM) to the data, which adds a line of best
fit through the points and a shaded area representing the confidence intervals.

"""

# load the required modules
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pygam import LinearGAM, s
import os

# Define file paths
stationary_survey_path = r'C:\Users\BoschJ\Desktop\ECSAS_analysis\data\stationary_platform_data.xlsx'

# Load the stationary survey data
stationary_survey = pd.read_excel(stationary_survey_path)


################################################
# Finding which species are most common offshore

# Group by species and WatchID to calculate the average count per watch
species_watch_avg = stationary_survey.groupby(['Alpha', 'WatchID'])['Count'].mean().reset_index()

# Calculate the overall average count per species across all watches
species_avg = species_watch_avg.groupby('Alpha')['Count'].mean().reset_index()

# Calculate the number of watches each species was observed in
species_watch_count = stationary_survey.groupby('Alpha')['WatchID'].nunique().reset_index()
species_watch_count.columns = ['Alpha', 'WatchCount']

# Calculate the total count among all watches for each species
species_total_count = stationary_survey.groupby('Alpha')['Count'].sum().reset_index()
species_total_count.columns = ['Alpha', 'TotalCount']

# Merge the average count data with the watch count and total count data
species_avg = pd.merge(species_avg, species_watch_count, on='Alpha')
species_avg = pd.merge(species_avg, species_total_count, on='Alpha')

# Sort the species by their average count in descending order
sorted_species_avg = species_avg.sort_values(by='Count', ascending=False)

# Print the sorted list of species by their average count, number of watches observed, and total count
print("List of seabird species observed during the cruise by highest average count per watch, the number of watches observed, and total count:")
print(sorted_species_avg)

# Save the table as a .csv file
sorted_species_avg.to_csv('sorted_species_avg.csv', index=False)

###################################
# Plotting a scatterplot with a GAM

# Ensure the 'StartTime' column is in datetime format with both date and time
stationary_survey['StartTime'] = pd.to_datetime(stationary_survey['StartTime'], errors='coerce')

# Selecting subset of columns
subset_df = stationary_survey[['WatchID', 'Alpha', 'Count', 'StartTime', 'LatStart', 'LongStart']]

# Grouping by WatchID, Alpha, and StartTime to sum the count of the same species on the same watch
grouped_df = subset_df.groupby(['WatchID', 'Alpha', 'StartTime', 'LatStart', 'LongStart']).agg({'Count': 'sum'}).reset_index()

# Sort the grouped_df by StartTime from earliest to latest
sorted_df = grouped_df.sort_values(by='StartTime')

# Save sorted dataframe to an Excel file
sorted_df.to_excel(os.path.join('data/sorted_stationary_survey_data.xlsx'), index=False)

# Extract unique days from StartTime
sorted_df['Date'] = sorted_df['StartTime'].dt.date

# Create a mapping of unique days to sequential day numbers
unique_days = sorted_df['Date'].unique()
day_mapping = {day: f"Day {i+1}" for i, day in enumerate(unique_days)}

# Map the day numbers back to the dataframe
sorted_df['Day'] = sorted_df['Date'].map(day_mapping)

# Drop the intermediate Date column
sorted_df.drop(columns=['Date'], inplace=True)

# Calculate z-scores for the counts of each species
sorted_df['ZScore'] = sorted_df.groupby('Alpha')['Count'].transform(lambda x: (x - x.mean()) / x.std())

# Compute the arithmetic mean of the z-scores for each WatchID
mean_zscores = sorted_df.groupby('WatchID')['ZScore'].mean()

# Create a mapping for WatchID to their relative positions
watch_id_mapping = {watch_id: idx for idx, watch_id in enumerate(sorted_df['WatchID'].unique())}
sorted_df['WatchID_Pos'] = sorted_df['WatchID'].map(watch_id_mapping)
mean_zscores = mean_zscores.rename(index=watch_id_mapping)

# Fit the GAM model
X = np.array(list(watch_id_mapping.values())).reshape(-1, 1)  # Independent variable (WatchID_Pos)
y = mean_zscores.values  # Dependent variable (ZScore)
gam = LinearGAM(s(0)).fit(X, y)

# Generate predictions
X_pred = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
y_pred = gam.predict(X_pred)

# Calculate confidence intervals (using standard deviation as a proxy)
y_err = np.std(y)
y_pred_upper = y_pred + y_err
y_pred_lower = y_pred - y_err

# Create interactive scatter plot using Plotly
fig = px.scatter(
    sorted_df,
    x='WatchID_Pos',
    y='ZScore',
    color='Alpha',
    hover_name='WatchID',
    hover_data={
        'WatchID': True,
        'Alpha': True,
        'Count': True,
        'StartTime': True,
        'ZScore': False,  # Do not display ZScore in hover data
        'WatchID_Pos': False  # Do not display WatchID_Pos in hover data
    },
    labels={'WatchID_Pos': 'WatchID', 'ZScore': 'Z-Score'},
    title='Figure 1. Z-Scores of Species Counts per Watch (May 12 - May 28)'
)

# Add GAM line to Plotly
fig.add_trace(go.Scatter(
    x=X_pred.flatten(),
    y=y_pred,
    mode='lines',
    line=dict(color='black', width=2),
    name='GAM Line'
))

# Add confidence intervals
fig.add_trace(go.Scatter(
    x=np.concatenate([X_pred.flatten(), X_pred.flatten()[::-1]]),
    y=np.concatenate([y_pred_upper, y_pred_lower[::-1]]),
    fill='toself',
    fillcolor='rgba(0,100,80,0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    name='Confidence Interval',
    showlegend=False
))

# Update layout with y-axis limits and wider margins for x-axis
fig.update_layout(
    xaxis_title='WatchID',
    yaxis_title='Z-Score',
    xaxis=dict(
        tickvals=list(watch_id_mapping.values()),
        ticktext=list(watch_id_mapping.keys()),
        tickangle=90,  # Rotate labels for better readability
        tickmode='array',
        dtick=1  # Adjust the interval of ticks if needed
    ),
    yaxis=dict(
        range=[-2, 6]  # Adjust y-axis limits
    ),
    legend_title_text='Species',
    legend=dict(title='Species', x=1.05, y=1)
)

# Save the interactive plot as an HTML file
fig.write_html('figures/interactive_scatter_plot.html')


