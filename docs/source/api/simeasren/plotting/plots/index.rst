simeasren.plotting.plots
========================

.. py:module:: simeasren.plotting.plots


Functions
---------

.. autoapisummary::

   simeasren.plotting.plots.plot_capacity_factors
   simeasren.plotting.plots.capacity_factor_formatting
   simeasren.plotting.plots.plot_scatter_comparison
   simeasren.plotting.plots.plot_error_metrics
   simeasren.plotting.plots.plot_high_res_days
   simeasren.plotting.plots.highres_plot_formatting
   simeasren.plotting.plots.plot_LCOF_diff


Module Contents
---------------

.. py:function:: plot_capacity_factors(data_sim_meas, location_name, year, legend_names, colors_CF, linestyles_CF, line_widths_CF, output_dir_timeseries, x_limit=5000)

   Plot the capacity factor figure for a given location and dataset.

   :param data_sim_meas: DataFrame with capacity factor time series for the location.
   :type data_sim_meas: pd.DataFrame
   :param location_name: Name of the location.
   :type location_name: str
   :param legend_names: List of time series/legend names corresponding to the columns.
   :type legend_names: list
   :param colors_CF: List of colors for each time series.
   :type colors_CF: list
   :param linestyles_CF: List of line styles for each time series.
   :type linestyles_CF: list
   :param line_widths_CF: List of line widths for each time series.
   :type line_widths_CF: list
   :param output_dir_timeseries: Path to save the figure.
   :type output_dir_timeseries: str
   :param x_limit: Maximum x-axis value (default is 5000).
   :type x_limit: int, optional


.. py:function:: capacity_factor_formatting(legend_names, highlight_label='PV-MEAS')

   Generate colors, linestyles, and line widths for capacity factor plots.

   :param data_sim_meas: DataFrame containing all simulation and measurement columns.
   :type data_sim_meas: pd.DataFrame
   :param user_color_mapping: Custom color mapping to override defaults.
   :type user_color_mapping: dict, optional
   :param user_linestyle_mapping: Custom linestyle mapping to override defaults.
   :type user_linestyle_mapping: dict, optional
   :param highlight_label: Label that should be highlighted with a thicker line width.
   :type highlight_label: str, optional

   :returns: (legend_names, colors_CF, linestyles_CF, line_widths_CF)
   :rtype: tuple


.. py:function:: plot_scatter_comparison(data_sim_meas, location_name, year, custom_cmap, output_dir_timeseries)

   Plot scatter plots comparing measured vs simulated data for multiple simulation columns.

   :param filtered_data_scat: DataFrame with filtered simulation data (rows where measured data != 0).
   :type filtered_data_scat: pd.DataFrame
   :param measured_data_scat: Series with measured data.
   :type measured_data_scat: pd.Series
   :param sim_columns: List of simulation column names to plot.
   :type sim_columns: list
   :param location_name: Name of the location.
   :type location_name: str
   :param custom_cmap: Colormap for KDE plot.
   :param output_dir_timeseries: Directory to save the scatter plot figure.
   :type output_dir_timeseries: str


.. py:function:: plot_error_metrics(location_name, year, mean_diff_results, mae_results, rmse_results, plot_palette, legend_names, output_dir_timeseries)

   Plot error metrics (Mean Difference, MAE, RMSE) for a location.

   :param location_name: Name of the location.
   :type location_name: str
   :param year: Year of the simulation.
   :type year: str
   :param mean_diff_results: List of mean difference results with keys "Location", "Tool", "Mean Difference (%)".
   :type mean_diff_results: list of dicts
   :param mae_results: List of MAE results with keys "Location", "Tool", "MAE (%)".
   :type mae_results: list of dicts
   :param rmse_results: List of RMSE results with keys "Location", "Tool", "RMSE (%)".
   :type rmse_results: list of dicts
   :param plot_palette: Dictionary mapping tools to colors for the bar plots.
   :type plot_palette: dict
   :param legend_names: List of tools to include in the legend.
   :type legend_names: list
   :param output_dir_timeseries: Directory to save the combined metrics figure.
   :type output_dir_timeseries: str


.. py:function:: plot_high_res_days(df_clear, df_cloudy, location_name, legend_names_high_res, colors_high_res, linestyles_high_res, line_widths_high_res, output_dir_timeseries)

   Plot high-resolution PV data for Clear Sky and Cloudy Sky days side by side.

   :param df_clear: DataFrame with clear sky day data.
   :type df_clear: pd.DataFrame
   :param df_cloudy: DataFrame with cloudy sky day data.
   :type df_cloudy: pd.DataFrame
   :param location_name: Name of the location.
   :type location_name: str
   :param legend_names_high_res: List of time series/legend names.
   :type legend_names_high_res: list
   :param colors_high_res: List of colors corresponding to the legends.
   :type colors_high_res: list
   :param linestyles_high_res: List of line styles for the legends.
   :type linestyles_high_res: list
   :param line_widths_high_res: List of line widths for the legends.
   :type line_widths_high_res: list
   :param output_dir_timeseries: Directory to save the figure.
   :type output_dir_timeseries: str


.. py:function:: highres_plot_formatting(legend_names_high_res, highlight_label='PV-MEAS')

   Generate legend names, colors, linestyles, and line widths for
   high-resolution (clear sky and cloudy sky) PV plots.

   :param clear_sky_df: DataFrame for the clear-sky high-res data.
   :type clear_sky_df: pd.DataFrame
   :param cloudy_sky_df: DataFrame for the cloudy-sky high-res data.
   :type cloudy_sky_df: pd.DataFrame
   :param highlight_label: Label that should be highlighted with a thicker line width.
   :type highlight_label: str, optional

   :returns: (legend_names_high_res, colors_high_res, linestyles_high_res, line_widths_high_res)
   :rtype: tuple


.. py:function:: plot_LCOF_diff(LCOF_diff_results, plot_palette, location_name, year, H2_end_user_min_load, output_dir_technoeco, legend_names)

   Function to plot LCOF difference for error analysis and save the figure.

   Args:
   LCOF_diff_results (list): List of dictionaries containing LCOF differences for each location and tool.
   plot_palette (dict): Dictionary containing the simulation tools for plotting.
   location_name (str): The location name used for saving the plot.
   H2_end_user_min_load (float): Minimum load for H2 end user, included in the figure filename.
   output_dir_technoeco (str): Directory to save the plot.
   legend_names (list): List of legend names to filter the plot legend

   Returns:
   None


