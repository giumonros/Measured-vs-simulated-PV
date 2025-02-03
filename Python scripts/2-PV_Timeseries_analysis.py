import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import re
import math
import sys
from sklearn.metrics import mean_absolute_error, mean_squared_error
from matplotlib.colors import LinearSegmentedColormap

#------------------------------------------------------------------------------------------

# Define location name and year
location_name = sys.argv[1]
location_year = sys.argv[2]
#location_name = "Almeria"  # This can be changed to any other location available in the Measured PV data folder
#location_year = "All years" # Write a specific year to avoid drawing graphs for all the years available the Measured PV data file

#------------------------------------------------------------------------------------------

# Create directory or use the already existing directory for saving graphs 
output_dir = "Results and graphs"
os.makedirs(output_dir, exist_ok=True)
output_dir_timeseries = os.path.join(output_dir,location_name,"Time series analysis results")
os.makedirs(output_dir_timeseries, exist_ok=True)

#Define file path for the simulated and measured PV data file and read csv file
file_path = os.path.join("Simulated and measured PV data", f"{location_name}_meas_sim.csv")
data_sim_meas = pd.read_csv(file_path, header=None).iloc[:, 1:]  # Skip the first column and load without headers

#Collect the clear sky day and cloudy sky day high resolution data for the selected location

file_path_PVdata = os.path.join("Measured PV data", f"{location_name}.xlsx")
clear_sky_df = pd.read_excel(file_path_PVdata, sheet_name='Clear sky day')
cloudy_sky_df = pd.read_excel(file_path_PVdata, sheet_name='Cloudy sky day')

# *********** Pre-process the "Measured PV data" input file ***************

# Function to convert columns with commas to decimal numbers
def convert_comma_to_dot(df):
    for column in df.columns:
        if df[column].dtype == 'object':  # Checks if the column is of type object (i.e., strings)
            df[column] = df[column].str.replace(',', '.')  # Replaces commas with dots
            try:
                df[column] = df[column].astype(float)  # Attempts to convert the column to float
            except ValueError:
                pass  # If conversion fails, leaves the column as it is (it may contain non-numeric text)
    return df

# Apply the conversion function to both DataFrames
clear_sky_df = convert_comma_to_dot(clear_sky_df)
cloudy_sky_df = convert_comma_to_dot(cloudy_sky_df)

# *********** Pre-process the "simulated and measured PV data" and "input file" ***************

# Drop specific rows (originally 0, 3, and 4) that are useful only for the techno-economic assessment
data_sim_meas.drop(index=[0, 3, 4], inplace=True)
# Reset index to realign row numbers
data_sim_meas.reset_index(drop=True, inplace=True)

# Set new headers using the first two rows as MultiIndex
new_headers = data_sim_meas.iloc[0:2]
data_sim_meas = data_sim_meas[2:]  # Remove header rows from data
data_sim_meas.columns = pd.MultiIndex.from_tuples(tuple(zip(new_headers.iloc[0], new_headers.iloc[1])))

# Trim the data to the first 8760 rows (one year of hourly data)
data_sim_meas = data_sim_meas.iloc[:8760, :]

# Combine headers to form unique column identifiers
data_sim_meas.columns = [' '.join(col).strip() for col in data_sim_meas.columns.values]
data_sim_meas = data_sim_meas.apply(pd.to_numeric, errors='coerce', axis=1)  # Convert to numeric where possible

# ********** Merge the "Simulated and measured PV data" and "Measured PV data" for the clear sky and cloudy day figure

## Select which year of data should be kept based on the infos inside the input excel file

def extract_year_selected(dataframe, column_pattern=r"([A-Za-z]+[0-9]{4})"):
    """
    Extract the PlaceYear (e.g., LocationYear) from a dataframe's column names.
    
    Parameters:
        dataframe (pd.DataFrame): The dataframe to search.
        column_pattern (str): The regex pattern to match PlaceYear format.
        
    Returns:
        str: The extracted PlaceYear.
        
    Raises:
        ValueError: If no matching column is found.
    """
    for col in dataframe.columns:
        match = re.match(column_pattern, col)
        if match:
            return match.group(1)
    
    # If no match is found, raise an error
    raise ValueError(
        "Column entry for cloudy and clear sky data should be written as 'LocationYear PV-MEAS_high_resolution'."
    )

