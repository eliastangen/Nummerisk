import pandas as pd
import matplotlib.pyplot as plt

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

# Read the experimental data from the Excel file
def read_experimental_data(exp_file):
    exp_df = pd.read_excel(exp_file)
    exp_df['Time (s)'] += 0.5
    return exp_df

# Function to plot pressure vs time for each probe
def plot_pressure_vs_time(df, exp_df):
    # Extract the probe columns from the experimental data
    probe_columns = exp_df.columns[1:]  # Exclude 'Time'

    # Create a plot for each probe
    for i, probe in enumerate(probe_columns):
        plt.figure(figsize=(10, 6))
        
        # Plot the simulation data
        plt.plot(df['Time'], df[f"Probe_{i}"], label=f"Simulation Probe {i+1}")
        
        # Plot the experimental data
        plt.plot(exp_df['Time (s)'], exp_df[probe], label=f"Experimental {probe}", linestyle='--')

        # Add titles and labels
        plt.title(f'Pressure vs. Time at {probe}')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [Pa]')
        plt.ylim([-100, 5000])  # Adjust the y-axis if needed (based on your data)
        plt.legend(loc='upper right')
        plt.grid(True)

        # Show the plot
        plt.show()

# Path to the p_rgh file and experimental data file
p_rgh_file_path = '/home/eliasmt/OpenFOAM/eliasmt-11/run/exercise_6/damBreak_16_10_24/postProcessing/probes1/0/p_rgh'
exp_file_path = '/home/eliasmt/OpenFOAM/eliasmt-11/run/exercise_6/damBreak_16_10_24/exp_data.xls'  # The experimental data Excel file

# Parse the p_rgh file (OpenFOAM simulation data) and the experimental data
df, probe_locations = parse_p_rgh_file(p_rgh_file_path)
exp_df = read_experimental_data(exp_file_path)

# Plot the pressure vs. time for each probe
plot_pressure_vs_time(df, exp_df)
