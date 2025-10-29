import os
import re
import pandas as pd
import numpy as np
from pathlib import Path

def convert_comma_to_dot(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns with commas as decimals to numeric floats."""
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].str.replace(",", ".", regex=False)
            try:
                df[column] = df[column].astype(float)
            except ValueError:
                pass
    return df


def extract_year_selected(dataframe: pd.DataFrame, column_pattern=r"([A-Za-z]+[0-9]{4})") -> str:
    """Extract year tag (e.g., Location2020) from dataframe column names."""
    for col in dataframe.columns:
        match = re.match(column_pattern, col)
        if match:
            return match.group(1)
    raise ValueError(
        "Column entry for cloudy and clear sky data should be written as 'LocationYear PV-MEAS_high_resolution'."
    )


def prepare_pv_data_for_plots(location_name: str, year: str):
    """
    Load and preprocess all data required for generating PV performance plots.

    Parameters
    ----------
    location_name : str
        Name of the site/location (e.g. 'Almeria')
    year : str
        Specific year to filter, or 'All years' to include all

    Returns
    -------
    data_sim_meas : pd.DataFrame
        Hourly simulated and measured PV data
    clear_sky_df : pd.DataFrame
        Processed clear-sky day data merged with simulation data
    cloudy_sky_df : pd.DataFrame
        Processed cloudy-sky day data merged with simulation data
    """

    # -------------------- Load data files --------------------

    # Get package root (two levels up from this file)
    package_root = Path(__file__).resolve().parent.parent
    measured_dir = package_root / "data" / "measured_PV"

    # Build full path to the Excel file
    file_path_pvdata  = measured_dir / f"{location_name}.xlsx"

    if not file_path_pvdata.exists():
        raise FileNotFoundError(f"Measured PV file not found: {file_path_pvdata}")
    
    file_path_sim_meas = os.path.join("results",location_name, "simulated_pv", f"{location_name}_meas_sim.csv")
    data_sim_meas = pd.read_csv(file_path_sim_meas)

    clear_sky_df = pd.read_excel(file_path_pvdata, sheet_name="Clear sky day")
    cloudy_sky_df = pd.read_excel(file_path_pvdata, sheet_name="Cloudy sky day")

    # -------------------- Preprocess measured PV data --------------------
    clear_sky_df = convert_comma_to_dot(clear_sky_df)
    cloudy_sky_df = convert_comma_to_dot(cloudy_sky_df)

    # -------------------- Preprocess simulated and measured PV data --------------------
    # Ensure all values are numeric
    data_sim_meas = data_sim_meas.apply(pd.to_numeric, errors="coerce")

    # Limit to 8760 rows (one year of hourly data)
    data_sim_meas = data_sim_meas.iloc[:8760, :]

    # -------------------- Merge with high-resolution clear/cloudy data --------------------
    def merge_with_highres(df, data_sim_meas):
        year_selected = extract_year_selected(df)
        data_sim_filtered = data_sim_meas[[col for col in data_sim_meas.columns if year_selected in col]]
        data_sim_filtered = data_sim_filtered.reset_index().rename(columns={"index": "Hour of the year"})
        data_sim_filtered["Hour of the year"] = range(1, len(data_sim_filtered) + 1)
        df = df.merge(data_sim_filtered, on="Hour of the year", how="left")
        df = df.iloc[:, 2:]  # Drop first two columns (timestamp info)
        return df

    clear_sky_df = merge_with_highres(clear_sky_df, data_sim_meas)
    cloudy_sky_df = merge_with_highres(cloudy_sky_df, data_sim_meas)

    # -------------------- Filter by year (if specified) --------------------
    columns_with_year = [col for col in data_sim_meas.columns if year in col]
    if columns_with_year:
        data_sim_meas = data_sim_meas[columns_with_year]
    else:
        print(f"No measured data for the year chosen")
        data_sim_meas = data_sim_meas.iloc[0:0]

    return (
        data_sim_meas,
        clear_sky_df,
        cloudy_sky_df
    )
