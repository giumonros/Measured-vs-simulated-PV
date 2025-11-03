from pathlib import Path
import pandas as pd

def load_pv_setup_from_meas_file(location_name: str) -> dict:
    """
    Load PV plant setup parameters from the measured data Excel file (in data/measured_PV)

    This function reads the `"PV_plant_setup"` sheet from the measured PV data Excel
    file for a given location and returns the contents as a dictionary, with the
    Excel sheet's `"Parameter"` column as keys and the `"Value"` column as values.

    Parameters
    ----------
    location_name : str
        Name of the location/site corresponding to the Excel file (without extension),
        e.g., `"Turin"`. The function expects the file to exist in:
        ```
        data/measured_PV/{location_name}.xlsx
        ```

    Returns
    -------
    dict
        Dictionary containing PV plant setup parameters. Keys correspond to parameter
        names (from the `"Parameter"` column in Excel), and values are the corresponding
        setup values.

    Raises
    ------
    FileNotFoundError
        If the measured PV Excel file for the specified location does not exist.

    Notes
    -----
    - The Excel sheet must be named `"PV_plant_setup"` with columns `"Parameter"` and `"Value"`.
    - Typical use includes retrieving metadata such as plant capacity, inverter specs,
      orientation, or other site-specific configuration values for plotting or modeling.

    Examples
    --------
    >>> from simeasren import load_pv_setup_from_meas_file
    >>> parameters = load_pv_setup_from_meas_file("Almeria")
    >>> parameters["System loss"]
    9.75
    >>> parameters["PV technology"]
    'crystSi'
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
