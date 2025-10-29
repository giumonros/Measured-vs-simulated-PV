from pathlib import Path
import pandas as pd

def load_pv_setup_from_meas_file(location_name: str) -> dict:
    """
    Load PV plant setup data from the Excel file and return as a dictionary of parameters.

    Parameters
    ----------
    location_name : str
        Name of the location (without extension, e.g., "Turin").

    Returns
    -------
    dict
        Dictionary of parameters loaded from the Excel file.
    """
    # Get package root (two levels up from this file)
    package_root = Path(__file__).resolve().parent.parent
    measured_dir = package_root / "data" / "measured_PV"

    # Build full path to the Excel file
    file_path = measured_dir / f"{location_name}.xlsx"

    if not file_path.exists():
        raise FileNotFoundError(f"Measured PV file not found: {file_path}")

    # Read Excel sheet
    df_setup = pd.read_excel(file_path, sheet_name="PV_plant_setup", index_col="Parameter")

    # Convert to dictionary
    parameters = df_setup["Value"].to_dict()

    return parameters
