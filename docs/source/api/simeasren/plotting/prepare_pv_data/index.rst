simeasren.plotting.prepare_pv_data
==================================

.. py:module:: simeasren.plotting.prepare_pv_data


Functions
---------

.. autoapisummary::

   simeasren.plotting.prepare_pv_data.convert_comma_to_dot
   simeasren.plotting.prepare_pv_data.extract_year_selected
   simeasren.plotting.prepare_pv_data.prepare_pv_data_for_plots


Module Contents
---------------

.. py:function:: convert_comma_to_dot(df: pandas.DataFrame) -> pandas.DataFrame

   Convert columns with commas as decimals to numeric floats.


.. py:function:: extract_year_selected(dataframe: pandas.DataFrame, column_pattern='([A-Za-z]+[0-9]{4})') -> str

   Extract year tag (e.g., Location2020) from dataframe column names.


.. py:function:: prepare_pv_data_for_plots(location_name: str, year: str)

   Load, clean, and prepare all measured and simulated PV datasets
   for subsequent time series and high-resolution plotting.

   This function consolidates and preprocesses photovoltaic (PV) performance data
   by loading measured Excel files and corresponding simulated CSV outputs for a given
   location and year. It also merges high-resolution daily data (clear and cloudy sky)
   with hourly simulation results to ensure consistent plotting inputs.

   :param location_name: Name of the PV site or measurement location (e.g., "Almeria", "Turin", "Utrecht").
                         Must match the filename in the `data/measured_PV/` directory
   :type location_name: str
   :param year: Specific year to filter the simulation data (e.g., `"2023"`). The year should exist
                in the measured data files
   :type year: str

   :returns: * **data_sim_meas** (*pd.DataFrame*) -- Hourly simulated and measured PV data (limited to 8760 hours for a full year).
               Columns include simulated and measured normalized power outputs per model/tool.
             * **clear_sky_df** (*pd.DataFrame*) -- Processed and merged clear-sky day data, combining high-resolution measured
               values with corresponding simulation results.
             * **cloudy_sky_df** (*pd.DataFrame*) -- Processed and merged cloudy-sky day data, combining high-resolution measured
               values with corresponding simulation results.

   :raises FileNotFoundError: If the measured PV Excel file for the specified location does not exist.
   :raises UserWarning: If the specified year is not found in the dataset, resulting in empty outputs.

   .. rubric:: Notes

   - Measured PV data are expected in:
     ```
     data/measured_PV/{location_name}.xlsx
     ```
     with sheet names `"Clear sky day"` and `"Cloudy sky day"`.
   - Simulated PV results must exist in:
     ```
     results/{location_name}/simulated_pv/{location_name}_meas_sim.csv
     ```
   - Helper functions used:
     - `convert_comma_to_dot()` for numeric conversion.
     - `extract_year_selected()` for extracting year tags from column names.

   .. rubric:: Examples

   >>> from simeasren import prepare_pv_data_for_plots
   >>> data_sim_meas, clear_sky_df, cloudy_sky_df = prepare_pv_data_for_plots(
   ...     location_name="Almeria",
   ...     year="2023"
   ... )
   >>> data_sim_meas.shape
   (8760, 3)


