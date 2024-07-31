#####################################################
#############   DATA PREPROCESSING    ###############

#########################
# Retrieving data files

"""
Here I connect to the Access database using a driver, and I perfrom two tasks:

1) I create a text file that contains a list of each table with all of their column names to organize all of the data when I perform SQL queries

2) I perform the SQL queries to fetch tables from the database to gather my data for the analysis
"""

import os
import pandas as pd
import pyodbc


# Define the output directory if it exists already using a raw string (r)
# the 'r' here makes python treat backslashes (\) as literal characters and not as escape characters used for newlines or tabs in python
output_directory = 'ECSAS_tables'


# Here I create the output directory if it doesn't exist already, this makes it so the ECSAS_tables directory can't be rewritten
    # this helps with rerunning a script so I don't lose all of the tables I might work with by accident

os.makedirs(output_directory, exist_ok=True)
print(f"Output directory is set to: {output_directory}")


# Define the path to save the list of all tables with their columns
    # ensures that tables_file_path correctly points to the desired file within the specified directory.

tables_file_path = os.path.join(output_directory, 'all-tables.txt')


# Define the path to your Access database file
db_path = 'data\ECSAS_v.3.68_BOSCH_MAY28.mdb'


# Set up the connection string for the Access database
conn_str = (

    # Specify the driver for Access databases, necessary for pyodbc module to know which driver to use
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'  

    # Specify the path to the database using the rf prefix to indicate a raw formatted string
    rf'DBQ={db_path};'
)

# Now we can connect to the Access database through the connection string we made,
# This lets me fetch tables from the Access database, in this case I just query all of the tables at once
    
# I use a try/except/finally statement for good practise

# TRY block: Contains the main logic for connecting to the database
try:
    conn = pyodbc.connect(conn_str)  # Establish the connection, define as conn
    print("Connection successful.")

    # Get a cursor to execute SQL queries and fetch data
    cursor = conn.cursor()

    # Get all the table names from the database, 'TABLE' is defined by pyodbc as one of the database objects
    table_names = [row.table_name for row in cursor.tables() if row.table_type == 'TABLE']


    # First, try to write table names and their columns to the all-tables.txt file
        # open a file and assign it to the variable tables_file 
        # where 'w' is a mode specifier for open(), which indicates the file is being opened for writing

    with open(tables_file_path, 'w') as tables_file:
        for table in table_names:

            # Get the first row from the specified tables to retrieve column names
                # Here I enclose 'table' in square brackets to handle special characters
                # The * wild card allows us to select column names from all of the tables
            cursor.execute(f'SELECT TOP 1 * FROM [{table}]')
            
            # Here I use the cursor.description attribute in the pyodbc library to extract the column names
            # After the query is executed above, cursor.description is created (a series of tuples)
            # cursor.description contains info about the column names in the first element of the tuple, column[0]
            # we can use cursor.description to retrieve the metadata it collects, defining this as column_names
            column_names = [column[0] for column in cursor.description]

            # Finally, write the table name and its columns to the file
            tables_file.write(f'{table}: {", ".join(column_names)}\n')  
                # f-string format embeds the table name and joins the column names with commas
                # \n ensures each table's information is on a new line

    print(f"List of all tables with their columns written to {tables_file_path}")


    # Second, try to query each table and save each as an Excel file
    for table in table_names:
        query = f'SELECT * FROM [{table}]' # selecting all of the tables using a wild card
        df = pd.read_sql(query, conn)  # execute the query and store the result in a df
        output_path = os.path.join(output_directory, f'{table}.xlsx') # Define the Excel file output path
        df.to_excel(output_path, index=False)  # Save the df to an Excel file
        
        print(f'{table} data has been written to {output_path}')

# EXCEPT block: Provides an error message if there's no conenction.
except pyodbc.Error as e:
    print("Error in connection:", e)  # Print the error if connection fails

# FINALLY block: Ensures cursor and connection are closed properly, even if an error occurs.
finally:
    # Close the cursor and connection
    if 'cursor' in locals():
        cursor.close()  # Close the cursor if it exists
    if 'conn' in locals():
        conn.close()  # Close the connection if it exists
        print("Connection closed.")
        
