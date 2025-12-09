import os
from .plots import (
    plot_capacity_factors,
    capacity_factor_formatting,
    plot_error_metrics,
    plot_scatter_comparison,
    plot_high_res_days,
    highres_plot_formatting,
    plot_LCOF_diff
)
from ..pv_analysis.metrics import calculate_error_metrics
import plot_style_config as style_config

import os

# ---------------------------------------------------------------------------
# 1. PV time series plots (capacity factor, scatter, error metrics)
# ---------------------------------------------------------------------------
def generate_PV_timeseries_plots(data_sim_meas, location_name: str, year: str, output_root: str = "results"):

    """
    Generate photovoltaic (PV) time-series comparison plots for measured and simulated data.

    This function produces and saves multiple visual analyses for a given location and year:

    - **Capacity factor time-series plot** comparing measured vs. simulated data.  
    - **Scatter comparison plot** between measured and simulated PV outputs.  
    - **Error metrics bar charts** (mean difference, MAE, RMSE).  

    Results are saved under a structured directory within the specified output root.

    Parameters
    ----------
    data_sim_meas : pandas.DataFrame
        DataFrame containing both measured and simulated PV time-series data.  
        Each column represents a dataset (e.g., different simulation tools) and must
        include one column containing `"PV-MEAS"` for measured data.
    location_name : str
        Name of the analyzed location (e.g., "Turin", "Almeria").
    year : str
        Year corresponding to the PV data (used for labeling and output directory naming).
    output_root : str, optional
        Root directory where all plots and results will be saved.  
        Defaults to "results".

    Returns
    -------
    None
        The function does not return any objects. It generates and saves plot images to disk.

    Raises
    ------
    FileNotFoundError
        If required plotting functions or style configuration files are missing.
    ValueError
        If the input DataFrame does not contain measured PV data ("PV-MEAS").

    Notes
    -----
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

    Examples
    --------
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
    """


    # -------------------- Exit function if the year is not available --------------------
    if data_sim_meas.empty:
        print(f"Year {year} not available for {location_name}, skipping plots.")
        return

    # -------------------- Create output directory --------------------
    output_dir_timeseries = os.path.join(output_root, location_name, "Time series analysis results")
    os.makedirs(output_dir_timeseries, exist_ok=True)

    # -------------------- Legend names and formatting --------------------
    legend_names = sorted(set(col.split()[1] for col in data_sim_meas.columns))

    colors_CF, linestyles_CF, line_widths_CF = capacity_factor_formatting(
        legend_names=legend_names,
        highlight_label="PV-MEAS"
    )

    # -------------------- Capacity Factor Plot --------------------
    plot_capacity_factors(
        data_sim_meas=data_sim_meas,
        location_name=location_name,
        year=year,
        legend_names=legend_names,
        colors_CF=colors_CF,
        linestyles_CF=linestyles_CF,
        line_widths_CF=line_widths_CF,
        output_dir_timeseries=output_dir_timeseries,
    )

    # -------------------- Scatter Comparison --------------------
    plot_scatter_comparison(
        data_sim_meas=data_sim_meas,
        location_name=location_name,
        year=year,
        custom_cmap=style_config.CUSTOM_CMAP,
        output_dir_timeseries=output_dir_timeseries,
    )

    # -------------------- Error Metrics --------------------
    mean_diff_results, mae_results, rmse_results = calculate_error_metrics(
        data_sim_meas=data_sim_meas,
        location_name=location_name,
        plot_palette=style_config.PLOT_PALETTE,
        exclude_non_palette = True,
    )

    plot_error_metrics(
        location_name=location_name,
        year=year,
        mean_diff_results=mean_diff_results,
        mae_results=mae_results,
        rmse_results=rmse_results,
        plot_palette=style_config.PLOT_PALETTE,
        legend_names=legend_names,
        output_dir_timeseries=output_dir_timeseries,
    )


