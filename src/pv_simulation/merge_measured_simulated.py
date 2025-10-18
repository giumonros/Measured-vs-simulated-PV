import os
import pandas as pd
# ---------------------------- Merge & Save -----------------------------

def merge_with_measured(location_name: str, *simulated_sources, measured_dir="data/measured_PV", output_dir="data"):
    """
    Merge measured PV data with any number of simulation sources and save CSV.
    Each simulated_source should be a dictionary {identifier: hourly_values}.
    """
    file_path = os.path.join(measured_dir, f"{location_name}.xlsx")
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

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{location_name}_meas_sim.csv")
    output_df.to_csv(out_path, index=False)

    print(f"Simulations completed and data merged for {location_name}. CSV file saved in the '{output_dir}' folder")
    return output_df
