import pandas as pd
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value, getSolver

# ------------------------------------------------------------------------------------------

# Define location name
location_name = sys.argv[1]
location_year = sys.argv[2]
H2_end_user_min_load = float(
    sys.argv[3]
)  # Values used in the publication are 0, 0.4 or 1
solver_name = sys.argv[4]

# location_name = "Almeria"  # This can be changed to any other location available in the Measured PV data folder
# location_year = "All years" # Write a specific year to avoid drawing graphs for all the years available the Measured PV data file
# H2_end_user_min_load = 0 # Define hydrogen end-user flexibility (minimal load between 0 and 1). Values used in the publication are 0, 0.4 or 1

# Solver
# solver = getSolver('HiGHS') # Solving with HiGHS should take around 180 seconds per run
solver = getSolver(
    solver_name
)  # Solving should takes around 20 seconds per run #Gurobi have to be installed on your computer with a valid license to work

# ----------------------------------------------------------------------------------------------

# Create directory or use the already existing directory for saving graphs and csv files
output_dir = "Results and graphs"
os.makedirs(output_dir, exist_ok=True)
output_dir_technoeco = os.path.join(
    output_dir, location_name, "Techno-eco assessments results"
)
os.makedirs(output_dir_technoeco, exist_ok=True)
output_dir_technoeco_syst = os.path.join(
    output_dir,
    location_name,
    "Techno-eco assessments results",
    f"End-user flex[{H2_end_user_min_load}-1]",
    "System size and costs",
)
os.makedirs(output_dir_technoeco_syst, exist_ok=True)
output_dir_flows = os.path.join(
    output_dir,
    location_name,
    "Techno-eco assessments results",
    f"End-user flex[{H2_end_user_min_load}-1]",
    "Hourly profiles",
)
os.makedirs(output_dir_flows, exist_ok=True)


# Define file path for the simulated and measured PV data file and read the file
folder_profiles = "Simulated and measured PV data"
file_profiles_list = f"{location_name}_meas_sim.csv"
folder_technoeco = "Techno-economic assessment data"
file_technoeco = "Techno-eco_data_NH3.csv"

# Define a function to read csv files (useful to simpliy the writting of the techno-economic optimization function)


def read_csv(file_path, selected_file):
    full_path = os.path.join(file_path, selected_file)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")
    data = pd.read_csv(full_path)
    data = data.fillna(0)
    return data


