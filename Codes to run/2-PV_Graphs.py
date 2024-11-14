import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import math
from sklearn.metrics import mean_absolute_error, mean_squared_error
from matplotlib.colors import LinearSegmentedColormap


#------------------------------------------------------------------------------------------

# Define location name
location_name = "Utrecht"  # This can be changed to any other location

#------------------------------------------------------------------------------------------

#Define file path
file_path = os.path.join("Simulated and measured PV data", f"{location_name}_meas_sim.csv")
data = pd.read_csv(file_path, header=None).iloc[:, 1:]  # Skip the first column and load without headers

# Drop specific rows (originally 0, 3, and 4)
data.drop(index=[0, 3, 4], inplace=True)

# Reset index to realign row numbers
data.reset_index(drop=True, inplace=True)

# Set new headers using the first two rows as MultiIndex
new_headers = data.iloc[0:2]
data = data[2:]  # Remove header rows from data
data.columns = pd.MultiIndex.from_tuples(tuple(zip(new_headers.iloc[0], new_headers.iloc[1])))

# Trim the data to the first 8760 rows (one year of hourly data)
data = data.iloc[:8760, :]

# Combine headers to form unique column identifiers
data.columns = [' '.join(col).strip() for col in data.columns.values]
data = data.apply(pd.to_numeric, errors='coerce', axis=1)  # Convert to numeric where possible

# Identify unique locations
locations = list(set(col.split()[0] for col in data.columns))

# Create directory for saving graphs
output_dir = "Output graphs"
os.makedirs(output_dir, exist_ok=True)
output_dir_loc = os.path.join(output_dir,location_name)
os.makedirs(output_dir_loc, exist_ok=True)

# Custom settings for the plots (colors, line styles, etc.)
legend_names = ['PV-MEAS', 'RN-MERRA2', 'RN-SARAH', 'PG2-SARAH', 'PG2-SARAH2', 'PG2-ERA5', 'PG3-SARAH3', 'PG3-ERA5','CR-ERA5', 'SIM-SELF1']
colors_CF = ['red', 'blue', 'blue', 'orange', 'orange', 'orange', 'darkorange', 'darkorange', 'green', 'purple']
linestyles = ['-', '--', ':', ':', '-', '-.', '-', '-.', '-.', '-.']
line_widths = [3, 2, 2, 2, 2, 2, 2, 2, 2, 2]

# Define color palette for bar plots
plot_palette = {
    'RN-MERRA2': 'blue',
    'PG3-SARAH3': 'orange',
    'PG3-ERA5': 'darkgoldenrod',
    'CR-ERA5': 'green',
    'PG2-SARAH': 'gold',
    'RN-SARAH': 'dodgerblue',
    'SIM-SELF1': 'purple',
}

# Customize the colormap for scatter plots
jet = plt.cm.jet
colors = jet(np.linspace(0, 1, 256))
for i in range(colors.shape[0]):
    colors[i, -1] = np.linspace(0.4, 0.8, 256)[i]  # Adjust transparency
custom_cmap = LinearSegmentedColormap.from_list('jet_custom', colors)

# Initialize result dictionaries for each metric (Mean Difference, MAE, RMSE)
mean_diff_results = []
mae_results = []
rmse_results = []

