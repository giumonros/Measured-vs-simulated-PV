simeasren.h2_techno_eco.LCOF_diff_all
=====================================

.. py:module:: simeasren.h2_techno_eco.LCOF_diff_all


Functions
---------

.. autoapisummary::

   simeasren.h2_techno_eco.LCOF_diff_all.calculate_all_LCOF_diff


Module Contents
---------------

.. py:function:: calculate_all_LCOF_diff(data_sim_meas, location_name, H2_end_user_min_load, solver_name, technoeco_file_name='Techno_eco_data_NH3')

   Calculate the difference in Levelized Cost of Fuel (LCOF) between
   measured and simulated data for a given location.

   This function performs a techno-economic analysis by comparing the
   measured energy production profile with multiple simulated profiles
   for the specified location. For each dataset, it computes the LCOF
   using the `solve_optiplant` optimization model, stores detailed
   results and flow data as CSV files, and calculates the relative
   difference in LCOF between measured and simulated cases.

   :param data_sim_meas: DataFrame containing both simulated and measured time-series data
                         for one or more locations. Each column name should include the
                         location name, and the measured data column should contain "PV-MEAS".
   :type data_sim_meas: pandas.DataFrame
   :param location_name: Name of the location to analyze (used to filter columns in
                         `data_sim_meas`).
   :type location_name: str
   :param H2_end_user_min_load: Minimum hydrogen end-user load (fraction of nominal load)
                                to be considered in the techno-economic model.
   :type H2_end_user_min_load: float
   :param solver_name: Name of the optimization solver to use (e.g., "PULP_CBC_CMD",
                       "GUROBI_CMD", "CPLEX_CMD").
   :type solver_name: str
   :param technoeco_file_name: Base filename (without extension) of the techno-economic data CSV file.
                               Defaults to "Techno_eco_data_NH3".
   :type technoeco_file_name: str, optional

   :returns: A list of dictionaries, each containing:

             - "Location" (str): Name of the analyzed location.
             - "Tool" (str): Identifier of the simulation tool or dataset.
             - "LCOF Difference (%)" (float): Relative difference in LCOF between
               simulated and measured data.
   :rtype: list of dict

   :raises FileNotFoundError: If the specified techno-economic CSV file does not exist.
   :raises ValueError: If no measured data column (containing "PV-MEAS") is found for the
       given location.

   .. rubric:: Notes

   The function assumes that the `solve_optiplant()` function is available
   in the current environment and returns:
   (LCOF_value, technoeco_results_df, flow_results_df).

   Intermediate results (system costs and hourly flow profiles) are saved
   automatically in the folders `System size and costs` and `Hourly profiles`

   .. rubric:: Examples

   Import and run the function using a CSV with simulated and measured PV data:

       >>> from simeasren import calculate_all_LCOF_diff, prepare_pv_data_for_plots
       >>> data_sim_meas, _, _ = prepare_pv_data_for_plots("Utrecht", "2017")
       >>> results = calculate_all_LCOF_diff(
       ...     data_sim_meas=data_sim_meas,
       ...     location_name="Utrecht",
       ...     H2_end_user_min_load=0.3,
       ...     solver_name="GUROBI_CMD",
       ...     technoeco_file_name="Techno_eco_data_NH3"
       ... )
       >>> results[0]
       {'Location': 'Utrecht', 'Tool': 'PG2-SARAH2', 'LCOF Difference (%)': -6.3}


