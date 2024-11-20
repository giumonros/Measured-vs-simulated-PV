import pandas as pd
import matplotlib.pyplot as plt
import os

#----------------------------------------------------------------------------------------------

# Define location name (same as the one in the folder "Measured PV data") and renewables.ninja token

location_name = "Utrecht"  # This can be changed to any other location

#----------------------------------------------------------------------------------------------

# Create directory for saving graphs
output_dir = "Output graphs"
os.makedirs(output_dir, exist_ok=True)
output_dir_loc = os.path.join(output_dir,location_name)
os.makedirs(output_dir_loc, exist_ok=True)

#Collect the clear sky day and cloudy sky day high resolution data 

file_path = os.path.join("Measured PV data", f"{location_name}.xlsx")
clear_sky_df = pd.read_excel(file_path, sheet_name='Clear sky day')
cloudy_sky_df = pd.read_excel(file_path, sheet_name='Cloudy sky day')

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


#Take hourly data from the "Simulated and measured PV data" file for the correct day


# Definition of columns of interest 
column_names = ['Timeserie', 'PV_MEASURED_sec', 'PV_MEASURED_hourly', 'RN_MERRA2', 'RN_SARAH', 'PG_SARAH', 'PG_SARAH2', 'PG_ERA5', 'CR_ERA5']
legend_names = [ 'Measured data', 'Measured hourly', 'RN_MERRA2', 'RN_SARAH', 'PG_SARAH', 'PG_SARAH2', 'PG_ERA5', 'CR_ERA5']  # Excludes 'Timeserie' from the legend names
colors = ['red', 'black', 'blue','blue', 'orange','orange','orange','green']
linestyles = ['-', '-', '--', ':', ':', '-','-.','-.']
line_widths = [2, 3, 2,2,2,2,2,2]

def plot_data(df1, df2):
    fig, axs = plt.subplots(1, 2, figsize=(20, 4))  # Compact layout
    
    # Extract the time series column
    time_series1 = df1[column_names[0]]
    time_series2 = df2[column_names[0]]
    
    # Plotting for Clear Sky Day
    for i, column in enumerate(column_names[1:]):  # Iterate only over columns of interest
        axs[0].plot(time_series1, df1[column], label=legend_names[i],
                    color=colors[i], linestyle=linestyles[i], linewidth=line_widths[i])
    axs[0].set_title(f'{location_name} - Clear Sky Day', fontsize=20)
    axs[0].set_xlabel('Number of timesteps', fontsize=16)
    axs[0].set_ylabel('Normalized power profiles', fontsize=16)
    axs[0].set_xlim(0, time_series1.max())  # Sets x-axis limits
    axs[0].set_ylim(0, 1)  # Sets y-axis limits
    #axs[0].legend(fontsize=10)
    axs[0].grid(True)
    
    # Plotting for Cloudy Sky Day
    for i, column in enumerate(column_names[1:]):  # Iterate only over columns of interest
        axs[1].plot(time_series2, df2[column], label=legend_names[i],
                    color=colors[i], linestyle=linestyles[i], linewidth=line_widths[i])
    axs[1].set_title(f'{location_name} - Cloudy Sky Day', fontsize=20)
    axs[1].set_xlabel('Number of timesteps', fontsize=16)
    axs[1].set_ylabel('Normalized power profiles', fontsize=16)
    axs[1].set_xlim(0, time_series2.max())  # Sets x-axis limits
    axs[1].set_ylim(0, 1)  # Sets y-axis limits
    #axs[1].legend(fontsize=15)
    axs[1].grid(True)

    # Adjust y-axis label size for both subplots
    for ax in axs:
        ax.tick_params(axis='y', labelsize=15)
        ax.tick_params(axis='x', labelsize=15)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir_loc, f'{location_name}_sec_vs_hourly_graph.png'), bbox_inches='tight')
    plt.close()
    print("Seconds vs hourly time series figure successfully generated in the 'Output graphs' folder")
    #plt.show()

# Plotting both graphs side by side
plot_data(clear_sky_df, cloudy_sky_df)
