simeasren.pv_simulation
=======================

.. py:module:: simeasren.pv_simulation


Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/simeasren/pv_simulation/load_pv_set_up/index
   /api/simeasren/pv_simulation/pvgis/index
   /api/simeasren/pv_simulation/renewables_ninja/index


Functions
---------

.. autoapisummary::

   simeasren.pv_simulation.load_pv_setup_from_meas_file
   simeasren.pv_simulation.download_pvgis_data
   simeasren.pv_simulation.download_rn_data


Package Contents
----------------

.. py:function:: load_pv_setup_from_meas_file(location_name: str) -> dict

   Load PV plant setup parameters from the measured data Excel file (in data/measured_PV)

   This function reads the `"PV_plant_setup"` sheet from the measured PV data Excel
   file for a given location and returns the contents as a dictionary, with the
   Excel sheet's `"Parameter"` column as keys and the `"Value"` column as values.

   :param location_name: Name of the location/site corresponding to the Excel file (without extension),
                         e.g., `"Turin"`. The function expects the file to exist in:
                         ```
                         data/measured_PV/{location_name}.xlsx
                         ```
   :type location_name: str

   :returns: Dictionary containing PV plant setup parameters. Keys correspond to parameter
             names (from the `"Parameter"` column in Excel), and values are the corresponding
             setup values.
   :rtype: dict

   :raises FileNotFoundError: If the measured PV Excel file for the specified location does not exist.

   .. rubric:: Notes

   - The Excel sheet must be named `"PV_plant_setup"` with columns `"Parameter"` and `"Value"`.
   - Typical use includes retrieving metadata such as plant capacity, inverter specs,
     orientation, or other site-specific configuration values for plotting or modeling.

   .. rubric:: Examples

   >>> parameters = load_pv_setup_from_meas_file("Turin")
   >>> parameters["Capacity_PV_MW"]
   5.0
   >>> parameters["Inverter_efficiency"]
   0.96


.. py:function:: download_pvgis_data(location_name: str, pv_parameters)

   Download simulated PV power output data from PVGIS for a specified location.

   This function queries the PVGIS API for multiple databases and versions to
   generate hourly PV power output for the given PV system parameters.
   The resulting data are saved as CSV files in the project directory and
   returned as a dictionary for further analysis.

   :param location_name: Name of the location/site (e.g., `"Almeria"`) used for file naming and
                         labeling downloaded data.
   :type location_name: str
   :param pv_parameters: Dictionary containing PV system configuration parameters, including:
                         - `"Latitude"` : float — geographic latitude
                         - `"Longitude"` : float — geographic longitude
                         - `"Tilt"` : float — tilt angle of PV modules (degrees)
                         - `"Azimuth"` : float — azimuth of PV modules (degrees)
                         - `"Max capacity simulation"` : float — peak PV power in kW
                         - `"System loss"` : float — system losses in %
                         - `"PV technology"` : str — PV technology type (e.g., `"crystalline silicon"`)
                         - `"Building/free"` : str — mounting type (`"building"` or `"free"`)
                         - `"Start year"` : int — first year of simulation
                         - `"End year"` : int — last year of simulation
   :type pv_parameters: dict

   :returns: Dictionary of PVGIS simulation outputs:
             - Keys : str — unique identifiers in the format
               `"{location_name}{year} PG{version}-{database}"` (e.g., `"Almeria2020 PG3-SARAH3"`)
             - Values : numpy.ndarray — hourly PV power output in kW.
   :rtype: dict

   :raises requests.exceptions.RequestException: If a network request to PVGIS fails.
   :raises FileNotFoundError: If the output directory cannot be created or written to.
   :raises ValueError: If PVGIS CSV data cannot be parsed correctly.

   .. rubric:: Notes

   - Output CSV files are saved to:
     ```
     results/{location_name}/simulated_PV/PVGIS/
     ```
   - PVGIS API versions used:
       - v5_2 : `"PVGIS-SARAH"`, `"PVGIS-SARAH2"`, `"PVGIS-ERA5"`
       - v5_3 : `"PVGIS-SARAH3"`, `"PVGIS-ERA5"`
   - Power output in the CSV is converted from W → kW and stored in `"P_kW"` column.
   - The function prints status messages for successful downloads and missing data.

   .. rubric:: Examples

   >>> from simeasren import download_pvgis_data
   >>> pv_params = {
   ...     "Latitude": 37.0,
   ...     "Longitude": -2.5,
   ...     "Tilt": 30,
   ...     "Azimuth": 180,
   ...     "Max capacity simulation": 1000,
   ...     "System loss": 14,
   ...     "PV technology": "crystalline silicon",
   ...     "Building/free": "free",
   ...     "Start year": 2020,
   ...     "End year": 2020
   ... }
   >>> productions = download_pvgis_data("Almeria", pv_params)
   >>> list(productions.keys())
   ['Almeria2020 PG2-SARAH', 'Almeria2020 PG2-SARAH2', 'Almeria2020 PG2-ERA5', 'Almeria2020 PG3-SARAH3', 'Almeria2020 PG3-ERA5']
   >>> productions['Almeria2020 PG3-SARAH3'].shape
   (8760,)


