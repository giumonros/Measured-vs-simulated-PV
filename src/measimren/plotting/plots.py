import os
import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from measimren.plotting import plot_style_config as style_config

#------------------- Plot capacity factor duration curve -------------------------


def plot_capacity_factors(data_sim_meas, location_name, year, legend_names, colors_CF, linestyles_CF, line_widths_CF, output_dir_timeseries, x_limit=5000):
    """
    Plot the capacity factor figure for a given location and dataset.

    Parameters:
        data_sim_meas (pd.DataFrame): DataFrame with capacity factor time series for the location.
        location_name (str): Name of the location.
        legend_names (list): List of time series/legend names corresponding to the columns.
        colors_CF (list): List of colors for each time series.
        linestyles_CF (list): List of line styles for each time series.
        line_widths_CF (list): List of line widths for each time series.
        output_dir_timeseries (str): Path to save the figure.
        x_limit (int, optional): Maximum x-axis value (default is 5000).
    """

    plt.figure(figsize=(10, 6))

    # Filter columns for the current location
    loc_data = data_sim_meas[
        [col for col in data_sim_meas.columns if col.startswith(location_name)]
    ]
 
    # Sort data descending by value for each column (hourly capacity factor)
    loc_data_sorted = loc_data.apply(lambda x: x.sort_values(ascending=False).reset_index(drop=True))
    for idx, tool in enumerate(legend_names):
        tool_column = f"{location_name}{year} {tool}"
        if tool_column in loc_data_sorted.columns:
            plt.plot(
                loc_data_sorted[tool_column],
                label=tool,
                color=colors_CF[idx],
                linestyle=linestyles_CF[idx],
                linewidth=line_widths_CF[idx],
            )

    plt.title(f"{location_name}{year}", fontsize=20)
    plt.xlabel("Hour of the year", fontsize=18)
    plt.ylabel("Capacity Factor", fontsize=18)
    plt.grid(True)
    plt.ylim(0, 1)
    plt.xlim(0, x_limit)
    plt.legend(loc="upper right", fontsize=12)

    output_file = os.path.join(output_dir_timeseries, f"{location_name}{year}_Capacity_Factors.png")
    plt.savefig(output_file, bbox_inches="tight")
    plt.close()
    
    print(f"Capacity factors figure successfully saved at '{output_file}'")

def capacity_factor_formatting(
    legend_names,
    highlight_label="PV-MEAS",
):
    """
    Generate colors, linestyles, and line widths for capacity factor plots.

    Parameters:
        data_sim_meas (pd.DataFrame): DataFrame containing all simulation and measurement columns.
        user_color_mapping (dict, optional): Custom color mapping to override defaults.
        user_linestyle_mapping (dict, optional): Custom linestyle mapping to override defaults.
        highlight_label (str, optional): Label that should be highlighted with a thicker line width.

    Returns:
        tuple: (legend_names, colors_CF, linestyles_CF, line_widths_CF)
    """

    color_mapping = style_config.COLOR_MAPPING_CF
    linestyle_mapping = style_config.LINESTYLE_MAPPING_CF

    default_color = style_config.DEFAULT_COLOR_CF
    default_linestyle = style_config.DEFAULT_LINESTYLE_CF

    # ------------------------------------------------------------------------------------
    # Apply formatting rules
    # ------------------------------------------------------------------------------------
    colors_CF = []
    linestyles_CF = []
    line_widths_CF = []

    for name in legend_names:
        # Color
        color_CF = next(
            (color for keyword, color in color_mapping.items() if keyword in name),
            default_color,
        )
        colors_CF.append(color_CF)

        # Linestyle
        linestyle_CF = next(
            (style for keyword, style in linestyle_mapping.items() if keyword in name),
            default_linestyle,
        )
        linestyles_CF.append(linestyle_CF)

        # Line width
        line_width = 3 if highlight_label in name else 2
        line_widths_CF.append(line_width)

    # ------------------------------------------------------------------------------------
    # Return the full style set
    # ------------------------------------------------------------------------------------
    return colors_CF, linestyles_CF, line_widths_CF


#----------------- Scatter measured vs simulation -------------------

