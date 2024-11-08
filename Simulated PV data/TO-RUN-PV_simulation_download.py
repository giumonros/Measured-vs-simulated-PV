import pandas as pd
import requests
import io
import time
import os

# Define location name and file path
location_name = "Utrecht"  # This can be changed to any other location
rn_token = '357952a8676cd53bca5860e5ecafa180c8dc4879'  # Replace with your actual token
file_path = os.path.join("Measured PV data", location_name, "Meas_PV_power.xlsx")

# Load the setup data
sheet_name = "PV_plant_setup"
df_setup = pd.read_excel(file_path, sheet_name=sheet_name, index_col="Parameter")
parameters = df_setup['Value']

# Setup API sessions
pvgis_session = requests.Session()
rn_session = requests.Session()
rn_session.headers = {'Authorization': 'Token ' + rn_token}

# Databases for each API
pvgis_databases = ['PVGIS-SARAH2', 'PVGIS-ERA5']
rn_databases = ['merra2', 'sarah']

# Dictionary to store production data
productions = {}

# Function to generate date ranges for each year
def generate_date_ranges(start_year, end_year):
    return [(f"{year}-01-01", f"{year}-12-31") for year in range(start_year, end_year + 1)]

# Function to create URL for PVGIS API call
def create_pvgis_url(db, year):
    return (
        f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?"
        f"lat={parameters['Latitude']}&lon={parameters['Longitude']}&aspect={parameters['Azimuth'] - 180}"
        f"&angle={parameters['Tilt']}&pvcalculation=1&peakpower={int(parameters['Capacity Factor 1'])}.0"
        f"&loss={parameters['System loss']}&pvtechchoice={parameters['PV technology']}"
        f"&startyear={year}&endyear={year}&outputformat=csv"
        f"&mountingplace={parameters['Building/free']}&browser=1&raddatabase={db}"
    )

# Iterate through each year range
start_year = int(parameters['Start year'])
end_year = int(parameters['End year'])

# Retrieve and process data for each API and year range
for year in range(start_year, end_year + 1):
    # Load measured data from the specified year
    sheet_measured = f"{location_name}{year}"
    df_measured = pd.read_excel(file_path, sheet_name=sheet_measured)
    measured_data = df_measured['Normalized PV power corrected']
    productions[f"{location_name}_{year}_PV-MEAS"] = measured_data.values

    for db in pvgis_databases:
        api_url = create_pvgis_url(db, year)
        identifier = f"{location_name}_{year}_PG-{db.split('-')[1]}"
        response = pvgis_session.get(api_url)
        if response.status_code == 200:
            data = pd.read_csv(io.StringIO(response.text), skiprows=10)
            data = data[:-7]  # Adjusting based on API data format
            productions.setdefault(identifier, []).extend((data["P"].astype(float) / 1000).values)
        else:
            print(f"Data non available from PVGIS for {identifier}")

    for db in rn_databases:
        for date_from, date_to in generate_date_ranges(year, year):
            identifier = f"{location_name}_{year}_RN-{db.upper()}"
            args = {
                'lat': parameters['Latitude'],
                'lon': parameters['Longitude'],
                'date_from': date_from,
                'date_to': date_to,
                'dataset': db,
                'capacity': parameters['Capacity Factor 1'],
                'system_loss': parameters['System loss'] / 100,
                'tracking': 0 if parameters['Fixed'] == 1 else parameters['Tracking'],
                'tilt': parameters['Tilt'],
                'azim': parameters['Azimuth'],
                'format': 'csv'
            }
            response = rn_session.get("https://www.renewables.ninja/api/data/pv", params=args)
            if response.status_code == 200:
                data = pd.read_csv(io.StringIO(response.text), skiprows=3)
                productions.setdefault(identifier, []).extend(data['electricity'].astype(float).values)
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 3600))
                print(f"Rate limit hit for Renewables Ninja. Pausing for {retry_after} seconds.")
                time.sleep(retry_after)
            else:
                print(f"Data not available from Renewables Ninja for {identifier}")

# Convert all lists to pandas Series and create a DataFrame
for key, value in productions.items():
    productions[key] = pd.Series(value)
output_df = pd.DataFrame(productions)
output_df.index += 1  # Start first line at 1 instead of 0

# Desired order for databases
database_order = ['PV-MEAS', 'RN-MERRA2', 'RN-SARAH', 'PG-SARAH', 'PG-SARAH2', 'PG-ERA5']

# Function to extract sort keys from column names
def sort_key(col):
    if col.endswith("PV-MEAS"):
        return (col[:-5], col[-4:], 0)  # 'MEAS' sorting as the first
    location_year, db = col.split('_', 1)  # Split at the first underscore
    year = location_year[-4:]  # Extract the year (last four characters)
    location = location_year[:-4]  # Extract location (all but last four characters)
    db_key = db.split('-')[1] if '-' in db else db  # Normalize the db part for sorting
    db_index = database_order.index(db_key) if db_key in database_order else len(database_order)
    return (location, year, db_index)

# Sort columns based on custom key
sorted_columns = sorted(output_df.columns, key=sort_key)

# Reorder DataFrame according to sorted columns
output_df = output_df[sorted_columns]

# Generate new column headers based on the sorted columns
new_columns = []
index_counter = 1

for col in sorted_columns:
    parts = col.split('_')
    if len(parts) > 2:  # Check if there are enough parts
        location = parts[0]
        year = parts[1]
        db = parts[2]
        db_name = db.split('-')[1] if '-' in db else db  # Extract database name correctly
        location_year = f"{location}{year}"
        new_columns.append(("Solar fixed", location_year, db, "RPU_Solar_fixed", str(index_counter)))
    else:
        print(f"Unexpected column format: {col}")
    index_counter += 1
#for col in sorted_columns:
#    location_year, db = col.split('_', 1)
#    new_columns.append(("Solar fixed", location_year, f"PV-{db.split('-')[1]}", "RPU_Solar_fixed", str(index_counter)))
#    print(location_year)
#    index_counter += 1


# Create a MultiIndex
multi_index = pd.MultiIndex.from_tuples(new_columns, names=["", "Locations", "Profile time series", "Subsets", "Index"])

# Assign this MultiIndex to the DataFrame
output_df.columns = multi_index

# Create directory for saving result file
output_dir = os.path.join("Time series analysis graphs", 'Input files')
os.makedirs(output_dir, exist_ok=True)

# Save the DataFrame to CSV
output_file = f"{location_name}_meas_sim.csv"
output_df.to_csv(os.path.join(output_dir, output_file))

print("Output CSV file successfully generated!")
