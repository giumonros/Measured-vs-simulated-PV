import subprocess
import sys
import os

#---------------User defined----------------
location = "Almeria" # Site name for the analysis (must be existing in the "measured data folder")
years = "All years" #Select a specific year for the analysis (otherwise all years in the measured folder will be used)
H2_end_user_min_load = "0" # Hydrogen end-user flexibility for the techno-economic assessment (minimal load between 0 and 1)
solver = "GUROBI_CMD" # Or HiGHS. To use other solvers modify the file '3-Techno-eco_assessment.py'
renewablesninja_token = "your_token_here" # Replace with your Renewables.ninja token to be able to use their API, e.g. "12345678910"

# List of scripts to run (in order)
#scripts = ["1-PV_simulation_download.py"] 
#scripts = ["2-PV_Timeseries_analysis.py"] 
#scripts = ["2-PV_Timeseries_analysis.py", "3-H2_Technoeco_assessment.py"]
scripts = ["1-PV_simulation_download.py", "2-PV_Timeseries_analysis.py", "3-H2_Technoeco_assessment.py"]

#-------------------------------------------

#Run all scripts from the list one by one
for script in scripts:
    script_path = os.path.join("Python scripts", script)  # Construct full pathto the folder containing the scripts
    print(f"\n=== Running {script} ===")
    # Run script and stream output live
    process = subprocess.Popen([sys.executable, script_path, location, years, H2_end_user_min_load, solver, renewablesninja_token], stdout=sys.stdout, stderr=sys.stderr, text=True)
    process.wait()  # 