# ---------------------------------------------------------------------------
# 2. High-resolution PV plots (clear & cloudy days)
# ---------------------------------------------------------------------------
def generate_high_res_PV_plots(clear_sky_df, cloudy_sky_df, location_name: str, year: str, output_root: str = "results"):

    """
    Generate high-resolution photovoltaic (PV) plots for clear and cloudy sky conditions.

    This function visualizes high-frequency PV time-series data for both clear and 
    cloudy days to assess model performance and temporal dynamics under different 
    weather conditions.

    Parameters
    ----------
    clear_sky_df : pandas.DataFrame
        High-resolution PV data corresponding to clear-sky conditions.
        Each column should represent a different dataset (e.g., measured and simulated values).
    cloudy_sky_df : pandas.DataFrame
        High-resolution PV data corresponding to cloudy-sky conditions.
        Must have the same column naming convention as `clear_sky_df`.
    location_name : str
        Name of the analyzed location (e.g., `"Turin"`, `"Almeria"`).
    year : str
        Year corresponding to the PV data (used for labeling and output directory naming).
    output_root : str, optional
        Root directory where all plots and results will be saved.
        Defaults to `"results"`.

    Returns
    -------
    None
        This function does not return any objects. It generates and saves plot images
        to the specified results directory.

    Raises
    ------
    ValueError
        If input DataFrames are empty or do not contain the expected columns.

    Notes
    -----
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

    Examples
    --------
    >>> from simeasren import generate_high_res_PV_plots, prepare_pv_data_for_plots
    >>> data_sim_meas, clear_sky_df, cloudy_sky_df = prepare_pv_data_for_plots("Almeria", "2023")
    >>> generate_high_res_PV_plots(
    ...     clear_sky_df=clear_sky_df,
    ...     cloudy_sky_df=cloudy_sky_df,
    ...     location_name="Almeria",
    ...     year="2023"
    ... )
    High-resolution PV plot saved at 'results\Almeria\Time series analysis results\Almeria_highres_clear_vs_cloudy.png'

    """
    # -------------------- Create output directory --------------------
    output_dir_timeseries = os.path.join(output_root, location_name, "Time series analysis results")
    os.makedirs(output_dir_timeseries, exist_ok=True)

    # -------------------- Legend names and formatting --------------------
    legend_names_high_res = sorted(
        set(
            col.split()[1]
            for df in [clear_sky_df, cloudy_sky_df]
            for col in df.columns
            if len(col.split()) == 2  # Only two-part column names (e.g., "Almeria PV-MEAS")
        )
    )

    colors_high_res, linestyles_high_res, line_widths_high_res = highres_plot_formatting(
        legend_names_high_res=legend_names_high_res,
        highlight_label="PV-MEAS"
    )

    # -------------------- Plot high-resolution days --------------------
    plot_high_res_days(
        df_clear=clear_sky_df,
        df_cloudy=cloudy_sky_df,
        location_name=location_name,
        legend_names_high_res=legend_names_high_res,
        colors_high_res=colors_high_res,
        linestyles_high_res=linestyles_high_res,
        line_widths_high_res=line_widths_high_res,
        output_dir_timeseries=output_dir_timeseries,
    )


# ---------------------------------------------------------------------------
# 3 - Wrapper that calls both
# ---------------------------------------------------------------------------
def generate_PV_plots(data_sim_meas, clear_sky_df, cloudy_sky_df, location_name: str, year: str, output_root: str = "results"):

    """
    Generate all photovoltaic (PV) plots for a given location and year.

    This wrapper function coordinates the generation of both:
      1. **Time-series PV plots** — including capacity factors, scatter comparisons, 
         and error metrics.
      2. **High-resolution PV plots** — for clear-sky and cloudy-sky conditions.

    It ensures all visualization outputs for the specified site and year are 
    consistently formatted, saved in the correct directory structure, and 
    produced with a single function call.

    Parameters
    ----------
    data_sim_meas : pandas.DataFrame
        DataFrame containing measured and simulated PV time-series data.
        Must include a `"PV-MEAS"` column representing measured data.
    clear_sky_df : pandas.DataFrame
        High-resolution PV data under clear-sky conditions.
    cloudy_sky_df : pandas.DataFrame
        High-resolution PV data under cloudy-sky conditions.
    location_name : str
        Name of the analyzed location (e.g., `"Turin"`, `"Utrecht"`).
    year : str
        Year corresponding to the PV data (used for labeling and output directories).
    output_root : str, optional
        Root directory where all plots and results will be saved.
        Defaults to `"results"`.

    Returns
    -------
    None
        This function does not return any objects. It calls subfunctions that 
        generate and save plots to disk.

    Raises
    ------
    ValueError
        If `data_sim_meas` is empty or lacks required columns.

    Notes
    -----
    - Output files are saved to:
      ```
      {output_root}/{location_name}/Time series analysis results/
      ```
    - If `data_sim_meas` is empty, the function exits without generating plots.

    Examples
    --------
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
    """

    if data_sim_meas.empty:
        print(f"Year {year} not available for {location_name}, skipping plots.")
        return

    generate_PV_timeseries_plots(data_sim_meas, location_name, year, output_root)
    generate_high_res_PV_plots(clear_sky_df, cloudy_sky_df, location_name, year, output_root)


