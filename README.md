# Measured-vs-simulated-PV

This repository has been created based on the work presented in the article: [ADD DOI]
The aim of this repository is to facilate the data sharing of measured PV profiles and compare measured and simulated PV power production data.
The README also explains how to use the measured and simulated PV data for e-fuel techno-economic assessments. 

This repository contains:
- Measured data from real photovoltaic (PV) plants
- Python scripts for extracting PV energy production data from PVGIS and Renewables.ninja
- Python scripts for data analysis, graphs, and error analysis

##Installation guide

This tool requires the use Python. We propose here two options to us it (if you already have Python installed you can skip):
- Option 1: Jupyter Notebook (easier for beginners)
- Option 2: Visual Studio Code (VS Code)

### Option 1: Jupyter Notebook

Install Python:
First, download and install Python from the official website: Python Downloads. Be sure to check the box that says "Add Python to PATH" during the installation.
Install Jupyter Notebook:
Open a terminal or command prompt and install Jupyter Notebook using pip:

pip install notebook

Install Required Libraries:
After Jupyter Notebook is installed, install the required libraries (pandas, requests, openpyxl):
pip install pandas requests openpyxl

Run Jupyter Notebook:
Open a terminal and run:
jupyter notebook
A browser window will open with the Jupyter interface. You can create a new Python notebook, copy the script into a cell, and run the script step by step.

Pros of Using Jupyter:
Easy to use: You can run the code line by line and see the output immediately.
Great for exploration: If you're analyzing data or working with output interactively, Jupyter is ideal.
Supports visualization: If you ever need to plot graphs or inspect your data, it's straightforward to integrate visualization libraries like matplotlib.

### Option 2: Visual Studio Code (VS Code) (more advanced
Step-by-Step Setup

Install Python:

First, download and install Python from the official website: Python Downloads. Make sure to check "Add Python to PATH" during the installation.
Install Visual Studio Code (VS Code):

Download and install Visual Studio Code from: VS Code Download.
Install Python Extension in VS Code:

Once VS Code is installed, open it, and go to the Extensions Marketplace (you can find it on the left sidebar).
Search for "Python" and install the official Python extension provided by Microsoft.
Install Required Libraries:

Open the terminal inside VS Code by clicking Terminal > New Terminal.
Run the following command to install the required libraries:

pip install pandas requests openpyxl
Create or Open the Python Script:

You can now either create a new Python file (with a .py extension) or open the existing script in VS Code.
Once the script is open, you can run the script by pressing F5 or selecting Run > Run Without Debugging.

Pros of Using VS Code:
Great for coding: If you're writing and editing Python code, VS Code provides many helpful features like code autocompletion, debugging tools, and syntax highlighting.
Integrated Terminal: You can run your Python scripts within the editor without needing to switch to another terminal window.
Extensibility: VS Code supports many extensions that make development easier (e.g., Git integration, Docker support).


# Library required

To run the project in your environemnt, you will need to install the following Python libraries:

pandas: For reading/writing Excel files and data manipulation.
requests: For making API calls to PVGIS and Renewable Ninja.
openpyxl: To handle Excel files when using pandas.
You can install these libraries using pip:


pip install pandas requests openpyxl
Usage
Once you've cloned the repository and installed the required libraries, follow these steps:

Prepare the input file: Ensure that the file input_datasheet.xlsx is in the root folder of the project, and it conforms to the structure defined above.

Set up Renewable Ninja API token: Before running the script, you need to obtain a Renewable Ninja API token (see Obtaining the Renewable Ninja API Token). Replace the rn_token variable in the script with your token.


## Input File Structure
The input file should be an Excel file named input_datasheet.xlsx with a sheet named datasheet. Each row in this sheet should represent an individual solar installation and provide details necessary to query both the PVGIS and Renewable Ninja APIs. Here’s a breakdown of the columns required:

Column Name	Description
cod	A unique code for each solar installation (e.g., 'SOL123').
latitude	Latitude of the solar installation (in decimal degrees).
longitude	Longitude of the solar installation (in decimal degrees).
azimuth	Azimuth angle of the solar panels.
tilt	Tilt angle of the solar panels.
peakpower_kW	Installed peak power of the solar system (in kW).
loss	System losses (as a percentage).
pv_technology	Type of photovoltaic technology (e.g., 'crystalline').
building/free	Indicates whether the panels are on a building (building) or free (free).
startyear	The year when data collection should start.
endyear	The year when data collection should end.
fixed	Indicator of whether the panels are fixed (1) or use tracking (0).
tracking	Tracking type for panels that are not fixed (e.g., single-axis).
Ensure that all required columns are present for proper execution.


# Run the script:

The script will:
Read the data from the input_datasheet.xlsx file.
Fetch solar production data from the PVGIS and Renewable Ninja APIs for each installation.
Consolidate the data into a structured output and save it as Consolidated_Hourly_Production.xlsx.
The resulting Excel file will contain hourly production data across all the specified years and databases.

# APIs Used and documentation
This project integrates with two APIs to gather solar production data:

PVGIS API: The Photovoltaic Geographical Information System (PVGIS) API provides solar irradiation and solar production data for various geographical locations.
API Documentation: https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html#PVP

Renewable Ninja API: Renewable Ninja provides simulation data for solar and wind energy production at any location worldwide.
API Documentation: https://www.renewables.ninja/api

# Obtaining the Renewable Ninja API Token
To use the Renewable Ninja API, you need to create a profile and obtain an API token. Follow these steps:

Visit Renewable Ninja's registration page.
Create a profile by registering with your email and setting up an account.
Once logged in, navigate to the API section of the website to generate and retrieve your API token.
Copy your API token and paste it into the script by setting the rn_token variable:

rn_token = 'your_token_here'
This token is required to authenticate and successfully retrieve data from Renewable Ninja.

# Output
The output file Consolidated_Hourly_Production.xlsx contains hourly solar production data for each installation, organized in the following dimensions:


# License
This project is licensed under the MIT License. See the LICENSE file for details.