def solve_optiplant(file_technoeco, PV_profile, H2_end_user_min_load):
    TMstart = 4000
    TMend = 4001
    Tbegin = 240
    Tfinish = 8712  # Time maintenance starts/ends; Tbegin: Time when plants can operate at 0% load

    # Create time arrays
    Time = np.concatenate(
        [np.arange(1, TMstart + 1), np.arange(TMend, Tfinish + 1)]
    ).tolist()
    T = len(Time)

    Tstart = np.concatenate(
        [np.arange(1, TMstart + 1), np.arange(TMend, Tfinish + 1)]
    ).tolist()

    # Handle the condition for Tbegin
    if Tbegin >= 2:
        Tstart = np.delete(
            Tstart, np.arange(0, Tbegin)
        )  # Remove the first Tbegin elements

    # -------------------------- Read and format data ------------------------------

    # --------------Techno-economics data--------------------
    data_units = read_csv(folder_technoeco, file_technoeco)

    # Subsets and related data
    subsets = data_units["Subsets"].tolist()
    n_subsets = len(subsets)

    subsets_2 = data_units["Subsets_2"].tolist()
    subsets_reactants = data_units["Produced from"].tolist()
    n_sub_reac = len(subsets_reactants)

    # Reactants used to produce the main product (chemical reactions)
    reactants = np.zeros(n_sub_reac, dtype=int)

    for i in range(n_subsets):  # Get the line numbers of the reactants
        for j in range(n_sub_reac):
            if subsets[i] == subsets_reactants[j]:
                reactants[j] = i

    # Filter out zeros and calculate R
    reactants = [x for x in reactants if x != 0]

    # Main fuel unit (e.g., Ammonia plant)
    main_fuel = [i for i, x in enumerate(subsets_2) if "MainFuel" in x]

    # Power unit that generates electricity
    pu = [i for i, x in enumerate(subsets) if "PU" in x]

    # Renewable power unit (profile dependent)
    rpu = [i for i, x in enumerate(subsets) if "RPU" in x]

    # Products of the energy system
    products = [i for i, x in enumerate(subsets) if "Product" in x]
    n_prod = len(products)

    # Products where minimal demands have to be respected
    min_d = [i for i, x in enumerate(subsets_2) if "Min_demand" in x]

    # Storage tank (mass or electrical)
    tanks = [i for i, x in enumerate(subsets) if x == "Tank"]
    n_st = len(tanks)

    # Storage input/output (hydrogen and batteries)
    stor_in = [i for i, x in enumerate(subsets) if x == "Stor_in"]
    stor_out = [i for i, x in enumerate(subsets) if x == "Stor_out"]

    # After subsets, get techno-economic data and put it in the correct variables

    required_columns = [
        "Type of units",
        "Subsets",
        "Subsets_2",
        "H2 balance",
        "El balance",
        "Max Capacity",
        "Load min (% of max capacity)",
        "Electrical consumption (kWh/output)",
        "Fuel production rate (kg output/kg input)",
        "Investment (EUR/Capacity installed)",
        "Fixed cost (EUR/Capacity installed/y)",
        "Variable cost (EUR/Output)",
        "Yearly demand (kg fuel)",
        "Annuity factor",
    ]
    for col in required_columns:
        if col not in data_units.columns:
            raise ValueError(f"Missing required column: {col}")

    # Extract data from the techno-economics data file
    unit_name = data_units["Type of units"].tolist()
    U = len(unit_name)

    used_unit = data_units[
        "Used (1 or 0)"
    ].tolist()  # Indicates if the unit is used in the energy system
    flow_tag = (
        data_units["Legend flows"].astype(str).tolist()
    )  # Head-lines for the output CSV file
    h2_balance = data_units["H2 balance"].tolist()
    el_balance = data_units["El balance"].tolist()
    # max_cap = data_units["Max Capacity"].tolist()  # Maximum capacity that can be installed
    load_min = data_units[
        "Load min (% of max capacity)"
    ].tolist()  # Minimum load of the unit
    sc_nom = data_units[
        "Electrical consumption (kWh/output)"
    ].tolist()  # Specific electrical consumption
    prod_rate = data_units[
        "Fuel production rate (kg output/kg input)"
    ].tolist()  # Fuel production
    invest = data_units[
        "Investment (EUR/Capacity installed)"
    ].tolist()  # Investment cost
    fix_om = data_units[
        "Fixed cost (EUR/Capacity installed/y)"
    ].tolist()  # Fixed operation and maintenance costs
    var_om = data_units[
        "Variable cost (EUR/Output)"
    ].tolist()  # Variable operation and maintenance costs
    demand = data_units["Yearly demand (kg fuel)"].tolist()  # Output fuel demand
    annuity_factor = data_units[
        "Annuity factor"
    ].tolist()  # Check the Excel for detailed calculations

    # Modify the hydrogen end-user minimal load (assumes H2 end-user is the first entry in techno-economic data)
    load_min[0] = H2_end_user_min_load

    # ------------------- Profile data ---------------------------

    # Flux profiles
    flux_profile = np.zeros(T)
    for t in range(T):
        flux_profile[t] = PV_profile.iloc[
            Time[t] - 1, 0
        ]  # Adjusted for 0-based indexing and include maintenance time

    # ------------------------- Model -------------------------
    # Initialize the model
    model_lp = LpProblem("TechnoEconomicOptimization", LpMinimize)

    # ------------------------- Decision Variables -------------------------
    # Total cost
    costs = LpVariable("Costs", lowBound=0)

    # Products and energy flow
    X = {(u, t): LpVariable(f"X_{u}_{t}", lowBound=0) for u in range(U) for t in Time}

    # Production capacity of each unit
    capacity = {u: LpVariable(f"Capacity_{u}", lowBound=0) for u in range(U)}

    # Quantity of products sold
    sold = {
        (u, t): LpVariable(f"Sold_{u}_{t}", lowBound=0) for u in range(U) for t in Time
    }

    # Quantity of input bought
    bought = {
        (u, t): LpVariable(f"Bought_{u}_{t}", lowBound=0)
        for u in range(U)
        for t in Time
    }

    # ------------------------- Constraints -------------------------
    # Set upper bounds for unused units
    for t in Time:
        for u in range(U):
            if used_unit[u] == 0:
                model_lp += X[(u, t)] <= 0
                model_lp += capacity[u] <= 0
                model_lp += sold[(u, t)] <= 0
                model_lp += bought[(u, t)] <= 0

    # ------------------------- Objective Function -------------------------
    # Minimize the total cost
    model_lp += costs, "Minimize_Costs"

    # Costs equation
    costs_expr = lpSum(
        (invest[u] * annuity_factor[u] + fix_om[u]) * capacity[u] for u in range(U)
    ) + lpSum(var_om[u] * X[(u, t)] for u in range(U) for t in Time)
    model_lp += costs == costs_expr, "Costs_Equation"

    # ------------------------- Constraints -------------------------

    # Yearly demand: fulfill minimum yearly demand if there is one
    for i in min_d:
        model_lp += lpSum(sold[(i, t)] for t in Time) == demand[i], f"YearlyDemand_{i}"

    # Capacity constraints
    # if Option_max_capacity:
    #    for u in range(U):
    #        model_lp += capacity[u] <= max_cap[u], f"MaxCapacity_{u}"

    # Load constraints
    for u in range(U):
        for t in Tstart:
            model_lp += X[(u, t)] >= capacity[u] * load_min[u]  # Min flow
        for t in Time:
            model_lp += X[(u, t)] <= capacity[u]  # Max flow

    # Production rates
    for i in range(n_prod):
        for t in Time:
            model_lp += (
                X[(products[i], t)] == X[(reactants[i], t)] * prod_rate[products[i]]
            )

    # Hydrogen balance
    for t in Time:
        model_lp += lpSum(h2_balance[u] * X[(u, t)] for u in range(U)) == 0

    # Storage balance
    for i in range(n_st):
        for t in range(1, T + 1):
            model_lp += (
                X[(tanks[i], Time[t - 1])]
                == (X[(tanks[i], Time[t - 2])] if t > 1 else 0)
                + X[(stor_in[i], Time[t - 1])]
                - X[(stor_out[i], Time[t - 1])]
            )

    # Renewable energy production constraint (profile dependent)
    for t in range(1, T + 1):
        model_lp += X[(rpu[0], Time[t - 1])] == flux_profile[t - 1] * capacity[rpu[0]]

    # Electricity produced and consumed must be at equilibrium
    for t in Time:
        model_lp += lpSum(el_balance[u] * X[(u, t)] for u in range(U)) == lpSum(
            sc_nom[u] * X[(u, t)] for u in range(U)
        )

    # Sold and bought outputs/inputs
    for u in range(U):
        for t in Time:
            model_lp += sold[(u, t)] <= X[(u, t)]  # Sold <= Produced
            model_lp += bought[(u, t)] == X[(u, t)]  # Bought == Used

    # ------------------------- Solve the Model -------------------------

    model_lp.solve(solver)  # Default solver (cbc)

    # ---------------------- Results Output ----------------------

    if model_lp.status != 1:  # 1 indicates "Optimal"
        raise RuntimeError(f"Solver failed with status: {LpStatus[model_lp.status]}")

    if LpStatus[model_lp.status] == "Optimal":
        # Total electricity consumption
        sc_tot = [
            sum(sc_nom[u] * X[(u, Time[t - 1])].varValue for u in range(U))
            for t in range(1, T + 1)
        ]

        # Flows
        solution_x = [
            [X[(u, Time[t - 1])].varValue for u in range(U)] for t in range(1, T + 1)
        ]
        df_flows = pd.DataFrame(solution_x, columns=flow_tag)
        df_flows.insert(0, "Time", Time)  # Insert the time column as first column
        df_flows["Electricity consumption"] = (
            sc_tot  # Insert electrical consumption as last column
        )

        # ---------------------- Main Results ----------------------
        R_fixOM = [0] * U
        R_varOM = [0] * U
        R_invest = [0] * U
        R_invest_year = [0] * U
        R_production = [0] * U
        R_capacity = [0] * U
        R_El_cons = [0] * U
        R_cost_unit = [0] * U
        R_load_av = [0] * U
        R_FLH = [0] * U
        R_prodcost_fuel = [0] * U
        R_prodcost_perunit = [0] * U
        R_elec_cost = [0] * U

        for u in range(U):
            R_capacity[u] = capacity[u].varValue * 1e-3  # Convert to MW or t/h
            R_invest[u] = invest[u] * capacity[u].varValue * 1e-6  # Convert to M€
            R_invest_year[u] = R_invest[u] * annuity_factor[u]  # Annualized investment
            R_fixOM[u] = fix_om[u] * capacity[u].varValue * 1e-6  # Convert to M€
            R_varOM[u] = (
                sum(var_om[u] * X[(u, t)].varValue for t in Time) * 1e-6
            )  # Convert to M€
            R_production[u] = (
                sum(X[(u, t)].varValue for t in Time) * 1e-6
            )  # ktons or GWh
            R_cost_unit[u] = R_invest_year[u] + R_fixOM[u] + R_varOM[u]

            if capacity[u].varValue != 0:
                R_load_av[u] = sum(
                    X[(u, t)].varValue / capacity[u].varValue for t in Time
                ) * (1 / T)
            else:
                R_load_av[u] = 0

            R_FLH[u] = R_load_av[u] * T
            R_El_cons[u] = sum(sc_nom[u] * X[(u, t)].varValue for t in Time) * 1e-6

            if R_production[u] == 0:
                R_prodcost_perunit[u] = 0
            else:
                R_prodcost_perunit[u] = R_cost_unit[u] / R_production[u]

        for u in main_fuel:
            R_prodcost_fuel[u] = (value(model_lp.objective) * 1e-6) / R_production[u]

        R_elec_cost_1 = (
            1e3
            * sum(R_prodcost_perunit[u] * R_production[u] for u in pu)
            / sum(R_production[u] for u in pu)
        )
        for u in range(U):
            R_elec_cost[u] = R_elec_cost_1

        # Create DataFrame for results
        df_results = pd.DataFrame(
            {
                "Type of unit": unit_name,
                "Installed capacity (MW, t/h, MWh, t)": R_capacity,
                "Total investment (MEUR)": R_invest,
                "Annualised investment (MEUR)": R_invest_year,
                "Fixed O&M (MEUR)": R_fixOM,
                "Variable O&M (MEUR)": R_varOM,
                "Cost per unit (MEUR)": R_cost_unit,
                "Production (kton or GWh)": R_production,
                "Electricity consumption (GWh)": R_El_cons,
                "Production cost fuel (EUR/kg)": R_prodcost_fuel,
                "Load average": R_load_av,
                "Full load hours": R_FLH,
                "Average electricity cost (EUR/MWh)": R_elec_cost,
            }
        )

        # Rename columns
        result_columns = [
            "Type of unit",
            "Installed capacity (MW, t/h, MWh, t)",
            "Total investment (MEUR)",
            "Annualised investment (MEUR)",
            "Fixed O&M (MEUR)",
            "Variable O&M (MEUR)",
            "Cost per unit (MEUR)",
            "Production (kton or GWh)",
            "Electricity consumption (GWh)",
            "Production cost fuel (EUR/kg)",
            "Load average",
            "Full load hours",
            "Average electricity cost (EUR/MWh)",
        ]
        df_results.columns = result_columns

    else:
        print("No optimal solution available")

    # Display fuel cost for the H2 end-user
    fuel_cost = R_prodcost_fuel[0] * 1000  # Assumes H2 is first in techno-economic data
    print(f"Fuel cost: {fuel_cost} EUR/t")

    if df_results.empty:
        raise ValueError(
            "Optimization produced no results. Check constraints or input data."
        )

    return fuel_cost, df_results, df_flows


