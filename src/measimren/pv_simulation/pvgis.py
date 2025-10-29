import os
import io
import pandas as pd
import requests


def download_pvgis_data(
    location_name: str,
    pv_parameters
):
    """
    Download simulated PV data from PVGIS for a given location and return as dict.

    Parameters
    ----------
    location_name : str
        Name of the location (used for file naming)
    pv_parameters : dict
        Dictionary of PV system parameters (Latitude, Longitude, Tilt, etc.)

    Returns
    -------
    productions : dict
        Dictionary where keys are identifiers (e.g., 'Almeria_2020_PG3-SARAH3')
        and values are NumPy arrays of hourly PV power output in kW.
    """
    # -------------------- Create output directory --------------------
    output_dir_simulated_pv = os.path.join("results", location_name, "simulated_PV/PVGIS")
    print(output_dir_simulated_pv)
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
