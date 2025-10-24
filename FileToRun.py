from src.pv_simulation.pv_set_up import load_pv_setup
from src.pv_simulation.pvgis import download_pvgis_data
from src.pv_simulation.renewables_ninja import download_rn_data
from src.pv_simulation.merge_measured_simulated import merge_with_measured
from src.plots.plot_all import generate_all_plots

import os

# ---------------User defined----------------
location = "Utrecht"  # Site name for the analysis (must be existing in the "measured data folder")
year = "2017"  # Select a specific year for the analysis
H2_end_user_min_load = 0  # Hydrogen end-user flexibility for the techno-economic assessment (minimal load between 0 and 1)
solver = "GUROBI_CMD"  # Or HiGHS. To use other solvers modify the file '3-Techno-eco_assessment.py'
renewablesninja_token = "your-token-here"  # Replace with your Renewables.ninja token to be able to use their API, e.g. "12345678910"

Run_simulations = False #Change to True to run new simulations

# --- Run pv simulations ---

if not os.path.exists(f"data/{location}_meas_sim.csv") or Run_simulations:

    pv_parameters = load_pv_setup(location)
    pvgis_data = download_pvgis_data(location, pv_parameters, save_as_csv = True)
    rn_data = download_rn_data(location, pv_parameters, rn_token=renewablesninja_token, save_as_csv = True)
    merged_df = merge_with_measured(location, pvgis_data, rn_data)

else:
    print(f"Using existing simulation data: data/{location}_meas_sim.csv")

# --- Draw plots for time series analysis----

generate_all_plots(
    location_name=location,
    year=year,
    PV_sim = True, #Change to false to avoid doing or re-doing all the time series analysis graphs
    LCOF_diff = True, #Change to false to avoid doing or re-doing the LCOF analysis
    H2_end_user_min_load = H2_end_user_min_load,
    solver_name = solver
)