# ------------------------------- Plot the LCOF graph and save the multiple csv results----------------------

# Read file with measured and simulated power profiles
data_sim_meas = read_csv(folder_profiles, file_profiles_list)

# Function to extract a specific row number


def get_row_number(data_file, row_name):
    # Find the row index where 'Index' is located
    idx_row = data_file[data_file.iloc[:, 0] == row_name].index
    if len(idx_row) == 0:
        raise ValueError(f"Could not find {row_name} row in the file.")
    idx_row = idx_row[0]

    return idx_row


# Extract the relevant row indexes from the file
index_row = get_row_number(data_sim_meas, "Index")
profile_time_series_row = get_row_number(data_sim_meas, "Profile time series")
locations_row = get_row_number(data_sim_meas, "Locations")
selected_rows_for_headers = data_sim_meas.iloc[[locations_row, profile_time_series_row]]

# Define color palette for bar plots with LCOF
plot_palette = {
    'RN-MERRA2': 'blue',
    'RN-SARAH': 'dodgerblue',
    'PG2-SARAH': 'gold',
    'PG2-SARAH2': 'orange',
    'PG3-SARAH3': 'sienna',
    'PG2-ERA5': 'limegreen',
    'PG3-ERA5': 'green',
    'SIM-SELF1': 'purple'
}

