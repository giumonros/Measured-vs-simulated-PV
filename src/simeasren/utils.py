import os
import pandas as pd
from pathlib import Path

# ---------------------------- Merge simulated with measured data in one file & Save -----------------------------

def merge_sim_with_measured(location_name: str, *simulated_sources, output_dir="results"):
    """
    Merge measured PV data with multiple simulation sources and save as a CSV file.

    This function reads measured PV data from an Excel file, combines it with any number
    of simulated PV datasets provided as dictionaries, and saves the merged dataset
    for further analysis or plotting. Each simulation source should be a dictionary
    where keys are identifiers and values are hourly PV power arrays.

    Parameters
    ----------
    location_name : str
        Name of the location/site (e.g., `"Almeria"`) used for file paths and labeling.
    *simulated_sources : dict
        Variable number of dictionaries containing simulated PV outputs.
        Each dictionary should have:
        - Keys : str — unique identifiers (e.g., `"Almeria2023 PG2-SARAH"`)
        - Values : numpy.ndarray — hourly PV power output in kW.
    output_dir : str, optional
        Root directory where the merged CSV will be saved (default is `"results"`).

    Returns
    -------
    None
        The function writes a CSV file to:
        ```
        {output_dir}/{location_name}/simulated_PV/{location_name}_meas_sim.csv
        ```
        and prints a completion message.

    Raises
    ------
    FileNotFoundError
        If the measured PV Excel file cannot be found.

    Notes
    -----
    - Only the first 8760 rows are kept to represent one year of hourly data.
    - Measured data is read from Excel sheets named `{location_name}{year}`.
    - Merged CSV columns include all simulation identifiers and the measured PV data
      labeled as `{location_name}{year} PV-MEAS`.

    Examples
    --------
    >>> from simesren import load_pv_setup_from_meas_file, download_pvgis_data, download_rn_data, merge_sim_with_measured
    >>> pv_parameters = load_pv_setup_from_meas_file("Almeria")
    >>> pvgis_data = download_pvgis_data("Almeria", pv_parameters)
    >>> rn_data = download_rn_data(location, pv_parameters, rn_token=renewablesninja_token)
    >>> merge_sim_with_measured(location, pvgis_data, rn_data)

    Simulations completed and merged with measured data for Almeria. CSV file saved in the 'results' folder
    """
    # -------------------- Create output directory --------------------
    output_dir_sim_and_meas = os.path.join(output_dir, location_name, "simulated_PV")
    os.makedirs(output_dir_sim_and_meas, exist_ok=True)

    # Get package root (two levels up from this file)
    package_root = Path(__file__).resolve().parent
    measured_dir = package_root / "data" / "measured_PV"

    # Build full path to the Excel file
    file_path = measured_dir / f"{location_name}.xlsx"

    if not file_path.exists():
        raise FileNotFoundError(f"Measured PV file not found: {file_path}")
    
    df_setup = pd.read_excel(file_path, sheet_name="PV_plant_setup", index_col="Parameter")

    parameters = df_setup["Value"]

    start_year = int(parameters["Start year"])
    end_year = int(parameters["End year"])

    productions = {}
    
    # Merge all simulated sources
    for source in simulated_sources:
        productions.update(source)

    # Merge measured data
    for year in range(start_year, end_year + 1):
        sheet_measured = f"{location_name}{year}"
        df_measured = pd.read_excel(file_path, sheet_name=sheet_measured)
        productions[f"{location_name}{year} PV-MEAS"] = df_measured["Normalized PV power corrected"].values

    output_df = pd.DataFrame({k: pd.Series(v) for k, v in productions.items()})
    output_df = output_df.iloc[:8760]  # One year hourly

    out_path = os.path.join(output_dir_sim_and_meas, f"{location_name}_meas_sim.csv")
    output_df.to_csv(out_path, index=False)

    print(f"Simulations completed and merged with measured data for {location_name}. CSV file saved in the '{output_dir}' folder")
    return