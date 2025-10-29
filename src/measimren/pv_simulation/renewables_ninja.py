import os
import io
import time
import requests
import pandas as pd


def download_rn_data(
    location_name: str,
    pv_parameters, 
    rn_token: str
):
    """
    Download simulated PV data from Renewables.ninja for a given location and return as dict.

    Parameters
    ----------
    location_name : str
        Name of the location (used in output filenames)
    pv_parameters : dict
        Dictionary of PV system parameters (Latitude, Longitude, etc.)
    rn_token : str
        Renewables Ninja API token

    Returns
    -------
    productions : dict
        Dictionary with keys as identifiers (e.g. "Almeria_2020_RN-MERRA2")
        and values as NumPy arrays of electricity generation.
    """
    # -------------------- Create output directory --------------------
    output_dir_simulated_pv = os.path.join("results", location_name, "simulated_PV/Renewables_ninja")
    os.makedirs(output_dir_simulated_pv, exist_ok=True)

    rn_session = requests.Session()
    rn_session.headers = {"Authorization": f"Token {rn_token}"}
    rn_databases = ["merra2", "sarah"]
    productions = {}

    def generate_date_ranges(start_year, end_year):
        return [(f"{year}-01-01", f"{year}-12-31") for year in range(start_year, end_year + 1)]

    start_year = int(pv_parameters["Start year"])
    end_year = int(pv_parameters["End year"])

    for year in range(start_year, end_year + 1):
        for db in rn_databases:
            for date_from, date_to in generate_date_ranges(year, year):
                identifier = f"{location_name}{year} RN-{db.upper()}"
                args = {
                    "lat": pv_parameters["Latitude"],
                    "lon": pv_parameters["Longitude"],
                    "date_from": date_from,
                    "date_to": date_to,
                    "dataset": db,
                    "capacity": pv_parameters["Max capacity simulation"],
                    "system_loss": pv_parameters["System loss"] / 100,
                    "tracking": 0 if pv_parameters["Fixed"] == 1 else pv_parameters["Tracking"],
                    "tilt": pv_parameters["Tilt"],
                    "azim": pv_parameters["Azimuth"],
                    "format": "csv",
                }

                success = False
                while not success:
                    response = rn_session.get("https://www.renewables.ninja/api/data/pv", params=args)
                    if response.status_code == 200:
                        data = pd.read_csv(io.StringIO(response.text), skiprows=3)

                        # Store numeric data
                        productions[identifier] = data["electricity"].astype(float).values

                        # Save CSV
                        file_path = os.path.join(output_dir_simulated_pv, f"{identifier}.csv")
                        data.to_csv(file_path, index=False)
                        print(f" Saved Renewables Ninja data to: {file_path}")

                        success = True

                    elif response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 3600))
                        print(f"Rate limit hit for Renewables Ninja. Pausing for {retry_after} seconds...")
                        time.sleep(retry_after)
                    else:
                        print(f" Data not available from Renewables Ninja for {identifier}")
                        success = True  # Exit loop to avoid infinite retry

    return productions
