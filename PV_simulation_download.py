
import pandas as pd
import requests
import io
import time

# Load the Excel file
file_path = "input_datasheet.xlsx"
sheet_name = "datasheet"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Setup sessions for APIs
pvgis_session = requests.Session()
rn_session = requests.Session()
rn_token = 'b1c4fdb0061a9b31fe363bccaba98201f311e055'
rn_session.headers = {'Authorization': 'Token ' + rn_token}

# Databases for each API
pvgis_databases = ['PVGIS-SARAH2', 'PVGIS-ERA5']
rn_databases = ['merra2', 'sarah']

# Dictionary to store production data for each installation, database, and year
productions = {}

# Function to generate date ranges
def generate_date_ranges(start_year, end_year):
    return [(f"{year}-01-01", f"{year}-12-31") for year in range(start_year, end_year + 1)]

# Function to create URL for PVGIS
def create_pvgis_url(row, db, year):
    return (
        f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?"
        f"lat={row['latitude']}&lon={row['longitude']}&aspect={row['azimuth'] - 180}&angle={row['tilt']}"
        f"&pvcalculation=1&peakpower={int(row['peakpower_kW'])}.0&loss={row['loss']}&pvtechchoice={row['pv_technology']}"
        f"&startyear={year}&endyear={year}&outputformat=csv"
        f"&mountingplace={row['building/free']}&browser=1&raddatabase={db}"
    )

# Iterate over the dataframe to get production data for each installation
for index, row in df.iterrows():
    # PVGIS Data Retrieval
    for db in pvgis_databases:
        for year in range(int(row['startyear']), int(row['endyear']) + 1):
            api_url = create_pvgis_url(row, db, year)
            identifier = f"{row['cod']}{year}_PG-{db.split('-')[1]}"  # Append year here
            try:
                response = pvgis_session.get(api_url)
                if response.status_code == 200:
                    data = pd.read_csv(io.StringIO(response.text), skiprows=10)
                    data = data[:-7]  # Assuming data format requires removing the last 7 rows
                    productions.setdefault(identifier, []).extend(data["P"].astype(float).values)
                else:
                    print(f"Failed to retrieve data for {identifier}")
            except Exception as e:
                print(f"Error retrieving PVGIS data for {identifier}: {e}")

    # Renewable Ninja Data Retrieval
    for db in rn_databases:
        for date_from, date_to in generate_date_ranges(int(row['startyear']), int(row['endyear'])):
            year = date_from[:4]
            identifier = f"{row['cod']}{year}_RN-{db.upper()}"
            args = {
                'lat': row['latitude'],
                'lon': row['longitude'],
                'date_from': date_from,
                'date_to': date_to,
                'dataset': db,
                'capacity': row['peakpower_kW'],
                'system_loss': row['loss'] / 100,
                'tracking': 0 if row['fixed'] == 1 else row['tracking'],
                'tilt': row['tilt'],
                'azim': row['azimuth'],
                'format': 'csv'
            }
            while True:
                response = rn_session.get(f"https://www.renewables.ninja/api/data/pv", params=args)
                if response.status_code == 200:
                    data = pd.read_csv(io.StringIO(response.text), skiprows=3)
                    productions.setdefault(identifier, []).extend(data['electricity'].astype(float).values)
                    break
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 3600))
                    print(f"Rate limit hit for Renewable Ninja. Pausing for {retry_after} seconds.")
                    time.sleep(retry_after)
                else:
                    print(f"Failed to download Renewable Ninja data for {identifier}: {response.text}")
                    break

# Convert all lists to pandas Series and create a DataFrame
for key, value in productions.items():
    productions[key] = pd.Series(value)
output_df = pd.DataFrame(productions)

# Desired order for databases
database_order = ['RN-MERRA2', 'RN-SARAH', 'PG-SARAH', 'PG-SARAH2', 'PG-ERA5']

# Function to extract sort keys from column names
def sort_key(col):
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
    location_year, db = col.split('_', 1)
    new_columns.append(("Solar fixed", location_year, f"PG-{db.split('-')[1]}", "RPU_Solar_fixed", str(index_counter)))
    index_counter += 1

# Create a MultiIndex
multi_index = pd.MultiIndex.from_tuples(new_columns, names=["", "Locations", "Profile time series", "Subsets", "Index"])

# Assign this MultiIndex to the DataFrame
output_df.columns = multi_index

# Save the DataFrame to an Excel file
output_file = "Consolidated_Hourly_Production.xlsx"
output_df.to_excel(output_file, index=True)  # Make sure to set index=False if not using DataFrame index

print("Consolidated Excel sheet successfully generated!")