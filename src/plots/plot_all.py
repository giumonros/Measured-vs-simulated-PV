import os
from src.plots.plots import (
    get_legend_names,
    plot_capacity_factors,
    capacity_factor_formatting,
    plot_error_metrics,
    plot_scatter_comparison,
    plot_high_res_days,
    highres_plot_formatting,
    plot_LCOF_diff
)
from src.pv_analysis.metrics import calculate_error_metrics
from src.plots.load_data_for_plots import load_plot_data
from src.H2_techno_eco.LCOF_diff_all import calculate_all_LCOF_diff
import src.plots.plot_style_config as style_config


def generate_all_plots(location_name: str, year: str, output_root: str = "results", PV_sim = True, LCOF_diff = False, H2_end_user_min_load = 0, solver_name = "HiGHS"):
    """
    Generate all plots (capacity factors, scatter, metrics, and high-resolution days)
    for a given location and year.

    Parameters
    ----------
    location_name : str
        Name of the location (e.g., "Turin").
    year : str
        Year of data to plot.
    output_root : str, optional
        Root output directory to store results. Default is "results".
    """

    # -------------------- Create output directories --------------------
    if PV_sim == True:
        output_dir_timeseries = os.path.join(output_root, location_name, "Time series analysis results")
        os.makedirs(output_dir_timeseries, exist_ok=True)

    if LCOF_diff == True:
        output_dir_technoeco = os.path.join(output_root, location_name, "Techno-eco assessments results")
        output_dir_technoeco_syst = os.path.join(output_dir_technoeco, f"End-user flex[{H2_end_user_min_load}-1]","System size and costs")
        os.makedirs(output_dir_technoeco_syst, exist_ok=True)
        
        output_dir_flows = os.path.join(output_dir_technoeco, f"End-user flex[{H2_end_user_min_load}-1]","Hourly profiles")
        os.makedirs(output_dir_flows, exist_ok=True)

    

    # -------------------- Load data --------------------
    data_sim_meas, clear_sky_df, cloudy_sky_df, data_units, year_not_available = load_plot_data(location_name, year)
    
    # Exit if the year or the location does not exist in the measured files
    if year_not_available == True:
        return


    # ----------------- Get legend names for capacity factor, error metrics, LCOF and high-res plots------------
    legend_names, legend_names_high_res = get_legend_names(data_sim_meas, clear_sky_df, cloudy_sky_df)
    
    # -------------------- Capacity Factor Plot --------------------
    colors_CF, linestyles_CF, line_widths_CF = capacity_factor_formatting(
        legend_names= legend_names,
        highlight_label="PV-MEAS"
    )

    if PV_sim == True:
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
        colors_high_res, linestyles_high_res, line_widths_high_res = (
            highres_plot_formatting(
                legend_names_high_res = legend_names_high_res,
                highlight_label="PV-MEAS"
            )
        )

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

    if LCOF_diff == True:
        LCOF_diff_results = calculate_all_LCOF_diff(
            data_sim_meas = data_sim_meas, 
            data_units = data_units,
            location_name = location_name, 
            H2_end_user_min_load = H2_end_user_min_load,
            solver_name = solver_name,
            plot_palette = style_config.PLOT_PALETTE,
            output_dir_technoeco_syst = output_dir_technoeco_syst,
            output_dir_flows = output_dir_flows)
        
        plot_LCOF_diff(
            LCOF_diff_results = LCOF_diff_results,
            location_name = location_name,
            year = year,
            legend_names=legend_names,
            H2_end_user_min_load = H2_end_user_min_load,
            plot_palette = style_config.PLOT_PALETTE,
            output_dir_technoeco = output_dir_technoeco)

    print(f"All plots successfully generated for {location_name}{year}")

