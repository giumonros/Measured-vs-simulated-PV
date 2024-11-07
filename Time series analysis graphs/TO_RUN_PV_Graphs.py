import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Set up directories and file paths
input_file_path = os.path.join("Input files", "Utrecht_meas_sim.csv")
output_dir = 'Location Graphs'
os.makedirs(output_dir, exist_ok=True)

# Load the data
data = pd.read_csv(input_file_path, header=None).iloc[:, 1:]
data.drop(index=[0, 3, 4], inplace=True)
data.reset_index(drop=True, inplace=True)
new_headers = data.iloc[0:2]
data = data[2:]
data.columns = pd.MultiIndex.from_tuples(tuple(zip(new_headers.iloc[0], new_headers.iloc[1])))
data.columns = [' '.join(col).strip() for col in data.columns.values]

# Extract unique locations
locations = data.columns.get_level_values(0).unique().tolist()

# Plotting configurations for capacity factors
legend_names = ['PV-MEAS', 'RN-MERRA2', 'RN-SARAH', 'PG-SARAH', 'PG-SARAH2', 'PG-ERA5', 'CR-ERA5']
colors = ['red', 'blue', 'blue', 'orange', 'orange', 'orange', 'green']
linestyles = ['-', '--', ':', ':', '-','-.','-.']
line_widths = [3, 2, 2, 2, 2, 2, 2]

# Plotting configurations for MAE and RMSE
plot_palette = {
    'RN-MERRA2': 'blue',
    'PG-SARAH2': 'orange',
    'PG-ERA5': 'darkgoldenrod',
    'CR-ERA5': 'green',
    'PG-SARAH': 'gold',
    'RN-SARAH': 'dodgerblue',
}

# Process and plot data for each location
for location in locations:
    loc_data = data[[col for col in data.columns if location in col]]

    # Part 1: Capacity Factor Line Plots
    fig, ax = plt.subplots(figsize=(10, 5))
    for idx, tool in enumerate(legend_names):
        tool_column = f'{location} {tool}'
        if tool_column in loc_data.columns:
            ax.plot(loc_data[tool_column].dropna().reset_index(drop=True), label=tool, color=colors[idx], linestyle=linestyles[idx], linewidth=line_widths[idx])

    ax.set_title(f'Capacity Factor: {location}', fontsize=20)
    ax.set_xlabel('Hour of the year', fontsize=18)
    ax.set_ylabel('Capacity Factor', fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.grid(True)
    ax.legend(fontsize=12, loc='upper right')
    ax.set_ylim(0, 1)
    ax.set_xlim(0, len(loc_data))
    fig.savefig(os.path.join(output_dir, f'{location}_Capacity_Factor.png'), bbox_inches='tight')
    plt.close(fig)

    # Part 2: Difference, MAE, RMSE Bar Plots
    fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    result_dfs = []

    for tool in plot_palette.keys():
        tool_column = f'{location} {tool}'
        if tool_column in loc_data.columns:
            valid_data = loc_data[[f'{location} PV-MEAS', tool_column]].dropna()
            mean_diff = (valid_data[tool_column].mean() - valid_data[f'{location} PV-MEAS'].mean()) * 100
            mae = mean_absolute_error(valid_data[f'{location} PV-MEAS'], valid_data[tool_column]) * 100
            rmse = np.sqrt(mean_squared_error(valid_data[f'{location} PV-MEAS'], valid_data[tool_column])) * 100

            result_dfs.append(pd.DataFrame({
                'Metric': ['Mean Difference', 'MAE', 'RMSE'],
                'Value': [mean_diff, mae, rmse],
                'Tool': tool
            }))

    results = pd.concat(result_dfs)
    metrics = ['Mean Difference', 'MAE', 'RMSE']
    for idx, metric in enumerate(metrics):
        sns.barplot(x='Tool', y='Value', hue='Tool', data=results[results['Metric'] == metric], ax=axes[idx], palette=plot_palette)
        axes[idx].set_title(f'{metric} for {location}')
        axes[idx].set_ylabel(f'{metric} (%)')
        axes[idx].get_legend().remove()

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, f'{location}CFdiff_MAE_RMSE.png'), bbox_inches='tight')
    plt.close(fig)