# Extract headers from the rows above 'Index'
# headers = data_sim_meas.iloc[:index_row].T.fillna("").agg(" ".join, axis=1)  # Merge multi-headers into a single row
headers = selected_rows_for_headers.T.fillna("").agg(" ".join, axis=1)
# Assign the new headers to the DataFrame
data_sim_meas.columns = headers

# Remove the first column
data_sim_meas = data_sim_meas.iloc[:, 1:]

# Remove the years that are not wanted for the figures (user defined)

## Check if any column name contains the user specified year
columns_with_year = [col for col in data_sim_meas.columns if location_year in col]

## If columns are found for the specified year, keep only those
if columns_with_year:
    data_sim_meas = data_sim_meas[columns_with_year]
else:
    ## Otherwise, retain all columns
    print(f"No specific year chosen or year not available: plot for all years instead")

# Identify unique locations
locations = list(set(col.split()[0] for col in data_sim_meas.columns))
# Identify unique time series for legend names
legend_names = list(set(col.split()[1] for col in data_sim_meas.columns))

# Keep only data below 'Index'
data_sim_meas = data_sim_meas.iloc[index_row + 1 :].reset_index(drop=True)

# Convert all values to numeric
data_sim_meas = data_sim_meas.apply(pd.to_numeric, errors="coerce")

