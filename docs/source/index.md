# Simeasren documentation

Welcome to the Simeasren documentation.

This package has been created based on the work presented in this [article](https://doi.org/10.1016/j.rser.2024.115044)

The aim of this package is to facilate the data sharing of measured PV profiles, compare measured and simulated PV power production data, and
analyse the influence of using measured or simulated PV power data for e-fuel techno-economic assessments. 

The data used to run this package are:
- Measured data from real photovoltaic (PV) plants (``src/simeasren/data/measured_PV``)
- Hydrogen based e-fuel techno-economic parameters (``src/simeasren/data/techno_economic_assessment``)

This package contains:
- Functions for extracting PV power production data from PVGIS and Renewables.ninja
- Data analysis tools and graphs to compare measured and simulated data
- A simple e-fuel techno-economic assessment to study the error propagation

The installation tutorial is available [here](installation.md)

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

