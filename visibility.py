#####################################################
###########   SUPPLEMENTARY FIGURES    ##############

""" 
This script makes a scatter plot that considers the relationship between the 
Observer's visibility from the platform (km) to the number of birds counted per watch.
"""

# Load the modules
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np

# Define file paths
stationary_survey_path = r'data\stationary_platform_data.xlsx'

# Load the stationary survey data
stationary_survey = pd.read_excel(stationary_survey_path)

# Aggregate the total count of birds for each WatchID
total_count_per_watch = stationary_survey.groupby('WatchID')['Count'].sum().reset_index()
total_count_per_watch.rename(columns={'Count': 'TotalCount'}, inplace=True)

# Merge total counts with visibility data
visibility_data = pd.merge(stationary_survey[['WatchID', 'Visibility']], total_count_per_watch, on='WatchID', how='left').drop_duplicates()

# Prepare data for regression
X = visibility_data[['Visibility']].values
y = visibility_data['TotalCount'].values

# Fit linear regression model
model = LinearRegression().fit(X, y)
slope = model.coef_[0]
intercept = model.intercept_
r_squared = model.score(X, y)

# Plot sizing
plt.figure(figsize=(10, 6))

# Plot the scatter plot with line of best fit
sns.regplot(x='Visibility', y='TotalCount', data=visibility_data, scatter_kws={'s':50}, line_kws={'color':'red'})

# Display the trend metrics on the plot
plt.text(
    0.05, 0.95, f'Linear Trend:\nSlope: {slope:.2f}\nIntercept: {intercept:.2f}\nR²: {r_squared:.2f}',
    ha='left', va='top', fontsize=12, bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'),
    transform=plt.gca().transAxes
)

plt.xlabel('Visibility (km)')
plt.ylabel('Count per watch')
plt.grid(True)

# Save the plot as a PNG file
plt.savefig('figures/visibility_vs_total_counts.png')

# Show the plot (optional)
plt.show()