"""
NOTE: Without a `try/except/finally` block, your script will stop immediately if an error happens, leaving things half-done and messy.
This can cause issues like open database connections or files not being properly closed, and you won't get helpful error 
messages to figure out what went wrong.

Now I can see all of the tables in the `ECSAS_tables` folder (left-hand nav on VS code).

Opening `all-tables.txt`, we can see how the `sightings data` and `watch data` are kept in a seperate file.
There is also important iformation on species codes and platform activities in other data files. 
For the purpose of this analysis, I merge these files together along with a few other files to make one dataset
that contains all the data I need in one csv file.

"""

####################
# Merging data files

"""
I parsed through the `all-tables.txt` file to find unique identifiers which need to be called on in each table to make
a dataframe of my own to use for downstream analysis. 

Here I draw data from the following tables to create final datasets:

- `tblWatch.xlsx` contains unique identifier WatchID, and info on watch data per sighting

- `tblSighting.xlsx` contains unqiue identifier WatchID and info on species sighted (SpecInfoID)

- `lkpPlatformClass.xlsx` contains metadata on stationary vs moving platform surveys
    
- `tblSpeciesInfo.xlsx` contains info on the Latin, English and Alpha codes for seabird species (SpecInfoID)
"""

# Start by reading the Excel files into their own pandas df
watch_df = pd.read_excel(os.path.join(output_directory, 'tblWatch.xlsx'))
sighting_df = pd.read_excel(os.path.join(output_directory, 'tblSighting.xlsx'))
species_info_df = pd.read_excel(os.path.join(output_directory, 'tblSpeciesInfo.xlsx'))
platform_class_df = pd.read_excel(os.path.join(output_directory, 'lkpPlatformClass.xlsx'))

# First, merge watch_df with sighting_df on WatchID to retain all WatchID entries
merged_sighting_df = pd.merge(watch_df, sighting_df, on='WatchID', how='left')

# Before merging more file together, let's see what this looks like
merged_sighting_df

# inspect those columns or just refer to the list of tables we made at the beginning
print(watch_df.columns)
print(sighting_df.columns)


"""We can see there are many NaN values in the dataset, this is because some watch periods had no seabird sightings, 
so the sightings file does not contain those unique Watch IDs. This results in a merged data file with some missing values for seabird Counts. 
We can take those NaN values and represent them as 0 values to denote that no birds were found during those watch periods."""

# Fill NaN values in Count column with 0
merged_sighting_df['Count'].fillna(0, inplace=True)

# Now we can see our count values are filled in accordingly
print(merged_sighting_df[['Count']])

# Now we can finish merging our main file with some other important files here

# Merge with species_info_df based on SpecInfoID
final_df = pd.merge(merged_sighting_df, species_info_df, on='SpecInfoID', how='left')


#################
### Data clean-up

""" Here I drop any unnecessary columns and seperate stationary and moving platform survey data into two seperate files"""

# Define columns to exclude for stationary surveys
columns_to_exclude_stationary = ['Key', 'OldWatchID', 'Kilometers', 'PlatformDir', 'PlatformDirDeg', 'OldFlockID', 'OldPiropID']

# Define columns to exclude for moving surveys
columns_to_exclude_moving = ['Key', 'OldWatchID', 'Kilometers', 'OldFlockID', 'OldPiropID']

# Drop columns from final_df based on the defined lists
final_df.drop(columns=columns_to_exclude_stationary, inplace=True, errors='ignore')
final_df.drop(columns=columns_to_exclude_moving, inplace=True, errors='ignore')

# Filter for moving surveys
moving_df = final_df[final_df['PlatformClass'] == 3].copy()

# Filter for stationary surveys
stationary_df = final_df[final_df['PlatformClass'] == 2].copy()

# Save the final datasets as Excel files
moving_df.to_excel(os.path.join('moving_platform_data.xlsx'), index=False)
stationary_df.to_excel(os.path.join('stationary_platform_data.xlsx'), index=False)