def plot_scatter_comparison(data_sim_meas, location_name, year, custom_cmap, output_dir_timeseries):
    """
    Plot scatter plots comparing measured vs simulated data for multiple simulation columns.

    Parameters:
        filtered_data_scat (pd.DataFrame): DataFrame with filtered simulation data (rows where measured data != 0).
        measured_data_scat (pd.Series): Series with measured data.
        sim_columns (list): List of simulation column names to plot.
        location_name (str): Name of the location.
        custom_cmap: Colormap for KDE plot.
        output_dir_timeseries (str): Directory to save the scatter plot figure.
    """
    # Filter columns for the current location
    loc_data = data_sim_meas[
        [col for col in data_sim_meas.columns if col.startswith(location_name)]
    ]

    # Identify 'PV-MEAS' column as the real (measured) data
    meas_column = next((col for col in loc_data.columns if "PV-MEAS" in col), None)
    if meas_column is None:
        print(f"Skipping {location_name}{year}: 'PV-MEAS' column missing.")

    # Identify simulations columns with only zero values
    valid_columns = [meas_column] + [
        col
        for col in loc_data.columns
        if col != meas_column and not loc_data[col].eq(0).all()
    ]

    # Filter data to exclude rows with zero values in the measured data column and simulation columns with only zero values (used for scatter plot only)
    filtered_data_scat = loc_data[loc_data[meas_column] != 0]
    filtered_data_scat = filtered_data_scat[valid_columns]
    measured_data_scat = filtered_data_scat[meas_column].squeeze()  # Measured

    #Identify simulation columns only
    sim_columns = [col for col in valid_columns if col != meas_column]

    # Determine grid layout for subplots
    cols = int(math.ceil(math.sqrt(len(sim_columns))))
    rows = int(math.ceil(len(sim_columns) / cols))
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 6, rows * 6))
    axs = axs.flatten() if len(sim_columns) > 1 else [axs]

    for idx, sim_col in enumerate(sim_columns):
        ax = axs[idx]
        simulated_data_scat = filtered_data_scat[sim_col].squeeze()

        # Scatter of simulated vs measured
        sns.scatterplot(
            x=measured_data_scat,
            y=simulated_data_scat,
            alpha=0.5,
            edgecolor="w",
            linewidth=0.5,
            label="Simulated data",
            s=15,
            ax=ax,
        )

        # KDE plot for density
        sns.kdeplot(
            x=measured_data_scat,
            y=simulated_data_scat,
            fill=True,
            cmap=custom_cmap,
            levels=20,
            ax=ax,
        )

        # Diagonal line y=x (perfect match)
        sns.scatterplot(
            x=measured_data_scat,
            y=measured_data_scat,
            alpha=0.5,
            edgecolor="w",
            color="r",
            linewidth=0.5,
            label="Measured data",
            s=15,
            ax=ax,
        )

        ax.set_title(f"{location_name}{year} - {sim_col.split()[1]}", fontsize=20)
        ax.set_xlabel("Measured Data", fontsize=18)
        ax.set_ylabel("Simulated Data", fontsize=18)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.grid(True)
        ax.legend(scatterpoints=1, markerscale=2, fontsize=12, loc="upper left")

    # Remove any empty subplots
    for j in range(idx + 1, len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    output_file = os.path.join(output_dir_timeseries, f"{location_name}{year}_scatterplot.png")
    plt.savefig(output_file)
    plt.close()
    print(f"Scatter plot figure successfully saved at '{output_file}'")

#------------------ Plot for error metrics -----------------

def plot_error_metrics(location_name, year, mean_diff_results, mae_results, rmse_results, plot_palette, legend_names, output_dir_timeseries):
    """
    Plot error metrics (Mean Difference, MAE, RMSE) for a location.

    Parameters:
        location_name (str): Name of the location.
        year (str): Year of the simulation.
        mean_diff_results (list of dicts): List of mean difference results with keys "Location", "Tool", "Mean Difference (%)".
        mae_results (list of dicts): List of MAE results with keys "Location", "Tool", "MAE (%)".
        rmse_results (list of dicts): List of RMSE results with keys "Location", "Tool", "RMSE (%)".
        plot_palette (dict): Dictionary mapping tools to colors for the bar plots.
        legend_names (list): List of tools to include in the legend.
        output_dir_timeseries (str): Directory to save the combined metrics figure.
    """

    def add_labels(ax):
        """Add labels on top of bars."""
        for p in ax.patches:
            height = p.get_height()
            if abs(height) > 1e-3:  # Ignore near-zero bars
                va = "bottom" if height >= 0 else "bottom"
                y_offset = 5 if height >= 0 else 16
                ax.annotate(
                    f"{height:.1f}",
                    (p.get_x() + p.get_width() / 2., height),
                    ha="center",
                    va=va,
                    xytext=(0, y_offset),
                    textcoords="offset points",
                    fontsize=11,
                )

    # Convert results to DataFrames
    mean_diff_df = pd.DataFrame(mean_diff_results)
    mae_df = pd.DataFrame(mae_results)
    rmse_df = pd.DataFrame(rmse_results)

    # Sort by Location
    mean_diff_df.sort_values("Location", inplace=True)
    mae_df.sort_values("Location", inplace=True)
    rmse_df.sort_values("Location", inplace=True)

    # Define order for hue
    tool_order = list(plot_palette.keys())

    # Create figure with 3 subplots
    fig, axes = plt.subplots(3, 1, figsize=(16, 15))
    tick_font_size = 16

    # Mean Difference
    sns.barplot(
        x="Location", y="Mean Difference (%)", hue="Tool",
        data=mean_diff_df, palette=plot_palette, hue_order=tool_order, ax=axes[0]
    )
    axes[0].set_ylabel("Annual average \nCF difference (%)", fontsize=20)
    axes[0].tick_params(axis="both", labelsize=tick_font_size)
    axes[0].set_axisbelow(True)
    axes[0].grid(True, axis="y")
    axes[0].set_xlabel("")
    axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}"))
    axes[0].get_legend().remove()
    axes[0].set_ylim(-0.4, 4)
    add_labels(axes[0])

    # MAE
    sns.barplot(
        x="Location", y="MAE (%)", hue="Tool",
        data=mae_df, palette=plot_palette, hue_order=tool_order, ax=axes[1]
    )
    axes[1].set_ylabel("Annual MAE \nof CF (%)", fontsize=20)
    axes[1].tick_params(axis="both", labelsize=tick_font_size)
    axes[1].set_axisbelow(True)
    axes[1].grid(True, axis="y")
    axes[1].set_xlabel("")
    axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}"))
    axes[1].get_legend().remove()
    axes[1].set_ylim(-0.3, 8)
    add_labels(axes[1])

    # RMSE
    sns.barplot(
        x="Location", y="RMSE (%)", hue="Tool",
        data=rmse_df, palette=plot_palette, hue_order=tool_order, ax=axes[2]
    )
    axes[2].set_ylabel("Annual RMSE of CF (%)", fontsize=20)
    axes[2].tick_params(axis="both", labelsize=tick_font_size)
    axes[2].set_axisbelow(True)
    axes[2].grid(True, axis="y")
    axes[2].set_xlabel("Location", fontsize=20)
    axes[2].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}"))
    axes[2].get_legend().remove()
    axes[2].set_ylim(-0.3, 15)
    add_labels(axes[2])

    # Adjust layout
    plt.tight_layout()

    # Create one combined legend at the bottom
    handles, labels = axes[2].get_legend_handles_labels()
    filtered_handles_labels = [(h, l) for h, l in zip(handles, labels) if l in legend_names]
    if filtered_handles_labels:
        filtered_handles, filtered_labels = zip(*filtered_handles_labels)
    else:
        filtered_handles, filtered_labels = [], []

    fig.legend(
        filtered_handles, filtered_labels,
        loc="lower center", ncol=len(tool_order), bbox_to_anchor=(0.5, -0.05),
        fontsize=16, title_fontsize=18, frameon=False
    )

    # Save figure
    output_file = os.path.join(output_dir_timeseries, f"{location_name}{year}_Errors_Analysis.png")
    plt.savefig(output_file, bbox_inches="tight")
    plt.close()
    print(f"Combined error analysis figure successfully saved at '{output_file}'")

