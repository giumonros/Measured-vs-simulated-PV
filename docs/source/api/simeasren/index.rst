simeasren
=========

.. py:module:: simeasren


Submodules
----------

.. toctree::
   :maxdepth: 1

   /api/simeasren/h2_techno_eco/index
   /api/simeasren/plotting/index
   /api/simeasren/pv_analysis/index
   /api/simeasren/pv_simulation/index
   /api/simeasren/utils/index


Functions
---------

.. autoapisummary::

   simeasren.load_pv_setup_from_meas_file
   simeasren.download_pvgis_data
   simeasren.download_rn_data
   simeasren.calculate_error_metrics
   simeasren.merge_sim_with_measured
   simeasren.generate_LCOF_diff_plot
   simeasren.generate_PV_timeseries_plots
   simeasren.generate_high_res_PV_plots
   simeasren.generate_PV_plots
   simeasren.prepare_pv_data_for_plots
   simeasren.calculate_all_LCOF_diff
   simeasren.solve_optiplant


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

   >>> from simeasren import load_pv_setup_from_meas_file
   >>> parameters = load_pv_setup_from_meas_file("Almeria")
   >>> parameters["System loss"]
   9.75
   >>> parameters["PV technology"]
   'crystSi'


.. py:function:: download_pvgis_data(location_name: str, pv_parameters)

   Download simulated PV power output data from PVGIS for a specified location.

   This function queries the PVGIS API for multiple databases and versions to
   generate hourly PV power output for the given PV system parameters.
   The resulting data are saved as CSV files in the project directory and
   returned as a dictionary for further analysis.

   :param location_name: Name of the location/site (e.g., "Almeria") used for file naming and
                         labeling downloaded data.
   :type location_name: str
   :param pv_parameters: Dictionary containing PV system configuration parameters.

                         **Expected keys:**
                             - "Latitude" : float — geographic latitude
                             - "Longitude" : float — geographic longitude
                             - "Tilt" : float — tilt angle of PV modules (degrees)
                             - "Azimuth" : float — azimuth of PV modules (degrees)
                             - "Max capacity simulation" : float — peak PV power in kW
                             - "System loss" : float — system losses in %
                             - "PV technology" : str — PV technology type (e.g., "crystalline silicon")
                             - "Building/free" : str — mounting type ("building" or "free")
                             - "Start year" : int — first year of simulation
                             - "End year" : int — last year of simulation
   :type pv_parameters: dict

   :returns: Dictionary of PVGIS simulation outputs.

             **Keys**
                 str — unique identifiers in the format
                 ``"{location_name}{year} PG{version}-{database}"``
                 Example: ``"Almeria2020 PG3-SARAH3"``

             **Values**
                 numpy.ndarray — hourly PV power output in kW.
   :rtype: dict

   :raises requests.exceptions.RequestException: If a network request to PVGIS fails.
   :raises FileNotFoundError: If the output directory cannot be created or written to.
   :raises ValueError: If PVGIS CSV data cannot be parsed correctly.

   .. rubric:: Notes

   - Output CSV files are saved to:

       results/{location_name}/simulated_PV/PVGIS/

   - PVGIS API versions used:
       - v5_2 : "PVGIS-SARAH", "PVGIS-SARAH2", "PVGIS-ERA5"
       - v5_3 : "PVGIS-SARAH3", "PVGIS-ERA5"
   - Power output in the CSV is converted from W → kW and stored in the "P_kW" column.
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


.. py:function:: calculate_all_LCOF_diff(data_sim_meas, location_name, H2_end_user_min_load, solver_name, technoeco_file_name='Techno_eco_data_NH3')

   Calculate the difference in Levelized Cost of Fuel (LCOF) between
   measured and simulated data for a given location.

   This function performs a techno-economic analysis by comparing the
   measured energy production profile with multiple simulated profiles
   for the specified location. For each dataset, it computes the LCOF
   using the `solve_optiplant` optimization model, stores detailed
   results and flow data as CSV files, and calculates the relative
   difference in LCOF between measured and simulated cases.

   :param data_sim_meas: DataFrame containing both simulated and measured time-series data
                         for one or more locations. Each column name should include the
                         location name, and the measured data column should contain "PV-MEAS".
   :type data_sim_meas: pandas.DataFrame
   :param location_name: Name of the location to analyze (used to filter columns in
                         `data_sim_meas`).
   :type location_name: str
   :param H2_end_user_min_load: Minimum hydrogen end-user load (fraction of nominal load)
                                to be considered in the techno-economic model.
   :type H2_end_user_min_load: float
   :param solver_name: Name of the optimization solver to use (e.g., "PULP_CBC_CMD",
                       "GUROBI_CMD", "CPLEX_CMD").
   :type solver_name: str
   :param technoeco_file_name: Base filename (without extension) of the techno-economic data CSV file.
                               Defaults to "Techno_eco_data_NH3".
   :type technoeco_file_name: str, optional

   :returns: A list of dictionaries, each containing:

             - "Location" (str): Name of the analyzed location.
             - "Tool" (str): Identifier of the simulation tool or dataset.
             - "LCOF Difference (%)" (float): Relative difference in LCOF between
               simulated and measured data.
   :rtype: list of dict

   :raises FileNotFoundError: If the specified techno-economic CSV file does not exist.
   :raises ValueError: If no measured data column (containing "PV-MEAS") is found for the
       given location.

   .. rubric:: Notes

   The function assumes that the `solve_optiplant()` function is available
   in the current environment and returns:
   (LCOF_value, technoeco_results_df, flow_results_df).

   Intermediate results (system costs and hourly flow profiles) are saved
   automatically in the folders `System size and costs` and `Hourly profiles`

   .. rubric:: Examples

   Import and run the function using a CSV with simulated and measured PV data:

       >>> from simeasren import calculate_all_LCOF_diff, prepare_pv_data_for_plots
       >>> data_sim_meas, _, _ = prepare_pv_data_for_plots("Utrecht", "2017")
       >>> results = calculate_all_LCOF_diff(
       ...     data_sim_meas=data_sim_meas,
       ...     location_name="Utrecht",
       ...     H2_end_user_min_load=0.3,
       ...     solver_name="GUROBI_CMD",
       ...     technoeco_file_name="Techno_eco_data_NH3"
       ... )
       >>> results[0]
       {'Location': 'Utrecht', 'Tool': 'PG2-SARAH2', 'LCOF Difference (%)': -6.3}


