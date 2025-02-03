import os
import re
import numpy as np
import matplotlib.pyplot as plt

def parse_stats(file_path):
    """
    Parse a gem5 stats.txt file into a dictionary mapping stat names to values.
    Lines that are empty or start with '#' are ignored.
    The first token is assumed to be the stat key and the second token its value.
    """
    stats = {}
    with open(file_path, 'r') as f:
        for line in f:
            # Skip empty lines and lines that start with '#'
            if line.strip() == '' or line.strip().startswith('#'):
                continue

            # Remove inline comments (anything after a '#')
            line_no_comment = line.split('#')[0].strip()
            if not line_no_comment:
                continue

            # Split the remaining line into tokens; expect at least key and value.
            tokens = line_no_comment.split()
            if len(tokens) < 2:
                continue

            key = tokens[0]
            value_str = tokens[1]
            # Try converting the value to a float; if not, keep as string.
            try:
                value = float(value_str)
            except ValueError:
                value = value_str
            stats[key] = value
    return stats

# --------------------------
# Configuration
# --------------------------

# Base directory where the run subdirectories are located.
base_dir = "chetanout"
# List of subdirectory names (each containing a stats.txt file).
run_dirs = ["1", "2", "3"]

# The metrics we want to extract and compare.
metrics = ['simSeconds', 'system.cpu.numCycles', 'simInsts', 'system.cpu.ipc']

# --------------------------
# Data Extraction
# --------------------------

# Create a dictionary mapping run name to its parsed stats.
data = {}
for run in run_dirs:
    stats_path = os.path.join(base_dir, run, "stats.txt")
    if os.path.exists(stats_path):
        data[run] = parse_stats(stats_path)
    else:
        print(f"Warning: {stats_path} does not exist!")
        data[run] = {}

# For each metric, gather values across runs.
# The structure will be: values[metric] = [value_in_run1, value_in_run2, value_in_run3]
values = {metric: [] for metric in metrics}
for metric in metrics:
    for run in run_dirs:
        # If the metric is missing, default to 0.
        values[metric].append(data[run].get(metric, 0))

# --------------------------
# Plotting
# --------------------------
# We will create a grouped bar chart.
n_metrics = len(metrics)
n_runs = len(run_dirs)

# x locations for groups (one group per metric)
x = np.arange(n_metrics)
bar_width = 0.2

fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars for each run with an offset.
for i, run in enumerate(run_dirs):
    # Offset each run's bars by bar_width * i, centering the group.
    offsets = x - (bar_width * n_runs) / 2 + i * bar_width + bar_width/2
    # Extract the values for this run across all metrics.
    run_values = [values[metric][i] for metric in metrics]
    ax.bar(offsets, run_values, width=bar_width, label=f"Run {run}")

# Labeling and formatting
ax.set_xlabel("Metric")
ax.set_ylabel("Value")
ax.set_title("Comparison of Selected gem5 Simulation Metrics")
ax.set_xticks(x)
ax.set_xticklabels(metrics, rotation=45, ha='right')
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
