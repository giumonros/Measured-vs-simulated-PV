# Measured-vs-simulated-PV

This repository has been created based on the work presented in the article: [ADD DOI]
The aim of this repository is to facilate the data sharing of measured PV profiles and compare measured and simulated PV power production data.
The README also explains how to use the measured and simulated PV data for e-fuel techno-economic assessments. 

This repository contains:
- Measured data from real photovoltaic (PV) plants (``Measured PV data`` folder)
- Python scripts for extracting PV power production data from PVGIS and Renewables.ninja (``Codes to run`` folder)
- Python scripts for data analysis and graphs (``Codes to run`` folder)
- Outputs files combining simulated and measured time series (``Simulated and measured PV data`` folder)
- Output graphs for measured vs simulated time series analysis

## Sharing PV measured data

If you have high resolution PV **power** measurement data that you can make public, you can share it here!
We do not need the time series with all the data points but **only the normalized hourly aggregated values**. 
Higher resolution data can be shared but only two days are enough (one cloudy day and one sunny day).

To share your PV power data, please follow these steps:

1- Go in the ``Measured PV data`` folder and download one of the existing excel file (for example the one called "Utrecht"): click on the file > click on the three dots on the top right of your screen > click download

2- Rename the excel file to your location and replace the required informations with yours

3- Fork this repository (Top right of the screen, you need to create a GitHub account)

4- Go inside the ``Measured PV data`` folder ; Click on "Add files" and "Upload files" ; Upload your new excel file

5- Commit the changes, create a pull request and we will review it!

## Installation guide for the PV time series analysis tool

1- Download the "Measured-vs-simulated-PV" ZIP folder: go to the green 'Code' button on this page, and click on 'Download ZIP'. Unzip the folder. 
You can also Fork this repository and clone it on your local machine with github (you can use [GitHub desktop](https://desktop.github.com/download/) to facilitate the process) 

2- Download and install [Python](https://www.python.org/downloads/). Add Python to PATH **ONLY if** you had VS Code already installed.

3- Download and install the code editor [VSCode](https://code.visualstudio.com/). Make sure to select the "Add to PATH" option when installing. 

4- Add the *Python* extension in the code editor (in "Extensions marketplace" on the left sidebar).

5- Open the unzipped folder "Measured-vs-simulated-PV" in VS Code: File > Open folder > "Measured-vs-simulated-PV folder"

6- Open the terminal inside VS Code by clicking Terminal > New Terminal. Run the following command to create an environment ``venv``:

``` bash
python -m venv venv
```
7- Activate the environment writting in the terminal

``` bash
venv\Scripts\Activate.ps1
```

8- Install the required libraries in this environment writting in the terminal:

``` bash
pip install -r requirements.txt
```

## Extracting simulated PV power production data

1- In VS code, open the "Measured-vs-simulated-PV" folder and click on the ``1-PV_simulation_download`` python file in the ``Codes to run`` folder

2- On top the the script, write down the location where you want to import simulated PV data. The name should match with one of the location in the ``Measured PV data`` folder

3- To generate profiles with [Renewables.ninja](https://www.renewables.ninja/), you have to set up a Renewable Ninja API token:
- Visit Renewables.ninja's [registration page](https://www.renewables.ninja/register) and create an account
- Once logged in go to your profile page(https://www.renewables.ninja/profile) to generate your API token
- Copy your API token 
- In the code, paste your token in front of the rn_token variable: ``rn_token = 'your_token_here'``

4- You can now run the script by clicking on the small arrow on the top right of the VS Code window (make sure that you are running with the correct environment set-up in the installation step).
The generated time series will save in the ``Simulated and measured PV data`` folder. 

5- You can add a personalized simulation and use it for the graphs inserting a new column called "SIM-SELF1".


## Drawing time-series analysis graphs

1- In VS code, open the "Measured-vs-simulated-PV" folder and click on the ``2-PV_graphs`` or ``3-PV_Graphs_Cloudy_Clear`` python file in the ``Codes to run`` folder

2- Write the location on top the script and run. The graphs will save in the ``Output graphs`` folder

## Performing hydrogen techno-economic assessments with measured or simulated data

1- Go to the techno-economic assessment Github tool "OptiPlant" and follow the instructions to install it: https://github.com/njbca/OptiPlant/ 

2- In "OptiPlant > Base > Data > Profiles > Meas-vs-sim" open the "All_profiles.xlsx" file (make a copy a keep it somewhere in case)

3- Delete the input data in the "Flux" sheet and copy-paste the ones from the file in the ``Simulated and measured PV data`` folder

4- Adapt the sheet "ScenariosToRun" in the file ``Meas_vs_sim_data.xlsx`` in "OptiPlant > Base > Data > Inputs > Meas-vs-sim" to your case

5- Run the techno-economic model

## APIs Used and documentation
This project integrates with two APIs to gather solar production data:

PVGIS API: The Photovoltaic Geographical Information System (PVGIS) API provides solar irradiation and solar production data for various geographical locations.
API Documentation: https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html#PVP

Renewable Ninja API: Renewable Ninja provides simulation data for solar and wind energy production at any location worldwide.
API Documentation: https://www.renewables.ninja/api

Remember to credit Renewables.ninja and PVGIS appropriately in your work :)
