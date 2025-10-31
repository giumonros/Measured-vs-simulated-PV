import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

def calculate_error_metrics(
    data_sim_meas,
    location_name,
    plot_palette=None,
    exclude_non_palette=True,
):
    """
    Calculate PV simulation error metrics relative to measured data.

    This function computes key statistical error metrics — Mean Difference, 
    Mean Absolute Error (MAE), and Root Mean Square Error (RMSE) — for each 
    simulation tool relative to measured PV data for a specific location.
    The outputs are structured as lists of dictionaries, ready for plotting 
    or further analysis.

    Parameters
    ----------
    data_sim_meas : pandas.DataFrame
        DataFrame containing measured and simulated PV data for a given location.
        Columns should include one `"PV-MEAS"` column for measured data and 
        one or more simulation tool columns (e.g., `"Turin PV-SIM1"`).
    location_name : str
        Name of the location (e.g., `"Turin"`) used to filter relevant columns 
        and label outputs.
    plot_palette : dict, optional
        Dictionary mapping simulation tool names to colors or labels for plotting.
        If None, no filtering is applied based on the palette.
    exclude_non_palette : bool, optional (default=True)
        If True, only simulation tools listed in `plot_palette` are included.
        If False, all simulation columns are processed regardless of the palette.

    Returns
    -------
    tuple of lists
        A tuple `(mean_diff_results, mae_results, rmse_results)` where each element 
        is a list of dictionaries with the following structure:
        - `"Location"` : str — name of the location
        - `"Tool"` : str — simulation tool name
        - `"Mean Difference (%)"` / `"MAE (%)"` / `"RMSE (%)"` : float — computed metric

    Raises
    ------
    None
        Missing `'PV-MEAS'` column is handled by returning empty lists.
        Columns with insufficient data (empty after NaN removal) are skipped.

    Notes
    -----
    - Metrics are calculated in **percent (%)** by multiplying the raw value by 100.
    - The function aligns indices of simulated and measured data to handle missing values.
    - Tool names are extracted from column names by splitting at whitespace and
      using the second part if available.

    Examples
    --------
    >>> from simeasren import calculate_error_metrics
    >>> df = pd.read_csv("Turin_meas_sim.csv")
    >>> mean_diff, mae, rmse = calculate_error_metrics(
    ...     data_sim_meas=df,
    ...     location_name="Turin"
    ... )
    >>> mean_diff[0]
    {'Location': 'Turin', 'Tool': 'PV-SIM1', 'Mean Difference (%)': 2.34}
    >>> mae[0]
    {'Location': 'Turin', 'Tool': 'PV-SIM1', 'MAE (%)': 3.12}
    >>> rmse[0]
    {'Location': 'Turin', 'Tool': 'PV-SIM1', 'RMSE (%)': 4.05}
    """

    mean_diff_results = []
    mae_results = []
    rmse_results = []

    # Filter columns for the given location
    loc_data = data_sim_meas[
        [col for col in data_sim_meas.columns if col.startswith(location_name)]
    ]

    # Identify measured column
    meas_column = next((col for col in loc_data.columns if "PV-MEAS" in col), None)
    if meas_column is None:
        print(f"'PV-MEAS' column missing for {location_name}")
        return mean_diff_results, mae_results, rmse_results

    valid_columns = loc_data.columns.tolist()

    for sim_col in valid_columns:
        # Skip measured column
        if sim_col == meas_column:
            continue

        # Conditionally exclude non-palette tools
        if (
            exclude_non_palette
            and plot_palette is not None
            and not any(tool in sim_col for tool in plot_palette.keys())
        ):
            continue

        # Drop NaNs and align
        simulated_data = loc_data[sim_col].dropna()
        measured_data = loc_data[meas_column].dropna()

        common_index = simulated_data.index.intersection(measured_data.index)
        simulated_data = simulated_data.loc[common_index]
        measured_data = measured_data.loc[common_index]

        if simulated_data.empty or measured_data.empty:
            continue

        # Calculate metrics (%)
        mean_diff = (simulated_data.mean() - measured_data.mean()) * 100
        mae = mean_absolute_error(measured_data, simulated_data) * 100
        rmse = np.sqrt(mean_squared_error(measured_data, simulated_data)) * 100

        # Try to extract tool name
        parts = sim_col.split()
        tool_name = parts[1] if len(parts) > 1 else sim_col

        mean_diff_results.append({
            "Location": location_name,
            "Tool": tool_name,
            "Mean Difference (%)": mean_diff,
        })
        mae_results.append({
            "Location": location_name,
            "Tool": tool_name,
            "MAE (%)": mae,
        })
        rmse_results.append({
            "Location": location_name,
            "Tool": tool_name,
            "RMSE (%)": rmse,
        })

    return mean_diff_results, mae_results, rmse_results