#-------------------- High resolution figure -------------------------------

def plot_high_res_days(df_clear, df_cloudy, location_name, legend_names_high_res, colors_high_res,
                        linestyles_high_res, line_widths_high_res, output_dir_timeseries):
    """
    Plot high-resolution PV data for Clear Sky and Cloudy Sky days side by side.

    Parameters:
        df_clear (pd.DataFrame): DataFrame with clear sky day data.
        df_cloudy (pd.DataFrame): DataFrame with cloudy sky day data.
        location_name (str): Name of the location.
        legend_names_high_res (list): List of time series/legend names.
        colors_high_res (list): List of colors corresponding to the legends.
        linestyles_high_res (list): List of line styles for the legends.
        line_widths_high_res (list): List of line widths for the legends.
        output_dir_timeseries (str): Directory to save the figure.
    """

    fig, axs = plt.subplots(1, 2, figsize=(20, 4))  # Two subplots side by side

    all_handles = []
    all_labels = []

    # Plot Clear Sky Day
    for col in df_clear.columns:
        if col.split()[1] in legend_names_high_res:
            idx = legend_names_high_res.index(col.split()[1])
            (line,) = axs[0].plot(
                df_clear.index,
                df_clear[col],
                label=legend_names_high_res[idx],
                color=colors_high_res[idx],
                linestyle=linestyles_high_res[idx],
                linewidth=line_widths_high_res[idx]
            )
            if line.get_label() not in all_labels:
                all_handles.append(line)
                all_labels.append(line.get_label())
    axs[0].set_title(f"{location_name} - Clear Sky Day", fontsize=20)
    axs[0].set_xlabel("Number of timesteps", fontsize=16)
    axs[0].set_ylabel("Normalized power profiles", fontsize=16)
    axs[0].set_xlim(0, len(df_clear))
    axs[0].set_ylim(0, 1)
    axs[0].grid(True)

    # Plot Cloudy Sky Day
    for col in df_cloudy.columns:
        if col.split()[1] in legend_names_high_res:
            idx = legend_names_high_res.index(col.split()[1])
            (line,) = axs[1].plot(
                df_cloudy.index,
                df_cloudy[col],
                label=legend_names_high_res[idx],
                color=colors_high_res[idx],
                linestyle=linestyles_high_res[idx],
                linewidth=line_widths_high_res[idx]
            )
            if line.get_label() not in all_labels:
                all_handles.append(line)
                all_labels.append(line.get_label())
    axs[1].set_title(f"{location_name} - Cloudy Sky Day", fontsize=20)
    axs[1].set_xlabel("Number of timesteps", fontsize=16)
    axs[1].set_ylabel("Normalized power profiles", fontsize=16)
    axs[1].set_xlim(0, len(df_cloudy))
    axs[1].set_ylim(0, 1)
    axs[1].grid(True)

    # Adjust tick sizes
    for ax in axs:
        ax.tick_params(axis="y", labelsize=15)
        ax.tick_params(axis="x", labelsize=15)

    # Add single legend at bottom
    max_items_per_row = 9
    ncol = min(len(all_labels), max_items_per_row)
    fig.legend(
        all_handles,
        all_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=ncol,
        fontsize=15
    )

    plt.tight_layout()
    output_file = os.path.join(output_dir_timeseries, f"{location_name}_highres_clear_vs_cloudy.png")
    plt.savefig(output_file, bbox_inches="tight")
    plt.close()
    print(f"High-resolution clear vs cloudy sky figure saved at '{output_file}'")