## Process data for the cloudy sky year
year_selected_cloudy = extract_year_selected(cloudy_sky_df)
data_sim_meas_filtered_cloudy = data_sim_meas[[col for col in data_sim_meas.columns if year_selected_cloudy in col]]
data_sim_meas_filtered_cloudy = data_sim_meas_filtered_cloudy.reset_index()  # Adds a new column 'index' with row numbers starting from 0
data_sim_meas_filtered_cloudy.rename(columns={'index': 'Hour of the year'}, inplace=True)  # Rename for matching
data_sim_meas_filtered_cloudy["Hour of the year"] = range(1, len(data_sim_meas_filtered_cloudy) + 1)  # Makes hour of the year start from 1

# Merge with the cloudy sky DataFrame
cloudy_sky_df = cloudy_sky_df.merge(data_sim_meas_filtered_cloudy, on='Hour of the year', how='left')
# Remove the first two columns
cloudy_sky_df = cloudy_sky_df.iloc[:, 2:]

# Process data for the clear sky year

year_selected_clear = extract_year_selected(clear_sky_df)
data_sim_meas_filtered_clear = data_sim_meas[[col for col in data_sim_meas.columns if year_selected_clear in col]]
data_sim_meas_filtered_clear = data_sim_meas_filtered_clear.reset_index()  # Adds a new column 'index' with row numbers starting from 0
data_sim_meas_filtered_clear.rename(columns={'index': 'Hour of the year'}, inplace=True)  # Rename for matching
data_sim_meas_filtered_clear["Hour of the year"] = range(1, len(data_sim_meas_filtered_clear) + 1)  # Makes hour of the year start from 1

# Merge with the clear sky DataFrame
clear_sky_df = clear_sky_df.merge(data_sim_meas_filtered_clear, on='Hour of the year', how='left')
# Remove the first two columns
clear_sky_df = clear_sky_df.iloc[:, 2:]

#Remove the years that are not wanted for the figures (user defined)

## Check if any column name contains the specified year
columns_with_year = [col for col in data_sim_meas.columns if location_year in col]

## If columns are found for the specified year, keep only those
if columns_with_year:
    data_sim_meas = data_sim_meas[columns_with_year]
else:
    ## Otherwise, retain all columns
    print(f"No specific year chosen or year not available: plot for all years instead")

# ************ Custom settings for all the plots (colors, line styles, etc.) *********

# Identify unique locations
locations = list(set(col.split()[0] for col in data_sim_meas.columns))
#Identify unique time series for legend names
legend_names = list(set(col.split()[1] for col in data_sim_meas.columns))
#Legend names for the clear sky and cloudy day Figure
legend_names_high_res = list(set(
    col.split()[1]
    for df in [cloudy_sky_df, clear_sky_df]  # Iterate over both DataFrames
    for col in df.columns
    if len(col.split()) == 2  # Ensure the column name splits into exactly two parts
))

# Initialize lists for colors and line styles for the capacity factor and high resolution PV data figure
colors_CF = []
linestyles_CF = []

colors_high_res = []
linestyles_high_res = []

# Loop through each legend name and assign color and line style (can possibly be changed)
for name in legend_names:
    # Determine color based on keywords
    if "PV-MEAS" in name:
        colors_CF.append("red")
    elif "RN" in name:
        colors_CF.append("blue")
    elif "PG2" in name:
        colors_CF.append("orange")
    elif "PG3" in name:
        colors_CF.append("sienna")
    elif "CR" in name:
        colors_CF.append("green")
    elif "SIM" in name:
        colors_CF.append("purple")
    else:
        colors_CF.append("black")  # Default color if no match

    # Determine line style based on keywords
    if "PV-MEAS" in name:
        linestyles_CF.append("-")
    elif "MERRA2" in name:
        linestyles_CF.append("--")
    elif "SARAH3" in name:
        linestyles_CF.append("-")
    elif "SARAH2" in name:
        linestyles_CF.append("-")
    elif "SARAH" in name:
        linestyles_CF.append(":")
    elif "ERA5" in name:
        linestyles_CF.append("-.")
    else:
        linestyles_CF.append("-.")  # Default line style if no match

