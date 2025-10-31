simeasren.h2_techno_eco.OptiPlant
=================================

.. py:module:: simeasren.h2_techno_eco.OptiPlant


Functions
---------

.. autoapisummary::

   simeasren.h2_techno_eco.OptiPlant.solve_optiplant


Module Contents
---------------

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

   :returns: A tuple `(fuel_cost, df_results, df_flows)` where:

             - `fuel_cost` (`float`): Production cost of the main fuel (EUR/t).
             - `df_results` (`pandas.DataFrame`): Summary of techno-economic results for each unit,
               including investment, O&M costs, production, capacity, and cost breakdowns.
             - `df_flows` (`pandas.DataFrame`): Detailed time-series of unit flows, power consumption,
               and electricity use.

             Example:
             ```python
             (
                 875.3,                            # Fuel cost (EUR/t)
                 <DataFrame: techno-economic summary>,
                 <DataFrame: hourly flow results>
             )
             ```
   :rtype: tuple

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


