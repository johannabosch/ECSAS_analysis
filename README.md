# Assessment of Seabird Species Prevalence and Influencing Environmental Factors During an Offshore Seabird Survey
## ACENET Independant Study Project (July 31, 2024)

## Author
Johanna-Lisa Bosch

## Abstract
This project assesses seabird species prevalence and the environmental factors influencing their distribution during an offshore seabird survey conducted by Environment and Climate Change Canada. The study identifies the most common seabird species and examines how weather, sea state, and glare conditions affect their presence.

## Introduction
Seabird populations and their distribution patterns are critical indicators of ocean health and ecosystem dynamics. Historically, systematic monitoring of seabirds in Atlantic Canada ceased in the mid-1980s, creating a gap in data needed to understand the impacts of human activities on these species (Gjerdrum et al. 2012). In response, Environment and Climate Change Canada (ECCC) established a pelagic seabird monitoring program, with protocols formalized by Gjerdrum et al. (2012). This analysis of a survey conducted approximately 500 km off the coast of Newfoundland aims to identify the most common seabird species and analyze how various environmental conditions influence their presence.

## Background
ECSAS surveys offshore are conducted by observing birds along a line transect on one side of the boat that is ≤300 m (Tasker et al. 1984) depending on the visibility from the platform. All observers conducting the surveys are trained and have experience working with and identifying seabirds. As the observer performs the surveys, data is entered into a Microsoft Access Database (SQL based) customized for ECSAS protocols. The data includes watch period details, species sightings, weather, sea state, glare conditions, and more.

## Report
A more detailed report is available in the /ISP_report folder.

## Preprocessing Script

**File:** `preprocessing.py`

### Description:
This script retrieves data from a Microsoft Access Database, performs SQL queries to fetch tables, and merges relevant data to create a comprehensive dataset for analysis.

### Steps:
1. **Connecting to the Access Database:**
   - Establish a connection using a driver.
   - Create a text file containing a list of each table with all of their column names for organizing data during SQL queries.
   - Perform SQL queries to fetch tables and save them as Excel files.

2. **Merging Data Files:**
   - Read data from multiple tables including `tblWatch`, `tblSighting`, `lkpPlatformClass`, and `tblSpeciesInfo`.
   - Merge these tables based on unique identifiers to create a final dataset.
   - Handle `NaN` values in the `Count` column by filling them with 0.
   - Separate stationary and moving platform survey data into different files.

3. **Data Clean-Up:**
   - Drop unnecessary columns.
   - Save the final datasets as Excel files (`moving_platform_data.xlsx` and `stationary_platform_data.xlsx`).

## Basic Metrics Script

**File:** `basic_metrics.py`

### Description:
This script calculates basic metrics for the stationary and moving platform surveys and creates a summary table with PrettyTable.

### Steps:
1. **Load Data:**
   - Load stationary and moving survey data from Excel files.
   - Convert the `Date` column to datetime format.

2. **Calculate Metrics:**
   - Determine the cruise start and end dates.
   - Calculate the total number of surveys conducted, species observed, and count occurrences for each species.
   - Identify the most and least seen species for both moving and stationary surveys.

3. **Display Metrics:**
   - Create a PrettyTable to display the calculated metrics.
   - Print the summary table and additional cruise information.

## GAM Script

**File:** `GAM_scatter.py`

### Description:
This script analyzes seabird prevalence during the cruise period by creating a scatter plot of species counts per watch and fitting a Generalized Additive Model (GAM).

### Steps:
1. **Load Data:**
   - Load stationary survey data from an Excel file.
   - Extract relevant columns and group data by species and watch ID.

2. **Calculate Z-Scores:**
   - Calculate z-scores for the counts of each species.
   - Compute the arithmetic mean of the z-scores for each WatchID.

3. **Fit GAM Model:**
   - Fit a GAM model to the data.
   - Generate predictions and calculate confidence intervals.

4. **Create Scatter Plot:**
   - Use Plotly to create an interactive scatter plot with a GAM line and confidence intervals.
   - Save the plot as an HTML file.

## Pie Chart Script

**File:** `pie-chart.py`

### Description:
This script creates pie charts displaying the most common sea state, weather, and glare conditions during the 17-day cruise using Plotly.

### Steps:
1. **Load Data:**
   - Load stationary survey data and metadata files for weather, sea state, and glare.

2. **Aggregate Data:**
   - Aggregate the most common weather, sea state, and glare codes.
   - Merge with metadata to get descriptive labels.

3. **Create Pie Charts:**
   - Create a subplot figure with three pie charts for weather, sea state, and glare.
   - Save the figure as an HTML file.

## Heatmap Script

**File:** `heatmaps.py`

### Description:
This script creates heatmaps to show the most common weather and sea state codes for each species.

### Steps:
1. **Load Data:**
   - Load stationary survey data and metadata files for weather and sea state.

2. **Find Most Common Codes:**
   - Calculate the most common weather and sea state codes for each species.
   - Merge with metadata to get descriptive labels.

3. **Create Heatmaps:**
   - Create full pivot tables with all possible codes as indices and columns.
   - Plot heatmaps for weather and sea state.
   - Save the plot as a PNG file.

## Interactive Map Script

**File:** `interactive_map.py`

### Description:
This script creates an interactive map showing survey points with details about species observed and environmental conditions.

### Steps:
1. **Load Data:**
   - Load stationary survey data and metadata files.
   - Clean and merge data to get observer, platform names, and watch notes.

2. **Aggregate Data:**
   - Aggregate species and counts for each WatchID.
   - Calculate total birds observed per watch.

3. **Create Interactive Map:**
   - Initialize a map using Folium.
   - Add survey points with details in pop-ups.
   - Add port markers and measure control.
   - Save the map as an HTML file.

## Visibility Script

**File:** `visibility.py`

### Description:
This script creates a scatter plot showing the relationship between the observer's visibility from the platform (in km) and the number of birds counted per watch.

### Steps:
1. **Load Data:**
   - Load stationary survey data from an Excel file.

2. **Calculate Total Count:**
   - Aggregate the total count of birds for each WatchID.
   - Merge total counts with visibility data.

3. **Fit Linear Regression Model:**
   - Fit a linear regression model to the data.
   - Calculate the slope, intercept, and R² value.

4. **Create Scatter Plot:**
   - Plot the scatter plot with a line of best fit.
   - Save the plot as a PNG file.

## Usage

1. **Clone the Repository:**

  ```git clone https://github.com/johannalisabosch/seabird-survey-analysis.git```
  ```cd seabird-survey-analysis```

2. **Install Dependencies**

```pip install -r requirements.txt```

3. **Run Preprocessing Script:**

```python preprocessing_script.py```

4. **Run Analysis Scripts:**
```python basic_metrics_script.py```
```python gam_script.py```
```python pie_chart_script.py```
```python heatmap_script.py```
```python interactive_map_script.py```
```python visibility_script.py```


## Figures
The generated figures will be saved in the figures directory. Open the HTML files in a web browser to view the interactive plots and maps.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
