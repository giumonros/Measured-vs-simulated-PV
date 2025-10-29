import os
import pandas as pd
from pathlib import Path

# ---------------------------- Merge simulated with measured data in one file & Save -----------------------------

def merge_sim_with_measured(location_name: str, *simulated_sources, output_dir="results"):
    """
    Merge measured PV data with any number of simulation sources and save CSV.
    Each simulated_source should be a dictionary {identifier: hourly_values}.
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