# ---------------------------------------------------------------------------
# 4 - Function for LCOF difference plots
# ---------------------------------------------------------------------------

def generate_LCOF_diff_plot(LCOF_diff_results, location_name: str, year: str, H2_end_user_min_load: float, output_root: str = "results"):

    """
    Generate Levelized Cost of Fuel (LCOF) difference plots for a given location and year.

    This function visualizes the percentage difference in LCOF values between measured
    and simulated datasets for different modeling tools or simulation sources.
    It uses the results from the techno-economic assessment (e.g., obtained via
    `calculate_all_LCOF_diff`) and produces a bar plot comparing performance
    across tools.

    Parameters
    ----------
    LCOF_diff_results : list of dict
        List of dictionaries containing LCOF comparison data for each simulation tool.

        Each dictionary must include:
            - "Location" : str — the location name  
            - "Tool" : str — the name of the simulation tool  
            - "LCOF Difference (%)" : float — percentage difference vs. measured data  
    location_name : str
        Name of the analyzed location (e.g., "Turin", "Almeria", "Utrecht").
    year : str
        Year corresponding to the techno-economic assessment (used for labeling).
    H2_end_user_min_load : float
        Minimum hydrogen end-user load used in the techno-economic calculations
        (e.g., 0.2 for 20% of full load).
    output_root : str, optional
        Root directory where all plots and assessment results are saved.
        Defaults to "results".

    Returns
    -------
    None
        The function does not return any objects. It generates and saves plot files 
        to the output directory.

    Raises
    ------
    ValueError
        If `LCOF_diff_results` is empty or not properly formatted.

    Notes
    -----
    Creates or ensures the existence of the following directory structure::

        {output_root}/{location_name}/Techno-eco assessments results/
            End-user flex[{H2_end_user_min_load}-1]/
                System size and costs/
                Hourly profiles/

    Additional details:
    - Relies on the helper plotting function :func:`plot_LCOF_diff`.
    - Uses the color palette defined in ``style_config.PLOT_PALETTE``.

    Examples
    --------
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
    """
    # -------------------- Create output directories --------------------
    output_dir_technoeco = os.path.join(output_root, location_name, "Techno-eco assessments results")
    output_dir_technoeco_syst = os.path.join(output_dir_technoeco, f"End-user flex[{H2_end_user_min_load}-1]", "System size and costs")
    output_dir_flows = os.path.join(output_dir_technoeco, f"End-user flex[{H2_end_user_min_load}-1]", "Hourly profiles")
    os.makedirs(output_dir_technoeco_syst, exist_ok=True)
    os.makedirs(output_dir_flows, exist_ok=True)

    # -------------------- Legend names --------------------
    
    legend_names = sorted({entry["Tool"] for entry in LCOF_diff_results})

    # -------------------- Compute and Plot LCOF Differences --------------------

    plot_LCOF_diff(
        LCOF_diff_results=LCOF_diff_results,
        location_name=location_name,
        year=year,
        legend_names=legend_names,
        H2_end_user_min_load=H2_end_user_min_load,
        plot_palette=style_config.PLOT_PALETTE,
        output_dir_technoeco=output_dir_technoeco
    )

