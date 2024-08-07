#!/bin/bash
#SBATCH --time= 00:05:00 #adjusted to 5 mins
#SBATCH --mem= 1 GB #adjusted to 1GB

#load the modules
module load StdEnv/2023
module load python
module load scipy-stack

# Create and activate a virtual environment
python -m venv myenv
source myenv/bin/activate

# Install necessary packages in the virtual environment
pip install folium
pip install openpyxl

# Run your script
python interactive_map.py

# Deactivate the virtual environment
deactivate