# Initialize LCOF_diff results
LCOF_diff_results = []

# Process data for each location and year
for location in locations:
    # Filter columns for the current location
    loc_data = data_sim_meas[[col for col in data_sim_meas.columns if location in col]]

    # Identify 'PV-MEAS' column as the measured data
    meas_column = next((col for col in loc_data.columns if "PV-MEAS" in col), None)
    if meas_column is None:
        print(f"Skipping {location}: 'PV-MEAS' column missing.")
        continue
    # Perform the techno-economic assessment with the measured data
    measured_profile_LCOF = loc_data[[meas_column]].dropna()
    LCOF_meas, df_results_meas, df_flows_meas = solve_optiplant(
        file_technoeco, measured_profile_LCOF, H2_end_user_min_load
    )
    output_file_tech_meas = f"{meas_column}.csv"
    df_results_meas.to_csv(
        os.path.join(output_dir_technoeco_syst, output_file_tech_meas), index=False
    )
    output_file_flow_meas = f"{meas_column}.csv"
    df_flows_meas.to_csv(
        os.path.join(output_dir_flows, output_file_flow_meas), index=False
    )

    # Identify simulations columns with only zero values
    valid_columns = [meas_column] + [
        col
        for col in loc_data.columns
        if col != meas_column and not loc_data[col].eq(0).all()
    ]

    # Calculate and store LCOF for each simulation tool/time series
    for sim_column in valid_columns:
        if sim_column != meas_column and any(
            tool in sim_column for tool in plot_palette.keys()
        ):
            simulated_profile_LCOF = loc_data[[sim_column]].dropna()
            LCOF_sim, df_results_sim, df_flows_sim = solve_optiplant(
                file_technoeco, simulated_profile_LCOF, H2_end_user_min_load
            )
            output_file_tech_sim = f"{sim_column}.csv"
            df_results_sim.to_csv(
                os.path.join(output_dir_technoeco_syst, output_file_tech_sim),
                index=False,
            )
            output_file_flow_sim = f"{sim_column}.csv"
            df_flows_sim.to_csv(
                os.path.join(output_dir_flows, output_file_flow_sim), index=False
            )
            LCOF_diff = (LCOF_sim - LCOF_meas) / LCOF_meas * 100
            LCOF_diff_results.append(
                {
                    "Location": location,
                    "Tool": sim_column.split()[1],
                    "LCOF Difference (%)": LCOF_diff,
                }
            )

