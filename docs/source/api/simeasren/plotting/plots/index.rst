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

   Parameters:
       data_sim_meas (pd.DataFrame): DataFrame with capacity factor time series for the location.
       location_name (str): Name of the location.
       legend_names (list): List of time series/legend names corresponding to the columns.
       colors_CF (list): List of colors for each time series.
       linestyles_CF (list): List of line styles for each time series.
       line_widths_CF (list): List of line widths for each time series.
       output_dir_timeseries (str): Path to save the figure.
       x_limit (int, optional): Maximum x-axis value (default is 5000).


.. py:function:: capacity_factor_formatting(legend_names, highlight_label='PV-MEAS')

   Generate colors, linestyles, and line widths for capacity factor plots.

   Parameters:
       data_sim_meas (pd.DataFrame): DataFrame containing all simulation and measurement columns.
       user_color_mapping (dict, optional): Custom color mapping to override defaults.
       user_linestyle_mapping (dict, optional): Custom linestyle mapping to override defaults.
       highlight_label (str, optional): Label that should be highlighted with a thicker line width.

   Returns:
       tuple: (legend_names, colors_CF, linestyles_CF, line_widths_CF)


.. py:function:: plot_scatter_comparison(data_sim_meas, location_name, year, custom_cmap, output_dir_timeseries)

   Plot scatter plots comparing measured vs simulated data for multiple simulation columns.

   Parameters:
       filtered_data_scat (pd.DataFrame): DataFrame with filtered simulation data (rows where measured data != 0).
       measured_data_scat (pd.Series): Series with measured data.
       sim_columns (list): List of simulation column names to plot.
       location_name (str): Name of the location.
       custom_cmap: Colormap for KDE plot.
       output_dir_timeseries (str): Directory to save the scatter plot figure.


.. py:function:: plot_error_metrics(location_name, year, mean_diff_results, mae_results, rmse_results, plot_palette, legend_names, output_dir_timeseries)

   Plot error metrics (Mean Difference, MAE, RMSE) for a location.

   Parameters:
       location_name (str): Name of the location.
       year (str): Year of the simulation.
       mean_diff_results (list of dicts): List of mean difference results with keys "Location", "Tool", "Mean Difference (%)".
       mae_results (list of dicts): List of MAE results with keys "Location", "Tool", "MAE (%)".
       rmse_results (list of dicts): List of RMSE results with keys "Location", "Tool", "RMSE (%)".
       plot_palette (dict): Dictionary mapping tools to colors for the bar plots.
       legend_names (list): List of tools to include in the legend.
       output_dir_timeseries (str): Directory to save the combined metrics figure.


.. py:function:: plot_high_res_days(df_clear, df_cloudy, location_name, legend_names_high_res, colors_high_res, linestyles_high_res, line_widths_high_res, output_dir_timeseries)

   Plot high-resolution PV data for Clear Sky and Cloudy Sky days side by side.

   Parameters:
       df_clear (pd.DataFrame): DataFrame with clear sky day data.
       df_cloudy (pd.DataFrame): DataFrame with cloudy sky day data.
       location_name (str): Name of the location.
       legend_names_high_res (list): List of time series/legend names.
       colors_high_res (list): List of colors corresponding to the legends.
       linestyles_high_res (list): List of line styles for the legends.
       line_widths_high_res (list): List of line widths for the legends.
       output_dir_timeseries (str): Directory to save the figure.


.. py:function:: highres_plot_formatting(legend_names_high_res, highlight_label='PV-MEAS')

   Generate legend names, colors, linestyles, and line widths for
   high-resolution (clear sky and cloudy sky) PV plots.

   Parameters:
       clear_sky_df (pd.DataFrame): DataFrame for the clear-sky high-res data.
       cloudy_sky_df (pd.DataFrame): DataFrame for the cloudy-sky high-res data.
       highlight_label (str, optional): Label that should be highlighted with a thicker line width.

   Returns:
       tuple: (legend_names_high_res, colors_high_res, linestyles_high_res, line_widths_high_res)


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


