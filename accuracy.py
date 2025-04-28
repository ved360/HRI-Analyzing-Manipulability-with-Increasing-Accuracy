import csv
import math
import os
import matplotlib.pyplot as plt

# Spiral parameters (same as experiment)
a = 10
b = 20
WIDTH, HEIGHT = 800, 800

# Compute Euclidean distance
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Generate spiral points
def generate_spiral(a, b, num_points=200):
    points = []
    for i in range(num_points):
        theta = i * 0.1
        r = a + b * theta
        x = r * math.cos(theta) + WIDTH // 2
        y = r * math.sin(theta) + HEIGHT // 2
        points.append((x, y))
    return points

# Compute accuracy
def compute_accuracy(trace_points, spiral_points, max_distance=100):
    if not trace_points:
        return 0.0

    total_distance = 0
    for pt in trace_points:
        x, y = pt
        closest_dist = min(euclidean_distance((x, y), sp) for sp in spiral_points)
        total_distance += closest_dist

    mean_distance = total_distance / len(trace_points)
    accuracy = max(0, 100 * (1 - mean_distance / max_distance))
    return round(accuracy, 2)

# Load trace points from CSV
def load_trace_data(filepath):
    trace_points = []
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                x = float(row["x"])
                y = float(row["y"])
                trace_points.append((x, y))
            except:
                continue
    return trace_points

# --- Main Logic ---
folder = "trace_data"
spiral_points = generate_spiral(a, b)

trial_accuracies = []

# Process all CSV files in the folder
for filename in sorted(os.listdir(folder)):
    if filename.endswith(".csv") and "trial_" in filename:
        filepath = os.path.join(folder, filename)
        trace_points = load_trace_data(filepath)
        accuracy = compute_accuracy(trace_points, spiral_points)
        
        # Extract trial number from filename
        try:
            trial_num = int(filename.split("trial_")[1].split("_")[0])
        except:
            trial_num = len(trial_accuracies) + 1
        
        trial_accuracies.append((trial_num, accuracy))
        print(f"Trial {trial_num}: Accuracy = {accuracy}%")

# Sort by trial number
trial_accuracies.sort(key=lambda x: x[0])

# Plotting
trial_nums = [t[0] for t in trial_accuracies]
accuracies = [t[1] for t in trial_accuracies]

plt.figure(figsize=(10, 6))
plt.plot(trial_nums, accuracies, marker='o', linestyle='-')
plt.xlabel("Trial Number")
plt.ylabel("Accuracy (%)")
plt.title("Spiral Tracing Accuracy Over Trials")
plt.grid(True)
plt.xticks(trial_nums)
plt.tight_layout()
plt.show()