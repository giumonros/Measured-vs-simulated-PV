simeasren.pv_simulation.load_pv_set_up
======================================

.. py:module:: simeasren.pv_simulation.load_pv_set_up


Functions
---------

.. autoapisummary::

   simeasren.pv_simulation.load_pv_set_up.load_pv_setup_from_meas_file


Module Contents
---------------

.. py:function:: load_pv_setup_from_meas_file(location_name: str) -> dict

   Load PV plant setup parameters from the measured data Excel file (in data/measured_PV)

   This function reads the `"PV_plant_setup"` sheet from the measured PV data Excel
   file for a given location and returns the contents as a dictionary, with the
   Excel sheet's `"Parameter"` column as keys and the `"Value"` column as values.

   :param location_name: Name of the location/site corresponding to the Excel file (without extension),
                         e.g., `"Turin"`. The function expects the file to exist in:
                         ```
                         data/measured_PV/{location_name}.xlsx
                         ```
   :type location_name: str

   :returns: Dictionary containing PV plant setup parameters. Keys correspond to parameter
             names (from the `"Parameter"` column in Excel), and values are the corresponding
             setup values.
   :rtype: dict

   :raises FileNotFoundError: If the measured PV Excel file for the specified location does not exist.

   .. rubric:: Notes

   - The Excel sheet must be named `"PV_plant_setup"` with columns `"Parameter"` and `"Value"`.
   - Typical use includes retrieving metadata such as plant capacity, inverter specs,
     orientation, or other site-specific configuration values for plotting or modeling.

   .. rubric:: Examples

   >>> from simeasren import load_pv_setup_from_meas_file
   >>> parameters = load_pv_setup_from_meas_file("Almeria")
   >>> parameters["System loss"]
   9.75
   >>> parameters["PV technology"]
   'crystSi'


