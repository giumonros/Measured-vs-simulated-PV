import os
from simeasren import *
'''
import sys

# Adjust the sys.path to include the project root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from measimren.pv_simulation import load_pv_setup_from_meas_file, download_pvgis_data, download_rn_data
from measimren.utils import merge_sim_with_measured
from measimren.plotting.plot_all import generate_LCOF_diff_plot, generate_PV_timeseries_plots, generate_high_res_PV_plots
from measimren.plotting.prepare_pv_data import prepare_pv_data_for_plots
from measimren.h2_techno_eco.LCOF_diff_all import calculate_all_LCOF_diff
'''
# ---------------User defined----------------
location = "Utrecht"  # Site name for the analysis (must be existing in the "measured data folder")
year = "2017"  # Select a specific year for the analysis
H2_end_user_min_load = 0  # Hydrogen end-user flexibility for the techno-economic assessment (minimal load between 0 and 1)
solver = "GUROBI_CMD"  # PULP_CBC_CMD or GUROBI_CMD. To use other solvers modify the file '3-Techno-eco_assessment.py'
renewablesninja_token = "your-token-here"  # Replace with your Renewables.ninja token to be able to use their API, e.g. "12345678910"

Run_simulations = False #Change to True to run new simulations

# --- Run pv simulations ---

if Run_simulations:

    pv_parameters = load_pv_setup_from_meas_file(location)
    pvgis_data = download_pvgis_data(location, pv_parameters)
    rn_data = download_rn_data(location, pv_parameters, rn_token=renewablesninja_token)
    #Merge simulations with measured data in the same file and seve
    merge_sim_with_measured(location, pvgis_data, rn_data)

else:
    print(f"Using existing simulation data: results/simulation_pv/{location}_meas_sim.csv")

# --- Extract and format data for plots ----

data_sim_meas, clear_sky_df, cloudy_sky_df = prepare_pv_data_for_plots(location, year)

# --- Draw plots for time series analysis----

generate_PV_timeseries_plots(data_sim_meas, location, year)

# --- Draw plot with high resolution pv data ---

generate_high_res_PV_plots(clear_sky_df, cloudy_sky_df, location, year)

# --- Calculate the different LCOF for all measured and simulated time series ---

LCOF_diff_results = calculate_all_LCOF_diff(data_sim_meas, location, H2_end_user_min_load, solver)

# --- Plot the LCOF diff graph ---

generate_LCOF_diff_plot(LCOF_diff_results, location, year, H2_end_user_min_load)






