# Measured-vs-simulated-PV

This repository has been created based on the work presented in this article: https://doi.org/10.1016/j.rser.2024.115044
. The data used for the article are in the ``Publication data`` folder. The aim of this repository is to facilate the data sharing of measured PV profiles, compare measured and simulated PV power production data, and
analyse the influence of using measured or simulated PV power data for e-fuel techno-economic assessments. 

This repository contains:
- Measured data from real photovoltaic (PV) plants (``Measured PV data``)
- Python scripts for extracting PV power production data from PVGIS and Renewables.ninja, data analysis and graphs for PV power time series, and hydrogen based fuels techno-economic assessment (``Python scripts``)
- Outputs files combining simulated and measured time series (``Simulated and measured PV data``)
- Data required for hydrogen based e-fuel techno-economic assessments (``Techno-economic assessment data``)
- PV power time series analysis and hydrogen systems techno-economic assessments results for measured and simulated data (``Results and graphs``)

## Sharing PV measured data

If you have high resolution PV **power** measurement data that you can make public, you can share it here!
We do not need the time series with all the data points but **only the normalized hourly aggregated values**. 
Higher resolution data can be shared but only two days are enough (one cloudy day and one sunny day).

To share your PV power data, please follow these steps:

1- Go in the ``Measured PV data`` folder and download one of the existing excel file (for example the one called "Utrecht"): click on the file > click on the three dots on the top right of your screen > click download

2- Rename the excel file to your location and replace the required informations with yours

3- Fork this repository (Top right of the screen, you need to create a GitHub account)

4- Go inside the ``Measured PV data`` folder ; Click on "Add files" and "Upload files" ; Upload your new excel file

5- Commit the changes, create a pull request, we will review it and after a while your data will be shared on the repository!

6- If you have questions, you can also contact us by e-mail at [giulia.montanari@polito.it](mailto:giulia.montanari@polito.it) or [njbca@dtu.dk](mailto:njbca@dtu.dk).

## Installation guide for the PV time series analysis and H2 techno-economic assessment tool

1- Download the "Measured-vs-simulated-PV" ZIP folder: go to the green 'Code' button on this page, and click on 'Download ZIP'. Unzip the folder. 
You can also Fork this repository and clone it on your local machine with github (you can use [GitHub desktop](https://desktop.github.com/download/) to facilitate the process) 

2- Download and install [Python](https://www.python.org/downloads/). Add Python to PATH **ONLY if** you had VS Code already installed

3- Download and install the code editor [VSCode](https://code.visualstudio.com/). Make sure to select the "Add to PATH" option when installing 

4- Add the *Python* extension in the code editor (in "Extensions marketplace" on the left sidebar)

5- Open the unzipped folder "Measured-vs-simulated-PV" in VS Code: File > Open folder > "Measured-vs-simulated-PV folder"

6- Open the terminal inside VS Code by clicking Terminal > New Terminal. Run the following command to create an environment ``.venv``:

``` bash
python -m venv .venv
```
7- Activate the environment writting in the terminal

``` bash
.venv\Scripts\Activate.ps1
```

8- Install the required libraries in this environment writting in the terminal:

``` bash
pip install -r requirements.txt
```

## Extracting simulated PV power production data

1- In VS code, open the "Measured-vs-simulated-PV" folder (File > Open Folder) and click on the ``FileToRun.py`` python file in the main folder

2- Fill up the "User defined" informations:
- Location: the name should match with one of the location in the ``Measured PV data`` folder
- Years: by default all the years available in the ``Measured PV data`` for a specific location will be used. To select a specific year write i.e. "2019"
- H2_end_user_min_load: for the H2 techno-economic assessment, define the flexibility of the hydrogen end-user choosing its minimal load between 0 and 1
- Solver: selected solver for the H2 techno-economic assessment, HiGHS is free but Gurobi need to be installed on your machine with a valid license. To use others solvers, modify the ``3-H2_Technoceco_assessment-py`` script [(help)](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html)
- Renewablesninja_token: follow step 3

3- To generate profiles with [Renewables.ninja](https://www.renewables.ninja/), you have to set up a Renewable Ninja API token:
- Visit Renewables.ninja's [registration page](https://www.renewables.ninja/register) and create an account
- Once logged in go to your profile page(https://www.renewables.ninja/profile) to generate your API token
- Copy your API token 
- In the code, paste your token in front of the rn_token variable: ``rn_token = 'your_token_here'``

4- Select which scripts to run (one at a time, or as a list, both works. Correct order should be respected)
- ``1-PV_simulation_download.py`` activates Renewables.ninja and PVGIS APIs to generate simulated PV profiles for the selected location. Make sure that all necessary information are filled in the ``Measured PV data`` folder. The generated time seriesare combined with the measured ones and saved in the ``Simulated and measured PV data`` folder
You can add a personalized simulation and use it for the graphs inserting a new column and writting "SIM-SELF1" in the "Profile time series" row 
- ``2-PV_Timeseries_analysis.py`` conducts some solar PV timeseries analysis and plots graphs in the ``Results and graphs`` folder
- ``3-H2_Technoeco_assessment.py`` performs hydrogen based fuels techno-economic assessments with measured and simulated data and write results in the ``Results and graphs`` folder. 
More advanced techno-economic assessments can also be performed using the ["OptiPlant"](https://github.com/njbca/OptiPlant/tool) tool 

5- You can now run the script by clicking on the small arrow on the top right of the VS Code window (make sure that you are running with the correct environment set-up in the installation step)


## APIs Used and documentation
This project integrates with two APIs to gather solar production data:

PVGIS API: The Photovoltaic Geographical Information System (PVGIS) API provides solar irradiation and solar production data for various geographical locations.
API Documentation: https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html#PVP

Renewable Ninja API: Renewable Ninja provides simulation data for solar and wind energy production at any location worldwide.
API Documentation: https://www.renewables.ninja/api

If using this script or related data, please remember to credit Renewables.ninja, PVGIS and cite https://doi.org/10.1016/j.rser.2024.115044 appropriately in your work :)

## Support

If you have questions or would like to discuss about PV power data sharing do not hesitate to send an e-mail at [giulia.montanari@polito.it](mailto:giulia.montanari@polito.it) or [njbca@dtu.dk](mailto:njbca@dtu.dk).

