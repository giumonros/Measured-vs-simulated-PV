simeasren.plotting
==================

.. py:module:: simeasren.plotting


Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/simeasren/plotting/plot_all/index
   /api/simeasren/plotting/plot_style_config/index
   /api/simeasren/plotting/plots/index
   /api/simeasren/plotting/prepare_pv_data/index


Functions
---------

.. autoapisummary::

   simeasren.plotting.generate_LCOF_diff_plot
   simeasren.plotting.generate_PV_timeseries_plots
   simeasren.plotting.generate_high_res_PV_plots
   simeasren.plotting.generate_PV_plots
   simeasren.plotting.prepare_pv_data_for_plots


Package Contents
----------------

.. py:function:: generate_LCOF_diff_plot(LCOF_diff_results, location_name: str, year: str, H2_end_user_min_load: float, output_root: str = 'results')

   Generate Levelized Cost of Fuel (LCOF) difference plots for a given location and year.

   This function visualizes the percentage difference in LCOF values between measured
   and simulated datasets for different modeling tools or simulation sources.
   It uses the results from the techno-economic assessment (e.g., obtained via
   `calculate_all_LCOF_diff`) and produces a bar plot comparing performance
   across tools.

   :param LCOF_diff_results: List of dictionaries containing LCOF comparison data for each simulation tool.

                             Each dictionary must include:
                                 - "Location" : str — the location name
                                 - "Tool" : str — the name of the simulation tool
                                 - "LCOF Difference (%)" : float — percentage difference vs. measured data
   :type LCOF_diff_results: list of dict
   :param location_name: Name of the analyzed location (e.g., "Turin", "Almeria", "Utrecht").
   :type location_name: str
   :param year: Year corresponding to the techno-economic assessment (used for labeling).
   :type year: str
   :param H2_end_user_min_load: Minimum hydrogen end-user load used in the techno-economic calculations
                                (e.g., 0.2 for 20% of full load).
   :type H2_end_user_min_load: float
   :param output_root: Root directory where all plots and assessment results are saved.
                       Defaults to "results".
   :type output_root: str, optional

   :returns: The function does not return any objects. It generates and saves plot files
             to the output directory.
   :rtype: None

   :raises ValueError: If `LCOF_diff_results` is empty or not properly formatted.

   .. rubric:: Notes

   Creates or ensures the existence of the following directory structure::

       {output_root}/{location_name}/Techno-eco assessments results/
           End-user flex[{H2_end_user_min_load}-1]/
               System size and costs/
               Hourly profiles/

   Additional details:
   - Relies on the helper plotting function :func:`plot_LCOF_diff`.
   - Uses the color palette defined in ``style_config.PLOT_PALETTE``.

   .. rubric:: Examples

   >>> from simeasren import generate_LCOF_diff_plot, prepare_pv_data_for_plots, calculate_all_LCOF_diff
   >>> data_sim_meas, clear_sky_df, cloudy_sky_df = prepare_pv_data_for_plots("Utrecht", "2017")
   >>> results = calculate_all_LCOF_diff(data_sim_meas, "Utrecht", 0, "GUROBI_CMD")
   Fuel cost: 1518.0033140603043 EUR/t
   Fuel cost: 1422.2281035151118 EUR/t
   Fuel cost: 1315.902904806376 EUR/t
   Fuel cost: 1441.4028983580704 EUR/t
   Fuel cost: 1320.3851528711755 EUR/t
   >>> generate_LCOF_diff_plot(
   ...     LCOF_diff_results=results,
   ...     location_name="Utrecht",
   ...     year="2017",
   ...     H2_end_user_min_load=0
   ... )
   LCOF difference figure successfully generated in the 'results/Utrecht/Techno-eco assessments results" folder for Utrecht'