for name in legend_names_high_res:
    # Determine color based on keywords
    if "PV-MEAS_high_resolution" in name:
        colors_high_res.append("red")
    elif "PV-MEAS" in name:
        colors_high_res.append("black")
    elif "RN" in name:
        colors_high_res.append("blue")
    elif "PG2" in name:
        colors_high_res.append("orange")
    elif "PG3" in name:
        colors_high_res.append("sienna")
    elif "CR" in name:
        colors_high_res.append("green")
    elif "SIM" in name:
        colors_high_res.append("purple")
    else:
        colors_high_res.append("darkgreen")  # Default color if no match

    # Determine line style based on keywords
    if "PV-MEAS_high_resolution" in name:
        linestyles_high_res.append("-")
    elif "PV-MEAS" in name:
        linestyles_high_res.append("-")
    elif "MERRA2" in name:
        linestyles_high_res.append("--")
    elif "SARAH3" in name:
        linestyles_high_res.append("-")
    elif "SARAH2" in name:
        linestyles_high_res.append("-")
    elif "SARAH" in name:
        linestyles_high_res.append(":")
    elif "ERA5" in name:
        linestyles_high_res.append("-.")
    else:
        linestyles_high_res.append("-.")  # Default line style if no match

# Initialize the line_widths list for the capacity factor figure based on the condition
line_widths_CF = [3 if name == "PV-MEAS" else 2 for name in legend_names]
line_widths_high_res= [3 if name == "PV-MEAS" else 2 for name in legend_names_high_res]


# Define color palette for bar plots with metrics
plot_palette = {
    'RN-MERRA2': 'blue',
    'PG2-SARAH2': 'orange',
    'PG3-SARAH3': 'sienna',
    'PG3-ERA5': 'darkgoldenrod',
    'RN-SARAH': 'dodgerblue',
    'PG2-SARAH': 'gold',
    'PG2-ERA5': 'green',
    'SIM-SELF1': 'purple',
}

# Customize the colormap for scatter plots
jet = plt.cm.jet
colors = jet(np.linspace(0, 1, 256))
for i in range(colors.shape[0]):
    colors[i, -1] = np.linspace(0.4, 0.8, 256)[i]  # Adjust transparency
custom_cmap = LinearSegmentedColormap.from_list('jet_custom', colors)

# ********************* Draw all the plots **********************

# Initialize result dictionaries for each metric for the metric plot(Mean Difference, MAE, RMSE)
mean_diff_results = []
mae_results = []
rmse_results = []