# Formatting
def highres_plot_formatting(
    legend_names_high_res,
    highlight_label="PV-MEAS",
):
    """
    Generate legend names, colors, linestyles, and line widths for
    high-resolution (clear sky and cloudy sky) PV plots.

    Parameters:
        clear_sky_df (pd.DataFrame): DataFrame for the clear-sky high-res data.
        cloudy_sky_df (pd.DataFrame): DataFrame for the cloudy-sky high-res data.
        highlight_label (str, optional): Label that should be highlighted with a thicker line width.

    Returns:
        tuple: (legend_names_high_res, colors_high_res, linestyles_high_res, line_widths_high_res)
    """

    # ------------------------------------------------------------------------------------
    # Define default color and linestyle mappings for high-res plots
    # ------------------------------------------------------------------------------------
    color_mapping = style_config.COLOR_MAPPING_HIGHRES
    linestyle_mapping = style_config.LINESTYLE_MAPPING_HIGHRES

    # Default fallback values
    default_color = style_config.DEFAULT_COLOR_HIGHRES
    default_linestyle = style_config.DEFAULT_LINESTYLE_HIGHRES

    # ------------------------------------------------------------------------------------
    # Apply formatting for each legend entry
    # ------------------------------------------------------------------------------------
    colors_high_res = []
    linestyles_high_res = []
    line_widths_high_res = []

    for name in legend_names_high_res:
        # Color
        color_high_res = next(
            (color for keyword, color in color_mapping.items() if keyword in name),
            default_color,
        )
        colors_high_res.append(color_high_res)

        # Linestyle
        linestyle_high_res = next(
            (style for keyword, style in linestyle_mapping.items() if keyword in name),
            default_linestyle,
        )
        linestyles_high_res.append(linestyle_high_res)

        # Line width (thicker for measured data)
        line_width = 3 if highlight_label == name else 2
        line_widths_high_res.append(line_width)

    # ------------------------------------------------------------------------------------
    # Return all styling elements
    # ------------------------------------------------------------------------------------
    return colors_high_res, linestyles_high_res, line_widths_high_res