.. py:function:: generate_PV_timeseries_plots(data_sim_meas, location_name: str, year: str, output_root: str = 'results')

   Generate photovoltaic (PV) time-series comparison plots for measured and simulated data.

   This function produces and saves multiple visual analyses for a given location and year:

   - **Capacity factor time-series plot** comparing measured vs. simulated data.
   - **Scatter comparison plot** between measured and simulated PV outputs.
   - **Error metrics bar charts** (mean difference, MAE, RMSE).

   Results are saved under a structured directory within the specified output root.

   :param data_sim_meas: DataFrame containing both measured and simulated PV time-series data.
                         Each column represents a dataset (e.g., different simulation tools) and must
                         include one column containing `"PV-MEAS"` for measured data.
   :type data_sim_meas: pandas.DataFrame
   :param location_name: Name of the analyzed location (e.g., "Turin", "Almeria").
   :type location_name: str
   :param year: Year corresponding to the PV data (used for labeling and output directory naming).
   :type year: str
   :param output_root: Root directory where all plots and results will be saved.
                       Defaults to "results".
   :type output_root: str, optional

   :returns: The function does not return any objects. It generates and saves plot images to disk.
   :rtype: None

   :raises FileNotFoundError: If required plotting functions or style configuration files are missing.
   :raises ValueError: If the input DataFrame does not contain measured PV data ("PV-MEAS").

   .. rubric:: Notes

   Creates or overwrites output files in::

       {output_root}/{location_name}/Time series analysis results/

   Uses the following helper functions:
   - :func:`capacity_factor_formatting`
   - :func:`plot_capacity_factors`
   - :func:`plot_scatter_comparison`
   - :func:`calculate_error_metrics`
   - :func:`plot_error_metrics`

   Plot aesthetics (colors, linestyles, and colormaps) are managed through
   the ``style_config`` module.

   .. rubric:: Examples

   >>> from simeasren import generate_PV_timeseries_plots, prepare_pv_data_for_plots
   >>> df, _, _ = prepare_pv_data_for_plots("Turin", "2019")
   >>> generate_PV_timeseries_plots(
   ...     data_sim_meas=df,
   ...     location_name="Turin",
   ...     year="2019"
   ... )
   Capacity factors figure successfully saved at 'results\Turin\Time series analysis results\Turin2019_Capacity_Factors.png'
   Scatter plot figure successfully saved at 'results\Turin\Time series analysis results\Turin2019_scatterplot.png'
   Combined error analysis figure successfully saved at 'results\Turin\Time series analysis results\Turin2019_Errors_Analysis.png'

   The following plots will be saved in::

       results/Turin/Time series analysis results/

       - Capacity factor comparison (*_capacity_factor.png)
       - Scatter plot comparison (*_scatter.png)
       - Error metrics summary (*_error_metrics.png)


.. py:function:: generate_high_res_PV_plots(clear_sky_df, cloudy_sky_df, location_name: str, year: str, output_root: str = 'results')

   Generate high-resolution photovoltaic (PV) plots for clear and cloudy sky conditions.

   This function visualizes high-frequency PV time-series data for both clear and
   cloudy days to assess model performance and temporal dynamics under different
   weather conditions.

   :param clear_sky_df: High-resolution PV data corresponding to clear-sky conditions.
                        Each column should represent a different dataset (e.g., measured and simulated values).
   :type clear_sky_df: pandas.DataFrame
   :param cloudy_sky_df: High-resolution PV data corresponding to cloudy-sky conditions.
                         Must have the same column naming convention as `clear_sky_df`.
   :type cloudy_sky_df: pandas.DataFrame
   :param location_name: Name of the analyzed location (e.g., `"Turin"`, `"Almeria"`).
   :type location_name: str
   :param year: Year corresponding to the PV data (used for labeling and output directory naming).
   :type year: str
   :param output_root: Root directory where all plots and results will be saved.
                       Defaults to `"results"`.
   :type output_root: str, optional

   :returns: This function does not return any objects. It generates and saves plot images
             to the specified results directory.
   :rtype: None

   :raises ValueError: If input DataFrames are empty or do not contain the expected columns.

   .. rubric:: Notes

   - Creates or overwrites output files in:
     ```
     {output_root}/{location_name}/Time series analysis results/
     ```
   - Uses helper functions for formatting and plotting:
     - `highres_plot_formatting()`
     - `plot_high_res_days()`
   - Column names are expected to follow the pattern:
     `"Location Source"` (e.g., `"Almeria PV-MEAS"`).
   - Plot appearance (colors, linestyles, widths) is controlled through
     `style_config` for visual consistency.

   .. rubric:: Examples

   >>> from simeasren import generate_high_res_PV_plots, prepare_pv_data_for_plots
   >>> data_sim_meas, clear_sky_df, cloudy_sky_df = prepare_pv_data_for_plots("Almeria", "2023")
   >>> generate_high_res_PV_plots(
   ...     clear_sky_df=clear_sky_df,
   ...     cloudy_sky_df=cloudy_sky_df,
   ...     location_name="Almeria",
   ...     year="2023"
   ... )
   High-resolution PV plot saved at 'results\Almeria\Time series analysis results\Almeria_highres_clear_vs_cloudy.png'


