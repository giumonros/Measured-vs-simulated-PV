simeasren.pv_simulation.renewables_ninja
========================================

.. py:module:: simeasren.pv_simulation.renewables_ninja


Functions
---------

.. autoapisummary::

   simeasren.pv_simulation.renewables_ninja.download_rn_data


Module Contents
---------------

.. py:function:: download_rn_data(location_name: str, pv_parameters, rn_token: str)

   Download simulated PV power output data from Renewables.ninja for a specified location.

   This function queries the Renewables.ninja API for multiple datasets (MERRA2 and SARAH)
   and generates hourly PV electricity output for the given PV system parameters.
   The resulting data are saved as CSV files in the project directory and
   returned as a dictionary for further analysis.

   :param location_name: Name of the location/site (e.g., "Almeria") used for file naming and labeling downloaded data.
   :type location_name: str
   :param pv_parameters: Dictionary containing PV system configuration parameters.

                         **Expected keys:**
                             - "Latitude" : float — geographic latitude
                             - "Longitude" : float — geographic longitude
                             - "Tilt" : float — tilt angle of PV modules (degrees)
                             - "Azimuth" : float — azimuth of PV modules (degrees)
                             - "Max capacity simulation" : float — peak PV power in kW
                             - "System loss" : float — system losses in %
                             - "Start year" : int — first year of simulation
                             - "End year" : int — last year of simulation
                             - "Fixed" : int — 1 if fixed tilt, 0 if tracking system
                             - "Tracking" : int — tracking type if not fixed (0 = none, 1 = single-axis, etc.)
   :type pv_parameters: dict
   :param rn_token: API token for Renewables.ninja.
   :type rn_token: str

   :returns: Dictionary of Renewables.ninja simulation outputs.

             **Keys**
                 str — unique identifiers in the format
                 ``"{location_name}{year} RN-{dataset}"``
                 Example: ``"Almeria2020 RN-MERRA2"``

             **Values**
                 numpy.ndarray — hourly PV electricity generation in kW.
   :rtype: dict

   :raises requests.exceptions.RequestException: If a network request to Renewables.ninja fails.
   :raises FileNotFoundError: If the output directory cannot be created or written to.
   :raises ValueError: If the CSV response from Renewables.ninja cannot be parsed correctly.

   .. rubric:: Notes

   - Output CSV files are saved to:

       results/{location_name}/simulated_PV/Renewables_ninja/

   - The function handles API rate limiting (HTTP 429) by pausing before retrying.
   - Power output is returned as a NumPy array in kW.
   - To set up a Renewables.ninja API token:
       1. Visit [Renewables.ninja registration page](https://www.renewables.ninja/register) and create an account
       2. Go to your [profile page](https://www.renewables.ninja/profile) to generate your API token
       3. Copy your API token for use in this function

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
   >>> rn_data = download_rn_data("Almeria", pv_params, rn_token)


