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
    Download simulated PV power output data from Renewables.ninja for a specified location.

    This function queries the Renewables.ninja API for multiple datasets (MERRA2 and SARAH)
    and generates hourly PV electricity output for the given PV system parameters.
    The resulting data are saved as CSV files in the project directory and
    returned as a dictionary for further analysis.

    Parameters
    ----------
    location_name : str
        Name of the location/site (e.g., "Almeria") used for file naming and labeling downloaded data.
    pv_parameters : dict
        Dictionary containing PV system configuration parameters.

        **Expected keys:**
            - "Latitude" : float — geographic latitude  
            - "Longitude" : float — geographic longitude  
            - "Tilt" : float — tilt angle of PV modules (degrees)  
            - "Azimuth" : float — azimuth of PV modules (degrees)  
            - "Max capacity simulation" : float — peak PV power in kW  
            - "System loss" : float — system losses in %  
            - "Start year" : int — first year of simulation  
            - "End year" : int — last year of simulation  
            - "Fixed" : int — 1 if fixed tilt, 0 if tracking system  
            - "Tracking" : int — tracking type if not fixed (0 = none, 1 = single-axis, etc.)  
    rn_token : str
        API token for Renewables.ninja.

    Returns
    -------
    dict
        Dictionary of Renewables.ninja simulation outputs.

        **Keys**  
            str — unique identifiers in the format  
            ``"{location_name}{year} RN-{dataset}"``  
            Example: ``"Almeria2020 RN-MERRA2"``  

        **Values**  
            numpy.ndarray — hourly PV electricity generation in kW.

    Raises
    ------
    requests.exceptions.RequestException
        If a network request to Renewables.ninja fails.
    FileNotFoundError
        If the output directory cannot be created or written to.
    ValueError
        If the CSV response from Renewables.ninja cannot be parsed correctly.

    Notes
    -----
    - Output CSV files are saved to:

        results/{location_name}/simulated_PV/Renewables_ninja/

    - The function handles API rate limiting (HTTP 429) by pausing before retrying.  
    - Power output is returned as a NumPy array in kW.  
    - To set up a Renewables.ninja API token:
        1. Visit [Renewables.ninja registration page](https://www.renewables.ninja/register) and create an account  
        2. Go to your [profile page](https://www.renewables.ninja/profile) to generate your API token  
        3. Copy your API token for use in this function  

    Examples
    --------
    >>> from simeasren import download_rn_data
    >>> pv_params = {
    ...     "Latitude": 37.0,
    ...     "Longitude": -2.5,
    ...     "Tilt": 30,
    ...     "Azimuth": 180,
    ...     "Max capacity simulation": 1000,
    ...     "System loss": 14,
    ...     "Start year": 2020,
    ...     "End year": 2020,
    ...     "Fixed": 1,
    ...     "Tracking": 0
    ... }
    >>> rn_token = "YOUR_RN_API_TOKEN"
    >>> rn_data = download_rn_data("Almeria", pv_params, rn_token)
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