.. py:function:: generate_PV_plots(data_sim_meas, clear_sky_df, cloudy_sky_df, location_name: str, year: str, output_root: str = 'results')

   Generate all photovoltaic (PV) plots for a given location and year.

   This wrapper function coordinates the generation of both:
     1. **Time-series PV plots** — including capacity factors, scatter comparisons,
        and error metrics.
     2. **High-resolution PV plots** — for clear-sky and cloudy-sky conditions.

   It ensures all visualization outputs for the specified site and year are
   consistently formatted, saved in the correct directory structure, and
   produced with a single function call.

   :param data_sim_meas: DataFrame containing measured and simulated PV time-series data.
                         Must include a `"PV-MEAS"` column representing measured data.
   :type data_sim_meas: pandas.DataFrame
   :param clear_sky_df: High-resolution PV data under clear-sky conditions.
   :type clear_sky_df: pandas.DataFrame
   :param cloudy_sky_df: High-resolution PV data under cloudy-sky conditions.
   :type cloudy_sky_df: pandas.DataFrame
   :param location_name: Name of the analyzed location (e.g., `"Turin"`, `"Utrecht"`).
   :type location_name: str
   :param year: Year corresponding to the PV data (used for labeling and output directories).
   :type year: str
   :param output_root: Root directory where all plots and results will be saved.
                       Defaults to `"results"`.
   :type output_root: str, optional

   :returns: This function does not return any objects. It calls subfunctions that
             generate and save plots to disk.
   :rtype: None

   :raises ValueError: If `data_sim_meas` is empty or lacks required columns.

   .. rubric:: Notes

   - Output files are saved to:
     ```
     {output_root}/{location_name}/Time series analysis results/
     ```
   - If `data_sim_meas` is empty, the function exits without generating plots.

   .. rubric:: Examples

   >>> from simeasren import generate_PV_plots, prepare_pv_data_for_plots
   >>> data_sim_meas, clear_sky_df, cloudy_sky_df = prepare_pv_data_for_plots("Almeria", "2023")
   >>> generate_PV_plots(
   ...     data_sim_meas=data_sim_meas,
   ...     clear_sky_df=clear_sky_df,
   ...     cloudy_sky_df=cloudy_sky_df,
   ...     location_name="Almeria",
   ...     year="2023"
   ... )
   Capacity factors figure successfully saved at 'results\Almeria\Time series analysis results\Almeria2023_Capacity_Factors.png'
   Scatter plot figure successfully saved at 'results\Almeria\Time series analysis results\Almeria2023_scatterplot.png'
   Combined error analysis figure successfully saved at 'results\Almeria\Time series analysis results\Almeria2023_Errors_Analysis.png'
   High-resolution PV plot saved at 'results\Almeria\Time series analysis results\Almeria_highres_clear_vs_cloudy.png'

   The generated plots will include:
     - Time-series comparisons (capacity factor, scatter, error metrics)
     - High-resolution plots for clear and cloudy conditions


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


