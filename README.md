# Measured-vs-simulated-PV

This package has been created based on the work presented in this article: https://doi.org/10.1016/j.rser.2024.115044 The data used for the article are in the ``publication data`` folder. The aim of this package is to facilate the data sharing of measured PV profiles, compare measured and simulated PV power production data, and
analyse the influence of using measured or simulated PV power data for e-fuel techno-economic assessments. 

The complete package documentation is available here: https://measured-vs-simulated-pv.readthedocs.io/en/latest/ 

The data used to run this package are:
- [Measured data](https://github.com/giumonros/Measured-vs-simulated-PV/tree/main/src/simeasren/data/measured_PV) from real photovoltaic (PV) plants
- Hydrogen based e-fuel [techno-economic parameters](https://github.com/giumonros/Measured-vs-simulated-PV/tree/main/src/simeasren/data/techno_economic_assessment)

This package contains:
- Functions for extracting PV power production data from PVGIS and Renewables.ninja
- Data analysis tools and graphs to compare measured and simulated data
- A simple e-fuel techno-economic assessment model to study the error propagation

## Sharing PV measured data

We would like to expand the analysis to other sites, so if you are allowed to publicly share high resolution PV power measurement data, that would help us a lot!

We do not need all the data points but **the normalized hourly aggregated values**. 
Higher resolution data can be shared but only two days are enough (one cloudy day and one sunny day).

To share PV power data, please contact us at [giulia.montanari@polito.it](mailto:giulia.montanari@polito.it) or [njbca@dtu.dk](mailto:njbca@dtu.dk).

## Installation guide

1- Download and install the code editor [VSCode](https://code.visualstudio.com/). Make sure to select the "Add to PATH" option when installing 

2- Download and install [Python](https://www.python.org/downloads/).

3- Add the *Python* extension in the code editor (in "Extensions marketplace" on the left sidebar)

4- Open the terminal inside VS Code by clicking Terminal > New Terminal. Run the following command to create an environment ``.venv``:

``` bash
python -m venv .venv
```
7- Activate the environment writting in the terminal

``` bash
.venv\Scripts\Activate.ps1
```

**Note** (from [here](https://docs.python.org/3/library/venv.html))

On Microsoft Windows, it may be required to enable the Activate.ps1 script by setting the execution policy for the user. You can do this by issuing the following PowerShell command:

``` bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

8- Install the package:

``` bash
pip install simeasren
```

## Run example scripts

In VS code, create a new python script and copy on of the file in the ``example`` folder.

The ``Full_analysis.py`` example shows a simplified version of the analysis made in this publication https://doi.org/10.1016/j.rser.2024.115044 

To personalize the analysis:

1- Fill up the "User defined" informations:
- Location: the name should match with one of the location in the ``src/simeasren/data/measured_PV`` folder
- Year: Specific year to run the simulation (the year must exist in the measured data)
- H2_end_user_min_load: for the H2 techno-economic assessment, define the flexibility of the hydrogen end-user choosing its minimal load between 0 and 1
- Solver: selected solver for the H2 techno-economic assessment. cbc is the default free solver. To use [Gurobi](https://www.gurobi.com/downloads/), it has to be installed on your machine with a valid license. To use others solvers, check the [PulP documentation](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html)
- Renewablesninja_token: follow step 2

2- To generate profiles with [Renewables.ninja](https://www.renewables.ninja/), you have to set up a Renewable Ninja API token:
- Visit Renewables.ninja's [registration page](https://www.renewables.ninja/register) and create an account
- Once logged in go to your [profile page](https://www.renewables.ninja/profile) to generate your API token
- Copy your API token 
- In the code, paste your token in front of the rn_token variable: ``rn_token = 'your-token-here'``

3- Run the ``Full_analysis.py`` file clicking on the small arrow on the top right of the VS Code window (make sure that you are running with the correct environment set-up in the installation step). A result folder will be created on your local machine.

More advanced e-fuel techno-economic assessments can also be performed using the ["OptiPlant"](https://github.com/njbca/OptiPlant/tool) tool 

## APIs Used and documentation
This project integrates with two APIs to gather solar production data:

PVGIS API: The Photovoltaic Geographical Information System (PVGIS) API provides solar irradiation and solar production data for various geographical locations.
API Documentation: https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html#PVP

Renewable Ninja API: Renewable Ninja provides simulation data for solar and wind energy production at any location worldwide.
API Documentation: https://www.renewables.ninja/api

If using this script or related data, please remember to credit Renewables.ninja, PVGIS and cite https://doi.org/10.1016/j.rser.2024.115044 appropriately in your work :)

## Support

If you have questions or would like to discuss about PV power data sharing do not hesitate to send an e-mail at [giulia.montanari@polito.it](mailto:giulia.montanari@polito.it) or [njbca@dtu.dk](mailto:njbca@dtu.dk).

