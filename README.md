# Assessment of Seabird Species Prevalence and Influencing Environmental Factors During an Offshore Seabird Survey
## ACENET Independant Study Project (July 31, 2024)

## Author
Johanna-Lisa Bosch

## Abstract
This project assesses seabird species prevalence and the environmental factors influencing their distribution during an offshore seabird survey conducted by Environment and Climate Change Canada. Scripts are written using Python.

## Background
Seabird populations and their distribution patterns are critical indicators of ocean health and ecosystem dynamics. Historically, systematic monitoring of seabirds in Atlantic Canada ceased in the mid-1980s, creating a gap in data needed to understand the impacts of human activities on these species. In response, Environment and Climate Change Canada (ECCC) established a pelagic seabird monitoring program, with protocols formalized by [Gjerdrum et al. (2012)](https://www.cnlopb.ca/wp-content/uploads/nexenergy/ecseabird.pdf).

This analysis looks at the metrics from an ECSAS survey conducted approximately 500 km off the coast of Newfoundland, and aims to identify the most common seabird species and analyze how various environmental conditions influence their presence. Data is avaialble [here](https://github.com/johannabosch/ECSAS_analysis/tree/main/data).

ECSAS surveys offshore are conducted by observing birds along a line transect on one side of the boat that is ≤300 m (([Tasker et al. 1984](https://academic.oup.com/auk/article/101/3/567/5191249?login=false))) depending on the visibility from the platform. All observers conducting the surveys are trained and have experience working with and identifying seabirds. As the observer performs the surveys, data is entered into a Microsoft Access Database (SQL based) customized for ECSAS protocols. The data includes watch period details, species sightings, weather, sea state, glare conditions, and more (see [data/stationary](https://github.com/johannabosch/ECSAS_analysis/tree/main/data)).

A more detailed report is available in the [/ISP_report](https://github.com/johannabosch/ECSAS_analysis/blob/main/ISP_report/ISP_report_JBosch.pdf) folder.

## Preprocessing Script

**File:** `preprocessing.py`

Retrieves data from an Access Database, performs SQL queries to fetch tables, and merges relevant data to create a comprehensive dataset for analysis. Steps include:

**Connecting to the Access Database:**
   - Establish a connection using a driver.
   - Perform SQL queries to fetch tables and save them as Excel files.

**Merging Data Files:**
   - Read data from multiple tables
   - Merge these tables based on unique identifiers to create a final dataset.  
   - Separate stationary and moving platform survey data into different files.

**Cleaning data:**
   - Drop unnecessary columns.
   - Handle `NaN` values in the `Count` column by filling them with 0.
   - Save the final datasets as Excel files (`moving_platform_data.xlsx` and `stationary_platform_data.xlsx`).


## Basic Metrics Script

**File:** `basic_metrics.py`

Calculates basic metrics for the surveys and creates a summary table with PrettyTable.

**Calculate Metrics:**
   - Calculate the total number of surveys conducted, species observed, and count occurrences for each species.
     
**Display Metrics:**
   - Create a PrettyTable to display the calculated metrics.


## GAM Script

**File:** `GAM_scatter.py`

Analyzes seabird prevalence during the cruise period by creating a scatter plot of species counts per watch and fitting a Generalized Additive Model (GAM).

**Calculate Z-Scores:**
   - Calculate z-scores for the counts of each species.

**Fit GAM Model:**
   - Fit a GAM model to the data.
   - Generate predictions and calculate confidence intervals.

**Create Scatter Plot:**
   - Use Plotly to create an interactive scatter plot

## Pie Chart Script

**File:** `pie-chart.py`

Creates pie charts displaying the most common sea state, weather, and glare conditions during the cruise

**Process Data:**
   - Aggregate the most common weather, sea state, and glare codes.
   - Merge with metadata to get descriptive labels.

**Create Pie Charts:**
   - Create a subplot figure with three pie charts

## Heatmap Script

**File:** `heatmaps.py`

Creates heatmaps to show the most common weather and sea state codes for each species.

**Find Most Common Codes:**
   - Calculate the most common weather and sea state codes for each species.
   - Merge with metadata to get descriptive labels.

**Create Heatmaps:**
   - Create full pivot tables
   - Plot heatmaps for weather and sea state

## Visibility Script

**File:** `visibility.py`
Creates a scatter plot showing the relationship between the observer's visibility from the platform (in km) and the number of birds counted per watch.

**Fit Linear Regression Model:**
   - Fit a linear regression model to the data.
   - Calculate the slope, intercept, and R² value.

**Create Scatter Plot:**
   - Plot the scatter plot with a line of best fit.

## Interactive Map Script

**File:** `interactive_map.py`

Creates an interactive map showing survey points with details about species observed and environmental conditions.

**Processing Data:**
   - Aggregate species and counts for each watch.
   - Calculate total birds observed per watch.

**Create Interactive Map:**
   - Initialize a map using Folium.
   - Add survey points with details in pop-ups boxes
   - Add port markers

#### Running the Interactive Map on an HPC cluster

To run the interactive map generation on an HPC cluster for a file that has a large size, you will need to run through the `preprocessing.py` script with your MDB file first, and then run the SLURM script `run-map.py` that contains the commands to execute the `interactive_map_script.py`on your cluster of choice. I have uploaded a SLURM submission script as an exmaple output after I had  submitted the job to the Graham cluster. 

**Create or edit the `run-map.py` file :**
 
 Begin by loading the appropraite modules required for running python on your cluster.
 This SLURM script will execute the `interactive_map_script.py` by creating a virtual environment to launch python, load the packages and run the script.
 Make sure to adjust the memory and time usage accordingly.
 
   ```
   python run-map.py
   ```

**Submit the job:**

   ```
   sbatch run-map.slurm
   ```

**Check job status or memory usage:**

   You can check the status of your job using the `squeue` command.

   ```
   squeue -u your_username
   ```

   or check the memory usage of your script after running it the first time.

   ```
   seff <JOB-ID>
   ```

This setup will help you run the interactive map generation on an HPC cluster efficiently.
Ensure that the paths in your scripts and SLURM file match the actual paths in your project directory.


## Usage

**Clone the Repository:**

  ```git clone https://github.com/johannalisabosch/seabird-survey-analysis.git```
  ```cd seabird-survey-analysis```

**Install Dependencies**

```pip install -r requirements.txt```

**Run Preprocessing Script:**

```python preprocessing_script.py```

**Run Analysis Scripts:**
```
python basic_metrics_script.py
python gam_script.py
python pie_chart_script.py
python heatmap_script.py
python interactive_map_script.py
python visibility_script.py
```

## Figures
The generated figures for this project will be saved in the figures directory. Open the HTML files in a web browser to view the interactive plots and maps.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
