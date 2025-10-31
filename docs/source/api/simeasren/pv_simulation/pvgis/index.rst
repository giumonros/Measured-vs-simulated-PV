simeasren.pv_simulation.pvgis
=============================

.. py:module:: simeasren.pv_simulation.pvgis


Functions
---------

.. autoapisummary::

   simeasren.pv_simulation.pvgis.download_pvgis_data


Module Contents
---------------

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


