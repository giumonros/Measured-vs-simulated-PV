import os
from src.pv_analysis.plots import (
    plot_capacity_factors,
    capacity_factor_formatting,
    plot_error_metrics,
    plot_scatter_comparison,
    plot_high_res_days,
    highres_plot_formatting,
)
from src.pv_analysis.metrics import calculate_error_metrics
from src.pv_analysis.load_data_for_plots import load_plot_data
import src.pv_analysis.plot_style_config as style_config


def generate_all_plots(location_name: str, year: str, output_root: str = "results"):
    """
    Generate all plots (capacity factors, scatter, metrics, and high-resolution days)
    for a given location and year.

    Parameters
    ----------
    location_name : str
        Name of the location (e.g., "Turin").
    year : str
        Year of data to plot (e.g., "2020" or "All years").
    output_root : str, optional
        Root output directory to store results. Default is "results".
    """

    # -------------------- Create output directories --------------------
    output_dir_timeseries = os.path.join(output_root, location_name, "Time series analysis results")
    os.makedirs(output_dir_timeseries, exist_ok=True)

    # -------------------- Load data --------------------
    data_sim_meas, clear_sky_df, cloudy_sky_df = load_plot_data(location_name, year)

    # -------------------- Capacity Factor Plot --------------------
    legend_names, colors_CF, linestyles_CF, line_widths_CF = capacity_factor_formatting(
        data_sim_meas=data_sim_meas,
        highlight_label="PV-MEAS"
    )

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

    # -------------------- High-Resolution (Clear & Cloudy) --------------------
    legend_names_high_res, colors_high_res, linestyles_high_res, line_widths_high_res = (
        highres_plot_formatting(
            clear_sky_df=clear_sky_df,
            cloudy_sky_df=cloudy_sky_df,
            highlight_label="PV-MEAS"
        )
    )

    plot_high_res_days(
        location_name=location_name,
        df_clear=clear_sky_df,
        df_cloudy=cloudy_sky_df,
        legend_names_high_res=legend_names_high_res,
        colors_high_res=colors_high_res,
        linestyles_high_res=linestyles_high_res,
        line_widths_high_res=line_widths_high_res,
        output_dir_timeseries=output_dir_timeseries,
    )

    print(f"All plots successfully generated for {location_name}{year}")

