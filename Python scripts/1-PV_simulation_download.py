import pandas as pd
import requests
import io
import time
import os
import sys

# ----------------------------------------------------------------------------------------------

# Define location name (same as the one in the folder "Measured PV data") and renewables.ninja token

location_name = sys.argv[1]
# location_name = "Almeria"  # This can be changed to any other location available in the Measured PV data folder
rn_token = sys.argv[5]  # Replace with your Renewable.ninja token
# ----------------------------------------------------------------------------------------------

# By default the script will download the PV power simulations for all databases and versions of PVGIS and Renewables Ninja
# You can modify the following part of the script to select specific databases and versions

# Specify the PVGIS versions and databases with a mapping
pvgis_versions = ["v5_2", "v5_3"]  # List of versions to use

# Map each version to its appropriate databases
pvgis_databases_by_version = {
    "v5_2": ["PVGIS-SARAH", "PVGIS-SARAH2", "PVGIS-ERA5"],
    "v5_3": ["PVGIS-SARAH3", "PVGIS-ERA5"],
}

rn_databases = ["merra2", "sarah"]

# ----------------------------------------------------------------------------------------------

file_path = os.path.join("Measured PV data", f"{location_name}.xlsx")

# Load the setup data
sheet_name = "PV_plant_setup"
df_setup = pd.read_excel(file_path, sheet_name=sheet_name, index_col="Parameter")
parameters = df_setup["Value"]

# Setup API sessions
pvgis_session = requests.Session()
rn_session = requests.Session()
rn_session.headers = {"Authorization": "Token " + rn_token}

# Dictionary to store production data
productions = {}


# Function to generate date ranges for each year
def generate_date_ranges(start_year, end_year):
    return [
        (f"{year}-01-01", f"{year}-12-31") for year in range(start_year, end_year + 1)
    ]


# Function to create URL for PVGIS API call, using specified version and database
def create_pvgis_url(version, db, year):
    return (
        f"https://re.jrc.ec.europa.eu/api/{version}/seriescalc?"
        f"lat={parameters['Latitude']}&lon={parameters['Longitude']}&aspect={parameters['Azimuth'] - 180}"
        f"&angle={parameters['Tilt']}&pvcalculation=1&peakpower={int(parameters['Max capacity simulation'])}.0"
        f"&loss={parameters['System loss']}&pvtechchoice={parameters['PV technology']}"
        f"&startyear={year}&endyear={year}&outputformat=csv"
        f"&mountingplace={parameters['Building/free']}&browser=1&raddatabase={db}"
    )


# Iterate through each year range and version
start_year = int(parameters["Start year"])
end_year = int(parameters["End year"])

# Retrieve and process data for each API, year range, and version
for year in range(start_year, end_year + 1):
    # Load measured data from the specified year
    sheet_measured = f"{location_name}{year}"
    df_measured = pd.read_excel(file_path, sheet_name=sheet_measured)
    measured_data = df_measured["Normalized PV power corrected"]
    productions[f"{location_name}_{year}_PV-MEAS"] = measured_data.values

    for version in pvgis_versions:
        for db in pvgis_databases_by_version[version]:
            # Customize the identifier to match the required format
            version_number = "2" if version == "v5_2" else "3"
            db_name = db.split("-")[1]  # Extract SARAH2, SARAH3, or ERA5
            identifier = f"{location_name}_{year}_PG{version_number}-{db_name}"

            api_url = create_pvgis_url(version, db, year)

            # Print the generated URL for debugging
            # print(f"Generated URL for version '{version}', database '{db}', year '{year}': {api_url}")

            response = pvgis_session.get(api_url)
            if response.status_code == 200:
                data = pd.read_csv(io.StringIO(response.text), skiprows=10)
                data = data[:-7]  # Adjusting based on API data format
                productions.setdefault(identifier, []).extend(
                    (data["P"].astype(float) / 1000).values
                )
            else:
                print(f"Data not available from PVGIS for {identifier}")
    for db in rn_databases:
        for date_from, date_to in generate_date_ranges(year, year):
            identifier = f"{location_name}_{year}_RN-{db.upper()}"
            args = {
                "lat": parameters["Latitude"],
                "lon": parameters["Longitude"],
                "date_from": date_from,
                "date_to": date_to,
                "dataset": db,
                "capacity": parameters["Max capacity simulation"],
                "system_loss": parameters["System loss"] / 100,
                "tracking": 0 if parameters["Fixed"] == 1 else parameters["Tracking"],
                "tilt": parameters["Tilt"],
                "azim": parameters["Azimuth"],
                "format": "csv",
            }
            response = rn_session.get(
                "https://www.renewables.ninja/api/data/pv", params=args
            )
            if response.status_code == 200:
                data = pd.read_csv(io.StringIO(response.text), skiprows=3)
                productions.setdefault(identifier, []).extend(
                    data["electricity"].astype(float).values
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 3600))
                print(
                    f"Rate limit hit for Renewables Ninja. Pausing for {retry_after} seconds."
                )
                time.sleep(retry_after)
            else:
                print(f"Data not available from Renewables Ninja for {identifier}")