# Plot for LCOF error analysis


def add_labels(ax):
    for p in ax.patches:
        height = p.get_height()
        if abs(height) > 1e-3:  # Ignore near-zero bars to prevent "0.0" labels
            if height >= 0:
                ax.annotate(
                    format(height, ".1f"),
                    (p.get_x() + p.get_width() / 2.0, height),
                    ha="center",
                    va="bottom",
                    xytext=(0, 5),
                    textcoords="offset points",
                    fontsize=11,
                )
            else:
                ax.annotate(
                    format(height, ".1f"),
                    (p.get_x() + p.get_width() / 2.0, height),
                    ha="center",
                    va="top",
                    xytext=(0, -5),
                    textcoords="offset points",
                    fontsize=11,
                )


# Extract the tool order from the palette (ensures tools are plotted in this specific order)
tool_order = list(plot_palette.keys())

# Create dataframe for plotting
LCOF_diff_df = pd.DataFrame(LCOF_diff_results)
# Sort DataFrames by Location
LCOF_diff_df.sort_values(by="Location", inplace=True)

# Compute min and max values with padding
y_min = LCOF_diff_df["LCOF Difference (%)"].min()
y_max = LCOF_diff_df["LCOF Difference (%)"].max()
padding = (y_max - y_min) * 0.3  # 30% padding

# Ensure zero is always visible on the y-axis
y_min = min(0, y_min - padding)
y_max = max(0, y_max + padding)

# Check if LCOF Difference values are mostly negative
mostly_negative = np.median(LCOF_diff_df["LCOF Difference (%)"]) < 0

# Create the figure
plt.figure(figsize=(10, 6))

# Define tick font size
tick_font_size = 16

# Plot LCOF Difference
ax = sns.barplot(
    x="Location",
    y="LCOF Difference (%)",
    hue="Tool",
    data=LCOF_diff_df,
    palette=plot_palette,
    hue_order=tool_order,
)

# Customize plot
ax.set_ylabel("LCOF difference (%)", fontsize=20)
ax.tick_params(axis="both", labelsize=tick_font_size)
ax.set_axisbelow(True)
ax.grid(True, axis="y")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}"))
ax.set_ylim(y_min, y_max)
ax.set_xlabel("")

# Add labels
add_labels(ax)

# Move x-axis labels above if mostly negative
if mostly_negative:
    ax.xaxis.set_label_position("top")
    ax.xaxis.tick_top()
    plt.subplots_adjust(top=0.85)

# Filter legend to only show labels in `legend_names`
handles, labels = ax.get_legend_handles_labels()
filtered_handles_labels = [(h, l) for h, l in zip(handles, labels) if l in legend_names]
filtered_handles, filtered_labels = (
    zip(*filtered_handles_labels) if filtered_handles_labels else ([], [])
)

# Add filtered legend below the figure
legend = ax.legend(
    filtered_handles,
    filtered_labels,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.05),
    ncol=3,
    fontsize=16,
    title_fontsize=18,
    frameon=False,
)

# Adjust layout
plt.tight_layout()

# Save the figure
plt.savefig(
    os.path.join(
        output_dir_technoeco,
        f"{location_name}_LCOF_diff_flex[{H2_end_user_min_load}-1].png",
    )
)
print(
    f"LCOF difference figure successfully generated in the '{output_dir}' folder for {location_name}"
)
plt.close()
