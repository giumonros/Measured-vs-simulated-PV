import os
import pandas as pd

def load_pv_setup(location_name: str, measured_dir="Measured PV data"):
    """
    Load PV plant setup data from the Excel file and return as a dictionary of parameters.
    """
    file_path = os.path.join(measured_dir, f"{location_name}.xlsx")
    df_setup = pd.read_excel(file_path, sheet_name="PV_plant_setup", index_col="Parameter")
    parameters = df_setup["Value"].to_dict()  # convert to standard dictionary
    return parameters