.. py:function:: download_rn_data(location_name: str, pv_parameters, rn_token: str)

   Download simulated PV power output data from Renewables.ninja for a specified location.

   This function queries the Renewables.ninja API for multiple datasets (MERRA2 and SARAH)
   and generates hourly PV electricity output for the given PV system parameters.
   The resulting data are saved as CSV files in the project directory and
   returned as a dictionary for further analysis.

   :param location_name: Name of the location/site (e.g., `"Almeria"`) used for file naming and
                         labeling downloaded data.
   :type location_name: str
   :param pv_parameters: Dictionary containing PV system configuration parameters, including:
                         - `"Latitude"` : float — geographic latitude
                         - `"Longitude"` : float — geographic longitude
                         - `"Tilt"` : float — tilt angle of PV modules (degrees)
                         - `"Azimuth"` : float — azimuth of PV modules (degrees)
                         - `"Max capacity simulation"` : float — peak PV power in kW
                         - `"System loss"` : float — system losses in %
                         - `"Start year"` : int — first year of simulation
                         - `"End year"` : int — last year of simulation
                         - `"Fixed"` : int — 1 if fixed tilt, 0 if tracking system
                         - `"Tracking"` : int — tracking type if not fixed (0 = none, 1 = single-axis, etc.)
   :type pv_parameters: dict
   :param rn_token: API token for Renewables.ninja.
   :type rn_token: str

   :returns: Dictionary of Renewables.ninja simulation outputs:
             - Keys : str — unique identifiers in the format
               `"{location_name}{year} RN-{dataset}"` (e.g., `"Almeria2020 RN-MERRA2"`)
             - Values : numpy.ndarray — hourly PV electricity generation in kW.
   :rtype: dict

   :raises requests.exceptions.RequestException: If a network request to Renewables.ninja fails.
   :raises FileNotFoundError: If the output directory cannot be created or written to.
   :raises ValueError: If the CSV response from Renewables.ninja cannot be parsed correctly.

   .. rubric:: Notes

   - Output CSV files are saved to:
     ```
     results/{location_name}/simulated_PV/Renewables_ninja/
     ```
   - The function handles API rate limiting (HTTP 429) by pausing before retrying.
   - Power output is returned as a NumPy array in kW.
   To set up a Renewable Ninja API token:
   - Visit Renewables.ninja's [registration page](https://www.renewables.ninja/register) and create an account
   - Once logged in go to your [profile page](https://www.renewables.ninja/profile) to generate your API token
   - Copy your API token

   .. rubric:: Examples

   >>> from simeasren import download_rn_data
   >>> pv_params = {
   ...     "Latitude": 37.0,
   ...     "Longitude": -2.5,
   ...     "Tilt": 30,
   ...     "Azimuth": 180,
   ...     "Max capacity simulation": 1000,
   ...     "System loss": 14,
   ...     "Start year": 2020,
   ...     "End year": 2020,
   ...     "Fixed": 1,
   ...     "Tracking": 0
   ... }
   >>> rn_token = "YOUR_RN_API_TOKEN"
   >>> productions = download_rn_data("Almeria", pv_params, rn_token)
   >>> list(productions.keys())
   ['Almeria2020 RN-MERRA2', 'Almeria2020 RN-SARAH']
   >>> productions['Almeria2020 RN-MERRA2'].shape
   (8760,)


