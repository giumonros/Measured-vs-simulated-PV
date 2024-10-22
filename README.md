# Measured-vs-simulated-PV
This repository contains measured data from real photovoltaic (PV) plants, along with Python scripts for extracting PV energy production data from PVGIS and Renewable Ninja. It also includes Python scripts for data analysis, graph creation, and error analysis, facilitating a comparison between measured and simulated PV energy production data.

# Table of Contents
Input File Structure
Installation
Usage
APIs Used
Obtaining the Renewable Ninja API Token
Output
License

# Input File Structure
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

# Installation
To run the project, you will need to install the following Python libraries:

pandas: For reading/writing Excel files and data manipulation.
requests: For making API calls to PVGIS and Renewable Ninja.
openpyxl: To handle Excel files when using pandas.
You can install these libraries using pip:

bash
Copia codice
pip install pandas requests openpyxl
Usage
Once you've cloned the repository and installed the required libraries, follow these steps:

Prepare the input file: Ensure that the file input_datasheet.xlsx is in the root folder of the project, and it conforms to the structure defined above.

Set up Renewable Ninja API token: Before running the script, you need to obtain a Renewable Ninja API token (see Obtaining the Renewable Ninja API Token). Replace the rn_token variable in the script with your token.

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
