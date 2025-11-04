# Simeasren documentation

Welcome to the Simeasren documentation. 

The installation tutorial is available [here](installation.md).

Examples of use can be found [here](https://github.com/giumonros/Measured-vs-simulated-PV/tree/main/examples) and in the rest of the documentation.

This package has been created based on the work presented in this [article](https://doi.org/10.1016/j.rser.2024.115044).

The aim of this package is to facilate the data sharing of measured PV profiles, compare measured and simulated PV power production data from different tools, and
analyse the influence of using measured or simulated PV power data for e-fuel techno-economic assessments. 

![png](/img/Introduction_methods.png)
*Figure taken from [this paper](https://doi.org/10.1016/j.rser.2024.115044)*

The data used to run this package are:
- [Measured data](https://github.com/giumonros/Measured-vs-simulated-PV/tree/main/src/simeasren/data/measured_PV) from real photovoltaic (PV) plants
- Hydrogen based e-fuel [techno-economic parameters](https://github.com/giumonros/Measured-vs-simulated-PV/tree/main/src/simeasren/data/techno_economic_assessment)

This package contains:
- Functions for extracting PV power production data from PVGIS and Renewables.ninja [here](pv_simulation.md) 
- Data analysis tools and graphs to compare measured and simulated data [here](pv_analysis.md)
- A simple e-fuel techno-economic assessment to study the error propagation [here](error_propagation_analysis.md)

```{toctree}
:maxdepth: 2
:caption: Simeasren
:hidden:

installation
pv_measured
pv_simulation
pv_analysis
error_propagation_analysis
api/index

