# PV data simulation

This package provides functions to simulate PV data using Renewables.ninja and PVGIS (for now)

Input parameters can be either user-defined or loaded directly from measured PV data files, ensuring that simulated and measured data are compared under the same assumptions.  

## Loading PV system parameters

To load parameters from a measured data file, use the `load_pv_setup_from_meas_file` function.
The file/location has to exist in the `src/data/measured_pv/` folder.

```python
from simeasren import load_pv_setup_from_meas_file
parameters = load_pv_setup_from_meas_file("Almeria")
```

## Renewables.ninja

Simulated PV power output data from Renewables.ninja can be downloaded using the ``download_rn_data`` function.
This function queries the Renewables.ninja API for multiple datasets (MERRA2 and SARAH) and generates hourly PV electricity output based on the provided system parameters.

The resulting data is returned as a dictionary for further analysis, and the raw CSV files are saved in the project directory under ``results/simulated_pv``.

### API Token Setup

To use this function, you must have a valid **Renewables.ninja API token**.  
Follow these steps to obtain it:

1. Register for a free account at [renewables.ninja/register](https://www.renewables.ninja/register).  
2. After logging in, visit your [profile page](https://www.renewables.ninja/profile).  
3. Generate and copy your API token.  
4. Provide the token as the `rn_token` parameter when using the function.

---

When filled up manually, the expected parameters keys are:

| Key | Type | Description |
|-----|------|-------------|
| `Latitude` | Float | Geographic latitude of the site |
| `Longitude` | Float | Geographic longitude of the site |
| `Tilt` | Float | PV module tilt angle (degrees) |
| `Azimuth` | Float | PV module azimuth (degrees) |
| `Max capacity simulation` | Float | Installed PV capacity (kW) |
| `System loss` | Float | Overall system losses (%) |
| `Start year` | Integer | Start year of the simulation |
| `End year` | Integer | End year of the simulation |
| `Fixed` | Integer | 1 for fixed-tilt systems, 0 for tracking systems |
| `Tracking` | Integer | Tracking type (0 = none, 1 = single-axis, etc.) |

---

### Example usage

With user-defined parameters
```python
from simeasren import download_rn_data

# Define PV system parameters
pv_params = {
    "Latitude": 37.0,
    "Longitude": -2.5,
    "Tilt": 30,
    "Azimuth": 180,
    "Max capacity simulation": 1000,
    "System loss": 14,
    "Start year": 2020,
    "End year": 2020,
    "Fixed": 1,
    "Tracking": 0
}

# Download data
rn_data = download_rn_data("Almeria", pv_params, rn_token = "YOUR_RN_API_TOKEN")

```

Reading set-up from one of the measured data files:

```python
from simeasren import download_rn_data, load_pv_setup_from_meas_file

pv_parameters = load_pv_setup_from_meas_file("Almeria")
rn_data = download_rn_data("Almeria", pv_parameters, rn_token="YOUR_RN_API_TOKEN")
```

## PVGIS
Then simulated data can be generated in a similar fashion with PVGIS except that no token is necessary:

```python
from simeasren import download_rn_data, load_pv_setup_from_meas_file

pv_parameters = load_pv_setup_from_meas_file("Almeria")
pvgis_data = download_pvgis_data("Almeria", pv_parameters)
```

## Merge simulated and measured data

Most of the ``simeasren`` package functions need to read a file that combine both measured and simulated data.
To create this file for example in Almeria:

```python
from simeasren import merge_sim_with_measured, load_pv_setup_from_meas_file, download_pvgis_data, download_rn_data

pv_parameters = load_pv_setup_from_meas_file("Almeria")
pvgis_data = download_pvgis_data("Almeria", pv_parameters)
rn_data = download_rn_data("Almeria", pv_parameters, rn_token="YOUR_RN_API_TOKEN")
merge_sim_with_measured("Almeria", pvgis_data, rn_data)
```

To include only pvgis data:
```python
merge_sim_with_measured("Almeria", pvgis_data)
```









