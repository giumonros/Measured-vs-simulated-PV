import os
import io
import pandas as pd
import requests


def download_pvgis_data(
    location_name: str,
    pv_parameters
):
    """
    Download simulated PV power output data from PVGIS for a specified location.

    This function queries the PVGIS API for multiple databases and versions to
    generate hourly PV power output for the given PV system parameters.
    The resulting data are saved as CSV files in the project directory and
    returned as a dictionary for further analysis.

    Parameters
    ----------
    location_name : str
        Name of the location/site (e.g., "Almeria") used for file naming and
        labeling downloaded data.
    pv_parameters : dict
        Dictionary containing PV system configuration parameters.

        **Expected keys:**
            - "Latitude" : float — geographic latitude  
            - "Longitude" : float — geographic longitude  
            - "Tilt" : float — tilt angle of PV modules (degrees)  
            - "Azimuth" : float — azimuth of PV modules (degrees)  
            - "Max capacity simulation" : float — peak PV power in kW  
            - "System loss" : float — system losses in %  
            - "PV technology" : str — PV technology type (e.g., "crystalline silicon")  
            - "Building/free" : str — mounting type ("building" or "free")  
            - "Start year" : int — first year of simulation  
            - "End year" : int — last year of simulation  

    Returns
    -------
    dict
        Dictionary of PVGIS simulation outputs.

        **Keys**
            str — unique identifiers in the format  
            ``"{location_name}{year} PG{version}-{database}"``  
            Example: ``"Almeria2020 PG3-SARAH3"``  

        **Values**
            numpy.ndarray — hourly PV power output in kW.

    Raises
    ------
    requests.exceptions.RequestException
        If a network request to PVGIS fails.
    FileNotFoundError
        If the output directory cannot be created or written to.
    ValueError
        If PVGIS CSV data cannot be parsed correctly.

    Notes
    -----
    - Output CSV files are saved to:

        results/{location_name}/simulated_PV/PVGIS/

    - PVGIS API versions used:
        - v5_2 : "PVGIS-SARAH", "PVGIS-SARAH2", "PVGIS-ERA5"
        - v5_3 : "PVGIS-SARAH3", "PVGIS-ERA5"
    - Power output in the CSV is converted from W → kW and stored in the "P_kW" column.
    - The function prints status messages for successful downloads and missing data.

    Examples
    --------
    >>> from simeasren import download_pvgis_data
    >>> pv_params = {
    ...     "Latitude": 37.0,
    ...     "Longitude": -2.5,
    ...     "Tilt": 30,
    ...     "Azimuth": 180,
    ...     "Max capacity simulation": 1000,
    ...     "System loss": 14,
    ...     "PV technology": "crystalline silicon",
    ...     "Building/free": "free",
    ...     "Start year": 2020,
    ...     "End year": 2020
    ... }
    >>> productions = download_pvgis_data("Almeria", pv_params)
    >>> list(productions.keys())
    ['Almeria2020 PG2-SARAH', 'Almeria2020 PG2-SARAH2', 'Almeria2020 PG2-ERA5', 'Almeria2020 PG3-SARAH3', 'Almeria2020 PG3-ERA5']
    >>> productions['Almeria2020 PG3-SARAH3'].shape
    (8760,)
    """
    
    # -------------------- Create output directory --------------------
    output_dir_simulated_pv = os.path.join("results", location_name, "simulated_PV/PVGIS")
    os.makedirs(output_dir_simulated_pv, exist_ok=True)

    # PVGIS API setup
    pvgis_versions = ["v5_2", "v5_3"]
    pvgis_databases_by_version = {
        "v5_2": ["PVGIS-SARAH", "PVGIS-SARAH2", "PVGIS-ERA5"],
        "v5_3": ["PVGIS-SARAH3", "PVGIS-ERA5"],
    }
    pvgis_session = requests.Session()
    productions = {}

    start_year = int(pv_parameters["Start year"])
    end_year = int(pv_parameters["End year"])

    # Helper function to create PVGIS API URL
    def create_pvgis_url(version, db, year):
        return (
            f"https://re.jrc.ec.europa.eu/api/{version}/seriescalc?"
            f"lat={pv_parameters['Latitude']}&lon={pv_parameters['Longitude']}"
            f"&aspect={pv_parameters['Azimuth'] - 180}&angle={pv_parameters['Tilt']}"
            f"&pvcalculation=1&peakpower={int(pv_parameters['Max capacity simulation'])}.0"
            f"&loss={pv_parameters['System loss']}&pvtechchoice={pv_parameters['PV technology']}"
            f"&startyear={year}&endyear={year}&outputformat=csv"
            f"&mountingplace={pv_parameters['Building/free']}&browser=1&raddatabase={db}"
        )

    # Main data download loop
    for year in range(start_year, end_year + 1):
        for version in pvgis_versions:
            for db in pvgis_databases_by_version[version]:
                version_number = "2" if version == "v5_2" else "3"
                db_name = db.split("-")[1]
                identifier = f"{location_name}{year} PG{version_number}-{db_name}"
                api_url = create_pvgis_url(version, db, year)

                response = pvgis_session.get(api_url)
                if response.status_code == 200:
                    # Read PVGIS CSV data, skipping metadata rows and trimming footer
                    data = pd.read_csv(io.StringIO(response.text), skiprows=10)
                    data = data[:-7]  # Remove trailing metadata rows
                    data["P_kW"] = data["P"].astype(float) / 1000  # convert W → kW
                    productions[identifier] = data["P_kW"].values

                    # Save to CSV
                    
                    file_path = os.path.join(output_dir_simulated_pv, f"{identifier}.csv")
                    data.to_csv(file_path, index=False)
                    print(f"Saved PVGIS data to: {file_path}")

                else:
                    print(f"Data not available from PVGIS for {identifier}")

    return productions
