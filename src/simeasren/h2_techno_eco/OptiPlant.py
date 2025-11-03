import numpy as np
import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value, getSolver

# Define a function to read csv files (useful to simpliy the writting of the techno-economic optimization function)


def solve_optiplant(data_units, PV_profile, H2_end_user_min_load, solver_name):
    """
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

    Parameters
    ----------
    data_units : pandas.DataFrame
        DataFrame containing techno-economic parameters for all system units.
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
    PV_profile : pandas.DataFrame
        DataFrame containing the renewable power (e.g., solar PV) time-series profile
        used as the main input energy source. Must have at least one column
        with hourly values.
    H2_end_user_min_load : float
        Minimum allowable load for the hydrogen end-user unit (as a fraction of
        maximum capacity, e.g., `0.3` for 30%).
    solver_name : str
        Name of the LP solver to use. Examples include:
        - `"GUROBI_CMD"` (recommended, requires license)
        - `"PULP_CBC_CMD"` (open-source)

    Returns
    -------
    tuple
        A tuple `(fuel_cost, df_results, df_flows)` where:

        - `fuel_cost` (`float`): Production cost of the main fuel (EUR/t).
        - `df_results` (`pandas.DataFrame`): Summary of techno-economic results for each unit,
          including investment, O&M costs, production, capacity, and cost breakdowns.
        - `df_flows` (`pandas.DataFrame`): Detailed time-series of unit flows, power consumption,
          and electricity use.

    Example:
        .. code-block:: python

            (
                875.3,                            # Fuel cost (EUR/t)
                <DataFrame: techno-economic summary>,
                <DataFrame: hourly flow results>
            )

    Raises
    ------
    ValueError
        If required columns are missing from `data_units`, or if the optimization
        produces no results.
    RuntimeError
        If the solver fails to find an optimal solution.

    Notes
    -----
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

    Examples
    --------
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
    """

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
        "Load min (percent of max capacity)",
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
        "Load min (percent of max capacity)"
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

    # Solver

    solver = getSolver(solver_name)  # Solving should takes around 20 seconds per run #Gurobi have to be installed on your computer with a valid license to work

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