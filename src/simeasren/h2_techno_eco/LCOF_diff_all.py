import os
import pandas as pd
from pathlib import Path
from ..h2_techno_eco.OptiPlant import solve_optiplant

def calculate_all_LCOF_diff(
    data_sim_meas,
    location_name,
    H2_end_user_min_load,
    solver_name,
    technoeco_file_name = "Techno_eco_data_NH3"
):
    """
    Calculate the difference in Levelized Cost of Fuel (LCOF) between 
    measured and simulated data for a given location.

    This function performs a techno-economic analysis by comparing the 
    measured energy production profile with multiple simulated profiles 
    for the specified location. For each dataset, it computes the LCOF 
    using the `solve_optiplant` optimization model, stores detailed 
    results and flow data as CSV files, and calculates the relative 
    difference in LCOF between measured and simulated cases.

    Parameters
    ----------
    data_sim_meas : pandas.DataFrame
        DataFrame containing both simulated and measured time-series data 
        for one or more locations. Each column name should include the 
        location name, and the measured data column should contain "PV-MEAS".
    location_name : str
        Name of the location to analyze (used to filter columns in 
        `data_sim_meas`).
    H2_end_user_min_load : float
        Minimum hydrogen end-user load (fraction of nominal load) 
        to be considered in the techno-economic model.
    solver_name : str
        Name of the optimization solver to use (e.g., "PULP_CBC_CMD", 
        "GUROBI_CMD", "CPLEX_CMD").
    technoeco_file_name : str, optional
        Base filename (without extension) of the techno-economic data CSV file.
        Defaults to "Techno_eco_data_NH3".

    Returns
    -------
    list of dict
        A list of dictionaries, each containing:

        - "Location" (str): Name of the analyzed location.
        - "Tool" (str): Identifier of the simulation tool or dataset.
        - "LCOF Difference (%)" (float): Relative difference in LCOF between 
          simulated and measured data.

    Raises
    ------
    FileNotFoundError
        If the specified techno-economic CSV file does not exist.
    ValueError
        If no measured data column (containing "PV-MEAS") is found for the 
        given location.

    Notes
    -----
    The function assumes that the `solve_optiplant()` function is available 
    in the current environment and returns:
    (LCOF_value, technoeco_results_df, flow_results_df).

    Intermediate results (system costs and hourly flow profiles) are saved 
    automatically in the folders `System size and costs` and `Hourly profiles`

    Examples
    --------
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
    """

    # -------------------- Create output directories --------------------
    output_dir_technoeco = os.path.join("results", location_name, "Techno-eco assessments results")
    output_dir_technoeco_syst = os.path.join(output_dir_technoeco, f"End-user flex[{H2_end_user_min_load}-1]", "System size and costs")
    output_dir_flows = os.path.join(output_dir_technoeco, f"End-user flex[{H2_end_user_min_load}-1]", "Hourly profiles")
    os.makedirs(output_dir_technoeco_syst, exist_ok=True)
    os.makedirs(output_dir_flows, exist_ok=True)

    # Get package root (two levels up from this file)
    package_root = Path(__file__).resolve().parent.parent
    technoeco_dir = package_root / "data" / "techno_economic_assessment"

    # Build full path to the Excel file
    file_path_technoeco  = technoeco_dir / f"{technoeco_file_name}.csv"

    if not file_path_technoeco.exists():
        raise FileNotFoundError(f"Techno-economic file not found: {file_path_technoeco}")

    data_units = pd.read_csv(file_path_technoeco)

    LCOF_diff_results = []

    # Filter columns for the current location
    loc_data = data_sim_meas[[col for col in data_sim_meas.columns if location_name in col]]

    # Identify 'PV-MEAS' column as the measured data
    meas_column = next((col for col in loc_data.columns if "PV-MEAS" in col), None)
    if meas_column is None:
        print(f"No measured data for {location_name}")
        return

    # Perform the techno-economic assessment with the measured data
    measured_profile_LCOF = loc_data[[meas_column]].dropna()
    LCOF_meas, df_results_meas, df_flows_meas = solve_optiplant(
        data_units, measured_profile_LCOF, H2_end_user_min_load, solver_name
    )

    # Save measured data results
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
        if sim_column != meas_column:
            simulated_profile_LCOF = loc_data[[sim_column]].dropna()
            LCOF_sim, df_results_sim, df_flows_sim = solve_optiplant(
                data_units, simulated_profile_LCOF, H2_end_user_min_load, solver_name
            )

            # Save simulated data results
            output_file_tech_sim = f"{sim_column}.csv"
            df_results_sim.to_csv(
                os.path.join(output_dir_technoeco_syst, output_file_tech_sim),
                index=False,
            )
            output_file_flow_sim = f"{sim_column}.csv"
            df_flows_sim.to_csv(
                os.path.join(output_dir_flows, output_file_flow_sim), index=False
            )

            # Calculate LCOF difference
            LCOF_diff = (LCOF_sim - LCOF_meas) / LCOF_meas * 100
            LCOF_diff_results.append(
                {
                    "Location": location_name,
                    "Tool": sim_column.split()[1],
                    "LCOF Difference (%)": LCOF_diff,
                }
            )

    return LCOF_diff_results
