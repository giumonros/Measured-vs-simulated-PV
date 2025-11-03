simeasren.pv_analysis
=====================

.. py:module:: simeasren.pv_analysis


Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/simeasren/pv_analysis/metrics/index


Functions
---------

.. autoapisummary::

   simeasren.pv_analysis.calculate_error_metrics


Package Contents
----------------

.. py:function:: calculate_error_metrics(data_sim_meas, location_name, plot_palette=None, exclude_non_palette=True)

   Calculate PV simulation error metrics relative to measured data.

   This function computes key statistical error metrics — Mean Difference,
   Mean Absolute Error (MAE), and Root Mean Square Error (RMSE) — for each
   simulation tool relative to measured PV data for a specific location.
   The outputs are structured as lists of dictionaries, ready for plotting
   or further analysis.

   :param data_sim_meas: DataFrame containing measured and simulated PV data for a given location.
                         Columns should include one `"PV-MEAS"` column for measured data and
                         one or more simulation tool columns (e.g., `"Turin PV-SIM1"`).
   :type data_sim_meas: pandas.DataFrame
   :param location_name: Name of the location (e.g., `"Turin"`) used to filter relevant columns
                         and label outputs.
   :type location_name: str
   :param plot_palette: Dictionary mapping simulation tool names to colors or labels for plotting.
                        If None, no filtering is applied based on the palette.
   :type plot_palette: dict, optional
   :param exclude_non_palette: If True, only simulation tools listed in `plot_palette` are included.
                               If False, all simulation columns are processed regardless of the palette.
   :type exclude_non_palette: bool, optional (default=True)

   :returns: A tuple `(mean_diff_results, mae_results, rmse_results)` where each element
             is a list of dictionaries with the following structure:
             - `"Location"` : str — name of the location
             - `"Tool"` : str — simulation tool name
             - `"Mean Difference (%)"` / `"MAE (%)"` / `"RMSE (%)"` : float — computed metric
   :rtype: tuple of lists

   :raises None: Missing `'PV-MEAS'` column is handled by returning empty lists.
       Columns with insufficient data (empty after NaN removal) are skipped.

   .. rubric:: Notes

   - Metrics are calculated in **percent (%)** by multiplying the raw value by 100.
   - The function aligns indices of simulated and measured data to handle missing values.
   - Tool names are extracted from column names by splitting at whitespace and
     using the second part if available.

   .. rubric:: Examples

   >>> from simeasren import calculate_error_metrics, prepare_pv_data_for_plots
   >>> data_sim_meas, _, _ = prepare_pv_data_for_plots("Turin", "2019")
   >>> mean_diff, mae, rmse = calculate_error_metrics(
   ...     data_sim_meas=data_sim_meas,
   ...     location_name="Turin"
   ... )
   >>> mean_diff[0]
   {'Location': 'Turin', 'Tool': 'PG2-SARAH2', 'Mean Difference (%)': np.float64(1.1827557468101797)}


