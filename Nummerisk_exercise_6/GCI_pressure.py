import pandas as pd
import numpy as np
from scipy.optimize import fsolve

# Function to parse the p_rgh file (OpenFOAM simulation results)
def parse_p_rgh_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extract probe locations (lines that start with '#')
    probe_locations = [line for line in lines if line.startswith("# Probe")]
    
    # Extract data lines (lines that don't start with '#')
    data_lines = [line for line in lines if not line.startswith("#")]

    # Create arrays to store the time and probe data
    times = []
    probes_data = {f"Probe_{i}": [] for i in range(len(probe_locations))}

    # Split the data lines into time and probe data
    for line in data_lines:
        values = line.split()
        times.append(float(values[0]))  # First value is time
        for i, probe_value in enumerate(values[1:]):
            probes_data[f"Probe_{i}"].append(float(probe_value))  # Remaining values are probe data

    # Convert to DataFrame
    df = pd.DataFrame({
        "Time": times,
        **probes_data
    })

    return df, probe_locations

# Function to extract the pressure values at 2 seconds
def extract_pressure_at_time(df, target_time=2.0):
    # Find the closest time index to the target time (e.g., 2 seconds)
    time_diff = (df['Time'] - target_time).abs()
    closest_time_index = time_diff.idxmin()
    
    # Extract the pressure values at that time for all probes
    pressure_at_time = df.iloc[closest_time_index, 1:]  # Exclude the 'Time' column
    return pressure_at_time

# Define the paths for the three cases (coarse, medium, fine)
cases = {
    "coarse": "/home/eliasmt/OpenFOAM/eliasmt-11/run/exercise_6/damBreak_course/postProcessing/probes1/0/p_rgh",
    "medium": "/home/eliasmt/OpenFOAM/eliasmt-11/run/exercise_6/damBreak_medium/postProcessing/probes1/0/p_rgh",
    "fine": "/home/eliasmt/OpenFOAM/eliasmt-11/run/exercise_6/damBreak_fine/postProcessing/probes1/0/p_rgh"
}

# Initialize arrays to store the pressure values for each case
pressure_course = []
pressure_medium = []
pressure_fine = []

# Loop over each case and extract the pressure values at 2 seconds
for case, path in cases.items():
    df, probe_locations = parse_p_rgh_file(path)
    
    # Extract the pressure values at 2 seconds
    pressure_values = extract_pressure_at_time(df, target_time=2.0)
    
    # Store the pressure values in the corresponding array
    if case == "coarse":
        pressure_course = pressure_values.values
    elif case == "medium":
        pressure_medium = pressure_values.values
    elif case == "fine":
        pressure_fine = pressure_values.values



# Number of cells for each mesh (replace with your actual values)
num_cells = [20395, 45839, 105666]  # Coarse, Medium, Fine

# Refinement ratios (r_c for coarse-to-medium and r_f for medium-to-fine)
r_c = (num_cells[1] / num_cells[0]) ** (1/3)  # Cubic root for 3D
r_f = (num_cells[2] / num_cells[1]) ** (1/3)  # Cubic root for 3D

# Function to calculate p for each point
def calculate_order_of_convergence(Xh, rc, rf):
    # Xh contains the coarse, medium, and fine values for a particular point
    a = (Xh[1] - Xh[0]) / (Xh[2] - Xh[1])
    s = np.sign(a)

    # Define the function for solving p
    def f(p):
        return p - np.abs(np.log(np.abs(a)) + np.log((rf**p - s) / (rc**p - s))) / np.log(rf)
    
    # Solve for p
    p = fsolve(f, 1)[0]
    return p

# Arrays containing pressure values for the 8 points after 2s
# pressure_course, pressure_medium, pressure_fine are already defined from the previous step

# Initialize an array to store the order of convergence for each of the 8 points
p_values = []

# Loop over each point (there are 8 points)
for i in range(8):
    # Extract pressure values for the i-th point across the three grids
    Xh = np.array([pressure_course[i], pressure_medium[i], pressure_fine[i]])
    
    # Calculate the order of convergence for this point
    p = calculate_order_of_convergence(Xh, r_c, r_f)
    
    # Store the result
    p_values.append(p)

# Convert to numpy array for further calculations if needed
p_values = np.array(p_values)

# Print the order of convergence for each point
print("Order of convergence (p) for each point:")
for i, p in enumerate(p_values):
    print(f"Point {i+1}: p = {p}")


# Print the results
print("Pressure values at 2 seconds for coarse case:", pressure_course)
print("Pressure values at 2 seconds for medium case:", pressure_medium)
print("Pressure values at 2 seconds for fine case:", pressure_fine)

