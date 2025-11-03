simeasren.utils
===============

.. py:module:: simeasren.utils


Functions
---------

.. autoapisummary::

   simeasren.utils.merge_sim_with_measured


Module Contents
---------------

.. py:function:: merge_sim_with_measured(location_name: str, *simulated_sources, output_dir='results')

   Merge measured PV data with multiple simulation sources and save as a CSV file.

   This function reads measured PV data from an Excel file, combines it with any number
   of simulated PV datasets provided as dictionaries, and saves the merged dataset
   for further analysis or plotting. Each simulation source should be a dictionary
   where keys are identifiers and values are hourly PV power arrays.

   :param location_name: Name of the location/site (e.g., `"Almeria"`) used for file paths and labeling.
   :type location_name: str
   :param \*simulated_sources: Variable number of dictionaries containing simulated PV outputs.
                               Each dictionary should have:
                               - Keys : str — unique identifiers (e.g., `"Almeria2023 PG2-SARAH"`)
                               - Values : numpy.ndarray — hourly PV power output in kW.
   :type \*simulated_sources: dict
   :param output_dir: Root directory where the merged CSV will be saved (default is `"results"`).
   :type output_dir: str, optional

   :returns: The function writes a CSV file to:
             ```
             {output_dir}/{location_name}/simulated_PV/{location_name}_meas_sim.csv
             ```
             and prints a completion message.
   :rtype: None

   :raises FileNotFoundError: If the measured PV Excel file cannot be found.

   .. rubric:: Notes

   - Only the first 8760 rows are kept to represent one year of hourly data.
   - Measured data is read from Excel sheets named `{location_name}{year}`.
   - Merged CSV columns include all simulation identifiers and the measured PV data
     labeled as `{location_name}{year} PV-MEAS`.

   .. rubric:: Examples

   >>> from simeasren import load_pv_setup_from_meas_file, download_pvgis_data, download_rn_data, merge_sim_with_measured
   >>> pv_parameters = load_pv_setup_from_meas_file("Almeria")
   >>> pvgis_data = download_pvgis_data("Almeria", pv_parameters)
   >>> rn_data = download_rn_data(location, pv_parameters, rn_token=renewablesninja_token)
   >>> merge_sim_with_measured(location, pvgis_data, rn_data)

   Simulations completed and merged with measured data for Almeria. CSV file saved in the 'results' folder