# Convert all lists to pandas Series and create a DataFrame
for key, value in productions.items():
    productions[key] = pd.Series(value)
output_df = pd.DataFrame(productions)
output_df.index += 1  # Start first line at 1 instead of 0

# Updated database order to include PG2-SARAH
database_order = [
    "PV-MEAS",
    "RN-MERRA2",
    "RN-SARAH",
    "PG2-SARAH",
    "PG2-SARAH2",
    "PG2-ERA5",
    "PG3-SARAH3",
    "PG3-ERA5",
]


# Function to extract sort keys from column names
def sort_key(col):
    if col.endswith("PV-MEAS"):
        return (col[:-5], col[-4:], 0)  # 'MEAS' sorting as the first
    location_year, db = col.split("_", 1)  # Split at the first underscore
    year = location_year[-4:]  # Extract the year (last four characters)
    location = location_year[:-4]  # Extract location (all but last four characters)

    # Normalize database part for sorting
    db_key = (
        db.split("-")[1] if "-" in db else db
    )  # This extracts "SARAH", "SARAH2", etc.
    db_index = database_order.index(db) if db in database_order else len(database_order)

    return (location, year, db_index)


# Sort columns based on custom key
sorted_columns = sorted(output_df.columns, key=sort_key)

# Reorder DataFrame according to sorted columns
output_df = output_df[sorted_columns]

# Generate new column headers based on the sorted columns
new_columns = []
index_counter = 1

for col in sorted_columns:
    parts = col.split("_")
    if len(parts) > 2:  # Check if there are enough parts
        location = parts[0]
        year = parts[1]
        db = parts[2]
        db_name = (
            db.split("-")[1] if "-" in db else db
        )  # Extract database name correctly
        location_year = f"{location}{year}"
        new_columns.append(
            ("Solar fixed", location_year, db, "RPU_Solar_fixed", str(index_counter))
        )
    else:
        print(f"Unexpected column format: {col}")
    index_counter += 1

# Create a MultiIndex
multi_index = pd.MultiIndex.from_tuples(
    new_columns, names=["", "Locations", "Profile time series", "Subsets", "Index"]
)

# Assign this MultiIndex to the DataFrame
output_df.columns = multi_index

# Truncate the DataFrame to the first 8760 rows of data
output_df = output_df.iloc[:8760]

# Create directory for saving result file
output_dir = "Simulated and measured PV data"
os.makedirs(output_dir, exist_ok=True)

# Save the DataFrame to CSV
output_file = f"{location_name}_meas_sim.csv"
output_df.to_csv(os.path.join(output_dir, output_file))

print(
    f"Output {location_name} CSV file successfully generated in the '{output_dir}' folder !"
)
