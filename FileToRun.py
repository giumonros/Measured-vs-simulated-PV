from src.pv_simulation.pv_set_up import load_pv_setup
from src.pv_simulation.pvgis import download_pvgis_data
from src.pv_simulation.renewables_ninja import download_rn_data
from src.pv_simulation.merge_measured_simulated import merge_with_measured
from src.pv_analysis.plot_all import generate_all_plots

import os

#from measured_vs_simulated_pv.data_loading import load_sim_meas_data, load_high_res_data, merge_high_res_with_sim, filter_data_by_year
#from measured_vs_simulated_pv.plotting import plot_capacity_factors, plot_high_res, plot_metrics


# ---------------User defined----------------
location = "Turin"  # Site name for the analysis (must be existing in the "measured data folder")
year = "2019"  # Select a specific year for the analysis
H2_end_user_min_load = "0"  # Hydrogen end-user flexibility for the techno-economic assessment (minimal load between 0 and 1)
solver = "GUROBI_CMD"  # Or HiGHS. To use other solvers modify the file '3-Techno-eco_assessment.py'
renewablesninja_token = "357952a8676cd53bca5860e5ecafa180c8dc4879"  # Replace with your Renewables.ninja token to be able to use their API, e.g. "12345678910"

Run_simulations = False

# --- Run pv simulations ---

if not os.path.exists(f"data/{location}_meas_sim.csv") or Run_simulations:

    pv_parameters = load_pv_setup(location)
    pvgis_data = download_pvgis_data(location, pv_parameters, save_as_csv = True)
    rn_data = download_rn_data(location, pv_parameters, rn_token=renewablesninja_token, save_as_csv = True)
    merged_df = merge_with_measured(location, pvgis_data, rn_data)

else:
    print(f"Using existing simulation data: {f"data/{location}_meas_sim.csv"}")

# --- Draw plots for time series analysis----

generate_all_plots(location_name=location, year=year)