# Process data for each location and year
for location in locations:
    # Filter columns for the current location
    loc_data = data_sim_meas[[col for col in data_sim_meas.columns if col.startswith(location)]]
    
    # Identify 'PV-MEAS' column as the real (measured) data
    meas_column = next((col for col in loc_data.columns if 'PV-MEAS' in col), None)
    if meas_column is None:
        print(f"Skipping {location}: 'PV-MEAS' column missing.")
        continue

    # Identify simulations columns with only zero values 
    valid_columns = [meas_column] + [col for col in loc_data.columns if col != meas_column and not loc_data[col].eq(0).all()]
    
    # Filter data to exclude rows with zero values in the measured data column and simulation columns with only zero values (used for scatter plot only)
    filtered_data_scat = loc_data[loc_data[meas_column] != 0]
    filtered_data_scat = filtered_data_scat[valid_columns]
    measured_data_scat = filtered_data_scat[meas_column].squeeze()  # Measured

    # ********************************************* Plot hourly capacity factors ********************************************************
    plt.figure(figsize=(10, 6))
    loc_data_sorted = loc_data.apply(lambda x: x.sort_values(ascending=False).reset_index(drop=True))
    for idx, tool in enumerate(legend_names):
        tool_column = f"{location} {tool}"
        if tool_column in loc_data_sorted.columns:
            plt.plot(loc_data_sorted[tool_column], label=tool, color=colors_CF[idx],
                     linestyle=linestyles_CF[idx], linewidth=line_widths_CF[idx])

    plt.title(f'{location}', fontsize=20)
    plt.xlabel('Hour of the year', fontsize=18)
    plt.ylabel('Capacity Factor', fontsize=18)
    plt.grid(True)
    plt.ylim(0, 1)
    plt.xlim(0, 5000)
    plt.legend(loc='upper right', fontsize=12)
    plt.savefig(os.path.join(output_dir_timeseries, f"{location}_Capacity_Factors.png"), bbox_inches='tight')
    print(f"Capacity factors figure successfully generated in the '{output_dir}' folder for {location}")
    plt.close()

    # ************************************************* Generate scatter plots for each simulation tool *******************************************************
    sim_columns = [col for col in valid_columns if col != meas_column]
    cols = int(math.ceil(math.sqrt(len(sim_columns))))
    rows = int(math.ceil(len(sim_columns) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 6, rows * 6))
    axs = axs.flatten() if len(sim_columns) > 1 else [axs]

    for idx, sim_col in enumerate(sim_columns):
        ax = axs[idx]
        simulated_data_scat = filtered_data_scat[sim_col].squeeze()
        sns.scatterplot(x=measured_data_scat, y=simulated_data_scat, alpha=0.5, edgecolor='w', linewidth=0.5, label='Simulated data', s=15, ax=ax)
        sns.kdeplot(x=measured_data_scat, y=simulated_data_scat, fill=True, cmap=custom_cmap, levels=20, ax=ax)
        sns.scatterplot(x=measured_data_scat, y=measured_data_scat, alpha=0.5, edgecolor='w', color='r', linewidth=0.5, label='Measured data', s=15, ax=ax)

        ax.set_title(f"{location} - {sim_col.split()[1]}", fontsize=20)
        ax.set_xlabel('Measured Data', fontsize=18)
        ax.set_ylabel('Simulated Data', fontsize=18)
        ax.grid(True)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.legend(scatterpoints=1, markerscale=2, fontsize=18, loc='upper left')
    for j in range(idx + 1, len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir_timeseries, f'{location}_scatterplot.png'))
    print(f"Scatter plot figure successfully generated in the '{output_dir}' folder for {location}")
    plt.close()

# ************************************************************ Error analysis*********************************************************************  
    # Calculate and store metrics for each simulation tool
    for sim_col in valid_columns:
        if sim_col != meas_column and any(tool in sim_col for tool in plot_palette.keys()):
            simulated_data_err_an = loc_data[sim_col].dropna()
            measured_data_err_an = loc_data[meas_column].dropna()
            if not simulated_data_err_an.empty:
                mean_diff = (simulated_data_err_an.mean() - measured_data_err_an.mean()) * 100
                mae = mean_absolute_error(measured_data_err_an, simulated_data_err_an) * 100
                rmse = np.sqrt(mean_squared_error(measured_data_err_an, simulated_data_err_an)) * 100
                mean_diff_results.append({'Location': location, 'Tool': sim_col.split()[1], 'Mean Difference (%)': mean_diff})
                mae_results.append({'Location': location, 'Tool': sim_col.split()[1], 'MAE (%)': mae})
                rmse_results.append({'Location': location, 'Tool': sim_col.split()[1], 'RMSE (%)': rmse})
    
