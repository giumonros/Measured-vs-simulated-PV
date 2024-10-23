# Measured-vs-simulated-PV

This repository has been created based on the work presented in the article: [ADD DOI]
The aim of this repository is to facilate the data sharing of measured PV profiles and compare measured and simulated PV power production data.
The README also explains how to use the measured and simulated PV data for e-fuel techno-economic assessments. 

This repository contains:
- Measured data from real photovoltaic (PV) plants
- Python scripts for extracting PV power production data from PVGIS and Renewables.ninja
- Python scripts for data analysis, graphs, and error analysis

## Sharing PV measured data

If you have high resolution PV **power** measurement data that you can make public, you can share it here!
We do not need the time series with all the data points but **only the hourly aggregated values**. 
Higher resolution data can be shared but only two days are enough (one cloudy day and one sunny day).

To share your PV power data, please follow these steps:
1- Download the ``input_datasheet.xlsx`` file and fill up the information regarding your PV plant.
2- Normalize your PV power time series based on the maximum PV plant capacity (all values should be between 0 and 1)
3- 

 
## Installation guide for the PV time series analysis tool

1- Download the "Measured-vs-simulated-PV" ZIP folder: go to the green 'Code' button on this page, and click on 'Download ZIP'. Unzip the folder. 
If you are familiar with GitHub you can also Fork this repository. 

2- Download and install [Python](https://www.python.org/downloads/). Add Python to PATH **ONLY if** you had VS Code already installed.

3- Download and install the code editor [VSCode](https://code.visualstudio.com/). Make sure to select the "Add to PATH" option when installing. 

4- Add the *Python* extension in the code editor (in "Extensions marketplace" on the left sidebar).

5- Open the terminal inside VS Code by clicking Terminal > New Terminal. Run the following command to install the required libraries:

``` bash
pip install pandas requests openpyxl matplotlib
```

## Extracting PV power production data from simulation tools

1- Open the ``input_datasheet.xlsx`` file and fill in the required informations

2- To generate profiles with [Renewables.ninja](https://www.renewables.ninja/), you have to set up a Renewable Ninja API token:
- Visit Renewables.ninja's [registration page](https://www.renewables.ninja/register) and create an account
- Once logged in go to your profile page(https://www.renewables.ninja/profile) to generate your API token.
- Copy your API token 

3- Open the script called [NAME] in VS Code (File > Open folder > Measured-vs-simulated-PV folder and click on the script)

4- Paste your token in front of the rn_token variable: ``rn_token = 'your_token_here'``

5- You can now run the script by clicking on the small arrow on the top right of the VS Code window.

More infos: https://code.visualstudio.com/docs/python/run
https://code.visualstudio.com/docs/datascience/jupyter-notebooks 

The script will read the data from the ``input_datasheet.xlsx`` file, fetch solar production data from the PVGIS and Renewable Ninja APIs for each installation and consolidate the data into a structured output saved as Consolidated_Hourly_Production.xlsx.
This file will contain hourly production data across all the specified years and databases.

## APIs Used and documentation
This project integrates with two APIs to gather solar production data:

PVGIS API: The Photovoltaic Geographical Information System (PVGIS) API provides solar irradiation and solar production data for various geographical locations.
API Documentation: https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html#PVP

Renewable Ninja API: Renewable Ninja provides simulation data for solar and wind energy production at any location worldwide.
API Documentation: https://www.renewables.ninja/api

Remember to credit Renewables.ninja and PVGIS appropriately in your work :)