# Plot LCOF error bar chart

def plot_LCOF_diff(LCOF_diff_results, plot_palette, location_name, year, H2_end_user_min_load,
                   output_dir_technoeco, legend_names):
    """
    Function to plot LCOF difference for error analysis and save the figure.

    Args:
    LCOF_diff_results (list): List of dictionaries containing LCOF differences for each location and tool.
    plot_palette (dict): Dictionary containing the simulation tools for plotting.
    location_name (str): The location name used for saving the plot.
    H2_end_user_min_load (float): Minimum load for H2 end user, included in the figure filename.
    output_dir_technoeco (str): Directory to save the plot.
    legend_names (list): List of legend names to filter the plot legend

    Returns:
    None
    """
    def add_labels(ax):
        """ Helper function to add labels to the bars in the plot """
        for p in ax.patches:
            height = p.get_height()
            if abs(height) > 1e-3:  # Ignore near-zero bars to prevent "0.0" labels
                if height >= 0:
                    ax.annotate(
                        format(height, ".1f"),
                        (p.get_x() + p.get_width() / 2.0, height),
                        ha="center",
                        va="bottom",
                        xytext=(0, 5),
                        textcoords="offset points",
                        fontsize=11,
                    )
                else:
                    ax.annotate(
                        format(height, ".1f"),
                        (p.get_x() + p.get_width() / 2.0, height),
                        ha="center",
                        va="top",
                        xytext=(0, -5),
                        textcoords="offset points",
                        fontsize=11,
                    )

    # Extract the tool order from the palette (ensures tools are plotted in this specific order)
    tool_order = list(plot_palette.keys())

    # Create dataframe for plotting
    LCOF_diff_df = pd.DataFrame(LCOF_diff_results)
    
    # Sort DataFrames by Location
    LCOF_diff_df.sort_values(by="Location", inplace=True)

    # Compute min and max values with padding
    y_min = LCOF_diff_df["LCOF Difference (%)"].min()
    y_max = LCOF_diff_df["LCOF Difference (%)"].max()
    padding = (y_max - y_min) * 0.3  # 30% padding

    # Ensure zero is always visible on the y-axis
    y_min = min(0, y_min - padding)
    y_max = max(0, y_max + padding)

    # Check if LCOF Difference values are mostly negative
    mostly_negative = np.median(LCOF_diff_df["LCOF Difference (%)"]) < 0

    # Create the figure
    plt.figure(figsize=(10, 6))

    # Define tick font size
    tick_font_size = 16

    # Plot LCOF Difference
    ax = sns.barplot(
        x="Location",
        y="LCOF Difference (%)",
        hue="Tool",
        data=LCOF_diff_df,
        palette=plot_palette,
        hue_order=tool_order,
    )

    # Customize plot
    ax.set_ylabel("LCOF Difference (%) (measured PV vs simulated)", fontsize=20)
    ax.tick_params(axis="both", labelsize=tick_font_size)
    ax.set_axisbelow(True)
    ax.grid(True, axis="y")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}"))
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("")

    # Add labels to the bars
    add_labels(ax)

    # Move x-axis labels above if mostly negative
    if mostly_negative:
        ax.xaxis.set_label_position("top")
        ax.xaxis.tick_top()
        plt.subplots_adjust(top=0.85)

    # Filter legend to only show labels in `legend_names` if provided
    if legend_names:
        handles, labels = ax.get_legend_handles_labels()
        filtered_handles_labels = [(h, l) for h, l in zip(handles, labels) if l in legend_names]
        filtered_handles, filtered_labels = (
            zip(*filtered_handles_labels) if filtered_handles_labels else ([], [])
        )
    else:
        filtered_handles, filtered_labels = ax.get_legend_handles_labels()

    # Add filtered legend below the figure
    ax.legend(
        filtered_handles,
        filtered_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=3,
        fontsize=16,
        title_fontsize=18,
        frameon=False,
    )

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        os.path.join(
            output_dir_technoeco,
            f"{location_name}{year}_LCOF_diff_flex[{H2_end_user_min_load}-1].png",
        )
    )
    
    # Print confirmation
    print(
        f"LCOF difference figure successfully generated in the '{output_dir_technoeco}' folder for {location_name}"
    )
    
    # Close the plot to free up memory
    plt.close()