# Plot for error analysis
def add_labels(ax):
    for p in ax.patches:  # Loop through all bars in the subplot
        height = p.get_height()  # Get the height (value) of the bar
        if abs(height) > 1e-3:  # Ignore near-zero bars to prevent "0.0" labels
            if height >= 0:
                # For positive values, place the label above the bar
                ax.annotate(format(height, '.1f'),  # Format the label to one decimal place
                            (p.get_x() + p.get_width() / 2., height),  # Position at the center of the bar
                            ha='center',  # Center horizontally
                            va='bottom',  # Align to the top of the bar
                            xytext=(0, 5),  # 10 points above the bar
                            textcoords='offset points',  # Use offset for positioning
                            fontsize=11)  # Font size
            else:
                # For negative values, place the label below the bar
                ax.annotate(format(height, '.1f'),  # Format the label to one decimal place
                            (p.get_x() + p.get_width() / 2., height),  # Position at the center of the bar
                            ha='center',  # Center horizontally
                            va='bottom',  # Align to the bottom of the bar
                            xytext=(0, 16),  # 10 points below the bar
                            textcoords='offset points',  # Use offset for positioning
                            fontsize=11)  # Font size
  
# Create a figure with three subplots
fig, axes = plt.subplots(3, 1, figsize=(16, 15))

# Define tick font size
tick_font_size = 16

# Extract the tool order from the palette (ensures tools are plotted in this specific order)
tool_order = list(plot_palette.keys())

mean_diff_df = pd.DataFrame(mean_diff_results)
mae_df = pd.DataFrame(mae_results)
rmse_df = pd.DataFrame(rmse_results)

# Sort DataFrames by Location
mean_diff_df.sort_values(by='Location', inplace=True)
mae_df.sort_values(by='Location', inplace=True)
rmse_df.sort_values(by='Location', inplace=True)

# Plot Mean Difference
sns.barplot(x='Location', y='Mean Difference (%)', hue='Tool', data=mean_diff_df,
            palette=plot_palette, hue_order=tool_order, ax=axes[0])
axes[0].set_ylabel('Annual average \nCF difference (%)', fontsize=20)
axes[0].tick_params(axis='both', labelsize=tick_font_size)
axes[0].set_axisbelow(True)
axes[0].grid(True, axis='y')
axes[0].set_xlabel('')
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}')) 
axes[0].get_legend().remove()
axes[0].set_ylim(-0.4, 4)  # Adjust y-limit before adding labels
add_labels(axes[0])

# Plot MAE
sns.barplot(x='Location', y='MAE (%)', hue='Tool', data=mae_df,
            palette=plot_palette, hue_order=tool_order, ax=axes[1])
axes[1].set_ylabel('Annual MAE \nof CF (%)', fontsize=20)
axes[1].tick_params(axis='both', labelsize=tick_font_size)
axes[1].set_axisbelow(True)
axes[1].grid(True, axis='y')
axes[1].set_xlabel('')
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}')) 
axes[1].get_legend().remove()
axes[1].set_ylim(-0.3, 8)  # Adjust y-limit before adding labels
add_labels(axes[1])

# Plot RMSE
sns.barplot(x='Location', y='RMSE (%)', hue='Tool', data=rmse_df,
            palette=plot_palette, hue_order=tool_order, ax=axes[2])
axes[2].set_ylabel('Annual RMSE of CF (%)', fontsize=20)
axes[2].tick_params(axis='both', labelsize=tick_font_size)
axes[2].set_axisbelow(True)
axes[2].grid(True, axis='y')
axes[2].set_xlabel('Location', fontsize=20)
axes[2].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}')) 
axes[2].get_legend().remove()
axes[2].set_ylim(-0.3, 15)  # Adjust y-limit before adding labels
add_labels(axes[2])

# Adjust layout
plt.tight_layout()

# Filter legend to only show labels in `legend_names`
handles, labels = axes[2].get_legend_handles_labels()  # Use handles from the last subplot
filtered_handles_labels = [(h, l) for h, l in zip(handles, labels) if l in legend_names]
filtered_handles, filtered_labels = zip(*filtered_handles_labels) if filtered_handles_labels else ([], [])

# Create one legend for all plots at the bottom
fig.legend(
    filtered_handles, filtered_labels, loc='lower center', ncol=len(tool_order),
    bbox_to_anchor=(0.5, -0.05), fontsize=16, title_fontsize=18, frameon=False
)

