import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ==========================================================
# User-editable plot style configuration file
# ==========================================================

# Color mappings for capacity factor (CF) plots
COLOR_MAPPING_CF = {
    "PV-MEAS": "red",
    "MERRA2": "blue",
    "SARAH3": "sienna",
    "SARAH2": "orange",
    "SARAH": "gold",
    "ERA5": "green",
    "SIM": "purple",
}
DEFAULT_COLOR_CF = "black"

# Linestyle mappings for capacity factor (CF) plots
LINESTYLE_MAPPING_CF = {
    "PV-MEAS": "-",
    "PG2": "--",
    "PG3": "-",
    "RN": ":",
    "CR": "-.",
}
DEFAULT_LINESTYLE_CF = "-."


# Color mappings for high-resolution (clear/cloudy) plots
COLOR_MAPPING_HIGHRES = {
    "PV-MEAS_high_resolution": "red",
    "PV-MEAS": "black",
    "MERRA2": "blue",
    "SARAH3": "sienna",
    "SARAH2": "orange",
    "SARAH": "gold",
    "ERA5": "green",
    "SIM": "purple",
}
DEFAULT_COLOR_HIGHRES = "darkgreen"

# Linestyle mappings for high-resolution (clear/cloudy) plots
LINESTYLE_MAPPING_HIGHRES = {
    "PV-MEAS_high_resolution": "-",
    "PV-MEAS": "-",
    "PG2": "--",
    "PG3": "-",
    "RN": ":",
    "CR": "-.",
}
DEFAULT_LINESTYLE_HIGHRES = "-."

# Plot palette for metric error plot
PLOT_PALETTE = {
    "RN-MERRA2": "blue",
    "RN-SARAH": "dodgerblue",
    "PG2-SARAH": "gold",
    "PG2-SARAH2": "orange",
    "PG3-SARAH3": "sienna",
    "PG2-ERA5": "limegreen",
    "PG3-ERA5": "green",
    "SIM-SELF1": "purple"
}

# Custom colormap for scatter plots
jet = plt.cm.jet
colors = jet(np.linspace(0, 1, 256))
for i in range(colors.shape[0]): colors[i, -1] = np.linspace(0.4, 0.8, 256)[i]

CUSTOM_CMAP = LinearSegmentedColormap.from_list("jet_custom", colors)
