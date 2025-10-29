import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

def calculate_error_metrics(
    data_sim_meas,
    location_name,
    plot_palette,
):
    """
    Calculate Mean Difference, MAE, and RMSE for each simulation tool
    relative to measured PV data.

    Parameters
    ----------
    data_sim_meas : pd.DataFrame
        DataFrame containing measured and simulated PV data for one location.
    location_name : str
        Name of the location (for labeling outputs).
    meas_column : str
        Name of the measured PV data column (e.g. 'Location PV-MEAS').
    plot_palette : dict
        Dictionary of simulation tools and their associated colors/names,
        typically style_config.PLOT_PALETTE.

    Returns
    -------
    tuple
        mean_diff_results, mae_results, rmse_results
        Each is a list of dictionaries, ready for the plot_error_metrics() function.
    """

    mean_diff_results = []
    mae_results = []
    rmse_results = []

    loc_data = data_sim_meas[
        [col for col in data_sim_meas.columns if col.startswith(location_name)]
    ]

    # Identify 'PV-MEAS' column as the real (measured) data
    meas_column = next((col for col in loc_data.columns if "PV-MEAS" in col), None)
    if meas_column is None:
        print(f"'PV-MEAS' column missing for {location_name}")

    valid_columns = loc_data.columns.tolist()

    for sim_col in valid_columns:
        # Skip the measured column itself
        if sim_col == meas_column:
            continue

        # Include only simulation tools defined in the palette
        if not any(tool in sim_col for tool in plot_palette.keys()):
            continue

        # Drop NaNs
        simulated_data = loc_data[sim_col].dropna()
        measured_data = loc_data[meas_column].dropna()

        # Ensure same length and alignment
        common_index = simulated_data.index.intersection(measured_data.index)
        simulated_data = simulated_data.loc[common_index]
        measured_data = measured_data.loc[common_index]

        if simulated_data.empty or measured_data.empty:
            continue

        # Calculate metrics (%)
        mean_diff = (simulated_data.mean() - measured_data.mean()) * 100
        mae = mean_absolute_error(measured_data, simulated_data) * 100
        rmse = np.sqrt(mean_squared_error(measured_data, simulated_data)) * 100

        tool_name = sim_col.split()[1]

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