# Save the combined plot
combined_plot_path = os.path.join(output_dir_timeseries, f'{location_name}_Errors_Analysis.png')
plt.savefig(combined_plot_path, bbox_inches='tight')
print(f"Combined error analysis figure successfully generated in the '{output_dir}' folder")
plt.close()



# ******************************************Plot cloudy and clear sky Figure **************************************************************

def plot_data(df1, df2):
    fig, axs = plt.subplots(1, 2, figsize=(20, 4))  # Compact layout
    
    column_names_df1 = df1.columns.tolist()
    column_names_df2 = df2.columns.tolist()

    # Extract the time series column
    time_series1 = df1.index
    time_series2 = df2.index

    # Initialize lists to collect handles and labels for the legend
    all_handles = []
    all_labels = []
    
    # Plotting for Clear Sky Day
    for i, column in enumerate(column_names_df1):  # Iterate only over all columns in df1
        # Check if the legend matches a valid entry
        if column.split()[1] in legend_names_high_res:  # Match against the legend
            idx = legend_names_high_res.index(column.split()[1])  # Get the index in the legend list
            line, = axs[0].plot(time_series1, df1[column], label=legend_names_high_res[idx],
                                color=colors_high_res[idx], linestyle=linestyles_high_res[idx], linewidth=line_widths_high_res[idx])
            if line.get_label() not in all_labels:  # Avoid duplicate labels
                all_handles.append(line)
                all_labels.append(line.get_label())
    axs[0].set_title(f'{location_name} - Clear Sky Day', fontsize=20)
    axs[0].set_xlabel('Number of timesteps', fontsize=16)
    axs[0].set_ylabel('Normalized power profiles', fontsize=16)
    axs[0].set_xlim(0, len(df1))  # Sets x-axis limits
    axs[0].set_ylim(0, 1)  # Sets y-axis limits
    axs[0].grid(True)
    
    # Plotting for Cloudy Sky Day
    for i, column in enumerate(column_names_df2):  # Iterate only over all columns in df2
        # Check if the legend matches a valid entry
        if column.split()[1] in legend_names_high_res:  # Match against the legend
            idx = legend_names_high_res.index(column.split()[1])  # Get the index in the legend list
            line, = axs[1].plot(time_series2, df2[column], label=legend_names_high_res[idx],
                                color=colors_high_res[idx], linestyle=linestyles_high_res[idx], linewidth=line_widths_high_res[idx])
            if line.get_label() not in all_labels:  # Avoid duplicate labels
                all_handles.append(line)
                all_labels.append(line.get_label())
    axs[1].set_title(f'{location_name} - Cloudy Sky Day', fontsize=20)
    axs[1].set_xlabel('Number of timesteps', fontsize=16)
    axs[1].set_ylabel('Normalized power profiles', fontsize=16)
    axs[1].set_xlim(0, len(df2))  # Sets x-axis limits
    axs[1].set_ylim(0, 1)  # Sets y-axis limits
    axs[1].grid(True)


    # Adjust y-axis label size for both subplots
    for ax in axs:
        ax.tick_params(axis='y', labelsize=15)
        ax.tick_params(axis='x', labelsize=15)
    
    # Calculate ncol dynamically to fit all items in one line or max two rows
    max_items_per_row = 9  # Adjust this number based on figure width and font size
    ncol = min(len(all_labels), max_items_per_row)

    # Add a single legend at the bottom
    fig.legend(all_handles, all_labels, loc='lower center', bbox_to_anchor=(0.5, -0.15),
               ncol=ncol, fontsize=15)

    plt.tight_layout()  # Adjust rect to leave space for the legend
    plt.savefig(os.path.join(output_dir_timeseries, f'{location_name}_sec_vs_hourly_graph.png'), bbox_inches='tight')
    plt.close()
    print(f"High resolution PV data figure successfully generated in the '{output_dir}' folder for {location}")

# Plotting both graphs side by side
plot_data(clear_sky_df,cloudy_sky_df)