# Process data for each location
for location in locations:
    # Filter columns for the current location
    loc_data = data[[col for col in data.columns if col.startswith(location)]]
    
    # Identify 'PV-MEAS' column as the real (measured) data
    meas_column = next((col for col in loc_data.columns if 'PV-MEAS' in col), None)
    if meas_column is None:
        print(f"Skipping {location}: 'PV-MEAS' column missing.")
        continue

    # Filter data to exclude rows with zero values in the measured data column
    filtered_data = loc_data[loc_data[meas_column] != 0]
    
    # Further filter to exclude any simulation columns with only zero values
    valid_columns = [meas_column] + [col for col in loc_data.columns if col != meas_column and not loc_data[col].eq(0).all()]
    filtered_data = filtered_data[valid_columns]
    real_data = filtered_data[meas_column].squeeze()  # Measured data

    # Calculate and store metrics for each simulation tool
    for sim_col in valid_columns:
        if sim_col != meas_column and any(tool in sim_col for tool in plot_palette.keys()):
            simulated_data = filtered_data[sim_col].dropna()
            if not simulated_data.empty:
                mean_diff = (simulated_data.mean() - real_data.mean()) * 100
                mae = mean_absolute_error(real_data, simulated_data) * 100
                rmse = np.sqrt(mean_squared_error(real_data, simulated_data)) * 100
                mean_diff_results.append({'Location': location, 'Tool': sim_col.split()[1], 'Mean Difference (%)': mean_diff})
                mae_results.append({'Location': location, 'Tool': sim_col.split()[1], 'MAE (%)': mae})
                rmse_results.append({'Location': location, 'Tool': sim_col.split()[1], 'RMSE (%)': rmse})
    
    # Plot hourly capacity factors
    plt.figure(figsize=(10, 6))
    loc_data_sorted = filtered_data.apply(lambda x: x.sort_values(ascending=False).reset_index(drop=True))
    for idx, tool in enumerate(legend_names):
        tool_column = f"{location} {tool}"
        if tool_column in loc_data_sorted.columns:
            plt.plot(loc_data_sorted[tool_column], label=tool, color=colors_CF[idx],
                     linestyle=linestyles[idx], linewidth=line_widths[idx])

    plt.title(f'{location}', fontsize=20)
    plt.xlabel('Hour of the year', fontsize=18)
    plt.ylabel('Capacity Factor', fontsize=18)
    plt.grid(True)
    plt.ylim(0, 1)
    plt.xlim(0, 5000)
    plt.legend(loc='upper right', fontsize=12)
    plt.savefig(os.path.join(output_dir_loc, f"{location}_Capacity_Factors.png"), bbox_inches='tight')
    print("Capacity factors figure successfully generated in the 'Output graphs' folder")
    plt.close()

    # Generate scatter plots for each simulation tool
    sim_columns = [col for col in valid_columns if col != meas_column]
    cols = int(math.ceil(math.sqrt(len(sim_columns))))
    rows = int(math.ceil(len(sim_columns) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 6, rows * 6))
    axs = axs.flatten() if len(sim_columns) > 1 else [axs]

    for idx, sim_col in enumerate(sim_columns):
        ax = axs[idx]
        simulated_data = filtered_data[sim_col].squeeze()
        sns.scatterplot(x=real_data, y=simulated_data, alpha=0.5, edgecolor='w', linewidth=0.5, label='Simulated data', s=15, ax=ax)
        sns.kdeplot(x=real_data, y=simulated_data, fill=True, cmap=custom_cmap, levels=20, ax=ax)
        sns.scatterplot(x=real_data, y=real_data, alpha=0.5, edgecolor='w', color='r', linewidth=0.5, label='Measured data', s=15, ax=ax)

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
    plt.savefig(os.path.join(output_dir_loc, f'{location}_scatterplot.png'))
    print("Scatter plot figure successfully generated in the 'Output graphs' folder")
    plt.close()

# Convert metrics results to DataFrames
mean_diff_df = pd.DataFrame(mean_diff_results)
mae_df = pd.DataFrame(mae_results)
rmse_df = pd.DataFrame(rmse_results)

# Plot summary statistics
for location in locations:
    loc_mean_diff_df = mean_diff_df[mean_diff_df['Location'] == location]
    loc_mae_df = mae_df[mae_df['Location'] == location]
    loc_rmse_df = rmse_df[rmse_df['Location'] == location]
    fig, axes = plt.subplots(3, 1, figsize=(10, 14))
    sns.barplot(x='Tool', y='Mean Difference (%)', data=loc_mean_diff_df, palette=plot_palette, ax=axes[0])
    sns.barplot(x='Tool', y='MAE (%)', data=loc_mae_df, palette=plot_palette, ax=axes[1])
    sns.barplot(x='Tool', y='RMSE (%)', data=loc_rmse_df, palette=plot_palette, ax=axes[2])

    axes[0].set_ylabel('Mean Difference (%)')
    axes[1].set_ylabel('MAE (%)')
    axes[2].set_ylabel('RMSE (%)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir_loc, f'{location}_Errors_Analysis.png'))
    print("Error analysis figure successfully generated in the 'Output graphs' folder")
    plt.close()