.. py:function:: solve_optiplant(data_units, PV_profile, H2_end_user_min_load, solver_name)

   Perform a techno-economic optimization of an integrated energy system.

   This function formulates and solves a linear programming (LP) model
   to determine the optimal design and operation of an energy system
   (e.g., hydrogen and ammonia production plant). It minimizes the
   total annualized cost subject to technical, economic, and operational
   constraints, using the specified solver.

   The optimization considers investment, fixed and variable O&M costs,
   production rates, storage balances, renewable profiles, and
   techno-economic parameters for each subsystem. It returns both
   aggregated economic results and detailed hourly flow data.

   :param data_units: DataFrame containing techno-economic parameters for all system units.
                      Must include the following columns:
                      - `"Type of units"`
                      - `"Subsets"`, `"Subsets_2"`, `"Produced from"`
                      - `"H2 balance"`, `"El balance"`
                      - `"Max Capacity"`
                      - `"Load min (percent of max capacity)"`
                      - `"Electrical consumption (kWh/output)"`
                      - `"Fuel production rate (kg output/kg input)"`
                      - `"Investment (EUR/Capacity installed)"`
                      - `"Fixed cost (EUR/Capacity installed/y)"`
                      - `"Variable cost (EUR/Output)"`
                      - `"Yearly demand (kg fuel)"`
                      - `"Annuity factor"`
                      - `"Used (1 or 0)"`
                      - `"Legend flows"`

                      These data define the structure, interconnections, and cost
                      characteristics of each unit in the modeled system.
   :type data_units: pandas.DataFrame
   :param PV_profile: DataFrame containing the renewable power (e.g., solar PV) time-series profile
                      used as the main input energy source. Must have at least one column
                      with hourly values.
   :type PV_profile: pandas.DataFrame
   :param H2_end_user_min_load: Minimum allowable load for the hydrogen end-user unit (as a fraction of
                                maximum capacity, e.g., `0.3` for 30%).
   :type H2_end_user_min_load: float
   :param solver_name: Name of the LP solver to use. Examples include:
                       - `"GUROBI_CMD"` (recommended, requires license)
                       - `"PULP_CBC_CMD"` (open-source)
   :type solver_name: str

   :returns: * *tuple* -- A tuple `(fuel_cost, df_results, df_flows)` where:

               - `fuel_cost` (`float`): Production cost of the main fuel (EUR/t).
               - `df_results` (`pandas.DataFrame`): Summary of techno-economic results for each unit,
                 including investment, O&M costs, production, capacity, and cost breakdowns.
               - `df_flows` (`pandas.DataFrame`): Detailed time-series of unit flows, power consumption,
                 and electricity use.
             * *Example* --

               .. code-block:: python

                   (
                       875.3,                            # Fuel cost (EUR/t)
                       <DataFrame: techno-economic summary>,
                       <DataFrame: hourly flow results>
                   )

   :raises ValueError: If required columns are missing from `data_units`, or if the optimization
       produces no results.
   :raises RuntimeError: If the solver fails to find an optimal solution.

   .. rubric:: Notes

   - Maintenance periods and partial operation times are modeled explicitly
     (e.g., `TMstart`, `TMend`, `Tbegin`, `Tfinish`).
   - The model assumes steady-state balance of electricity and hydrogen at each timestep.
   - Storage dynamics are represented with inflow/outflow constraints and
     mass balance equations.
   - The cost objective includes investment annuities, fixed, and variable O&M components.
   - The hydrogen end-user minimal load constraint is modified based on
     `H2_end_user_min_load`.

   The LP model is constructed using **PuLP** and solved using the chosen backend solver.
   Optimal solutions typically take 5-10 seconds with Gurobi and 180 seconds with cbc.

   .. rubric:: Examples

   >>> import pandas as pd
   >>> from simeasren import solve_optiplant
   >>> technoeco_data = pd.read_csv("Techno_eco_data_NH3.csv")
   >>> pv_profile = pd.read_csv("Somewhere_PV_profile.csv")
   >>> fuel_cost, df_results, df_flows = solve_optiplant(
   ...     data_units=technoeco_data,
   ...     PV_profile=pv_profile,
   ...     H2_end_user_min_load=0.3,
   ...     solver_name="GUROBI_CMD"
   ... )
   >>> print(f"Fuel cost: {fuel_cost:.2f} EUR/t")
   Fuel cost: 875.32 EUR/t
   >>> df_results.head()
     Type of unit  Installed capacity (MW, t/h, MWh, t)  ...  Full load hours
   0      Electrolyzer                             120.5  ...           5900.0
   1           Tank                                  2.3  ...           4500.0
   >>> df_flows.head()
      Time  Electrolyzer  Tank  Electricity consumption
   0     1        100.0   0.0                     350.0
   1     2        100.0   0.0                     350.0


