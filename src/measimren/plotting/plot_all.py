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
from measimren.plotting import plot_style_config as style_config

import os

# ---------------------------------------------------------------------------
# 1. PV time series plots (capacity factor, scatter, error metrics)
# ---------------------------------------------------------------------------
def generate_PV_timeseries_plots(data_sim_meas, location_name: str, year: str, output_root: str = "results"):

    """
    Generate time series PV plots: capacity factor, scatter, and error metrics.

    Parameters
    ----------
    data_sim_meas : pd.DataFrame
        DataFrame containing measured and simulated PV data.
    location_name : str
        Name of the location (e.g., "Turin").
    year : str
        Year of data to plot.
    output_root : str, optional
        Root output directory to store results.
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

    print(f"PV time series plots successfully generated for {location_name} {year}")


# ---------------------------------------------------------------------------
# 2. High-resolution PV plots (clear & cloudy days)
# ---------------------------------------------------------------------------
def generate_high_res_PV_plots(clear_sky_df, cloudy_sky_df, location_name: str, year: str, output_root: str = "results"):
    """
    Generate high-resolution PV plots for clear and cloudy days.

    Parameters
    ----------
    clear_sky_df : pd.DataFrame
        High-resolution data for clear sky conditions.
    cloudy_sky_df : pd.DataFrame
        High-resolution data for cloudy sky conditions.
    location_name : str
        Name of the location (e.g., "Turin").
    year : str
        Year of data to plot.
    output_root : str, optional
        Root output directory to store results.
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

    print(f" High-resolution PV plots successfully generated for {location_name} {year}")


# ---------------------------------------------------------------------------
# 3 - Wrapper that calls both
# ---------------------------------------------------------------------------
def generate_PV_plots(data_sim_meas, clear_sky_df, cloudy_sky_df, location_name: str, year: str, output_root: str = "results"):
    """
    Wrapper that runs both time series and high-resolution PV plots.
    """

    if data_sim_meas.empty:
        print(f"Year {year} not available for {location_name}, skipping plots.")
        return

    generate_PV_timeseries_plots(data_sim_meas, location_name, year, output_root)
    generate_high_res_PV_plots(clear_sky_df, cloudy_sky_df, location_name, year, output_root)

    print(f" All PV plots successfully generated for {location_name} {year}")


# ---------------------------------------------------------------------------
# 4 - Function for LCOF difference plots
# ---------------------------------------------------------------------------

def generate_LCOF_diff_plot(LCOF_diff_results, location_name: str, year: str, H2_end_user_min_load: float, output_root: str = "results"):
   
    """
    Generate LCOF difference plot for a given location and year.
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

    print(f"LCOF diff plot successfully generated for {location_name} {year}")

