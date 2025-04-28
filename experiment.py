import pygame
import csv
import os
from datetime import datetime
import math
import serial
import threading

ser = serial.Serial('COM9', 9600, timeout=0.1)
encoder_data = ["", ""]

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spiral Tracing Experiment")
clock = pygame.time.Clock()

# Output Folder
if not os.path.exists("trace_data"):
    os.makedirs("trace_data")

# Constants
FONT = pygame.font.SysFont(None, 36)
BLUE = (173, 239, 209)
BLACK = (0, 32, 63)
RED = (255, 0, 0)
TRIAL_DURATION = 10000  # in milliseconds
COUNTDOWN_DURATION = 3000  # in milliseconds

# Spiral Parameters
a = 10  # Start radius
b = 20  # Rate of increase in spiral radius

# Experiment States
WAIT_FOR_ENTER = 0
COUNTDOWN = 1
RECORDING = 2

state = WAIT_FOR_ENTER
trial = 50
trace_points = []
trial_start_time = 0
countdown_start_time = 0

# Compute Euclidean distance
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Compute accuracy based on average distance from ideal spiral
def compute_accuracy(trace_points, spiral_points, max_distance=100):
    if not trace_points:
        return 0.0

    total_distance = 0
    for pt in trace_points:
        x, y = pt[0], pt[1]
        closest_dist = min(euclidean_distance((x, y), sp) for sp in spiral_points)
        total_distance += closest_dist

    mean_distance = total_distance / len(trace_points)
    accuracy = max(0, 100 * (1 - mean_distance / max_distance))  # Clamp to [0, 100]
    return round(accuracy, 2)


# Background thread to update encoder data
def read_serial():
    global encoder_data
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if "Encoder 1:" in line and "Encoder 2:" in line:
                parts = line.split("\t")
                deg1 = parts[0].split("Encoder 1: ")[1]
                deg2 = parts[1].split("Encoder 2: ")[1]
                encoder_data = [deg1, deg2]
        except:
            continue

# Start the thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()


# Save function
def save_trace(points, trial):
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"trace_data/trial_{trial}_{now}.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["x", "y", "timestamp", "encoder_1_deg", "encoder_2_deg"])
        for x, y, t, e1, e2 in points:
            writer.writerow([x, y, t, e1, e2])
    print(f"Saved trial {trial} to {filename}")


# Generate Spiral Points (polar to cartesian conversion)
def generate_spiral(a, b, num_points=200):
    points = []
    for i in range(num_points):
        theta = i * 0.1  # Angle increment
        r = a + b * theta  # Radius formula
        x = r * math.cos(theta) + WIDTH // 2  # Convert to Cartesian coordinates
        y = r * math.sin(theta) + HEIGHT // 2
        points.append((x, y))
    return points

# --- Main Loop ---
running = True
spiral_points = generate_spiral(a, b)

while running:
    screen.fill(BLUE)

    # Draw the continuous spiral by connecting the points
    for i in range(1, len(spiral_points)):
        pygame.draw.line(screen, BLACK, spiral_points[i-1], spiral_points[i], 10)

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif state == WAIT_FOR_ENTER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                countdown_start_time = pygame.time.get_ticks()
                state = COUNTDOWN

    current_time = pygame.time.get_ticks()

    if state == COUNTDOWN:
        elapsed = current_time - countdown_start_time
        if elapsed < COUNTDOWN_DURATION:
            # Blur simulation: draw semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)  # Transparency level
            overlay.fill(BLUE)
            screen.blit(overlay, (0, 0))

            # Countdown number
            countdown_number = 3 - elapsed // 1000
            large_font = pygame.font.SysFont(None, 120)
            countdown_msg = large_font.render(str(countdown_number), True, BLACK)

            # Slight bounce effect
            scale = 1.2 + 0.1 * (elapsed % 500) / 500
            countdown_msg = pygame.transform.rotozoom(countdown_msg, 0, scale)

            # Centered placement
            rect = countdown_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(countdown_msg, rect)
        else:
            state = RECORDING
            trace_points = []
            trial_start_time = pygame.time.get_ticks()

    elif state == RECORDING:
        elapsed = current_time - trial_start_time
        remaining = max(0, (TRIAL_DURATION - elapsed) // 1000)
        time_msg = FONT.render(f"Time left: {remaining}s", True, BLACK)
        screen.blit(time_msg, (WIDTH - 200, 20))

        # Draw user trace
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            t = pygame.time.get_ticks() - trial_start_time
            e1, e2 = encoder_data  # From background thread
            trace_points.append((x, y, t, e1, e2))


            # Draw continuous path
            if len(trace_points) > 1:
                pygame.draw.lines(screen, RED, False, [(pt[0], pt[1]) for pt in trace_points], 10)


        if elapsed >= TRIAL_DURATION:
            save_trace(trace_points, trial)
            
            accuracy = compute_accuracy(trace_points, spiral_points)
            print(f"Accuracy for trial {trial}: {accuracy}%")

            # Save accuracy to show in WAIT_FOR_ENTER
            last_accuracy = accuracy

            trial += 1
            state = WAIT_FOR_ENTER

    elif state == WAIT_FOR_ENTER:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLUE)
        screen.blit(overlay, (0, 0))

        msg = FONT.render("Trial Ended! Press ENTER to start next trial", True, BLACK)
        screen.blit(msg, (WIDTH // 2 - 250, HEIGHT // 2 - 20))

        # Show accuracy from last trial
        if 'last_accuracy' in locals():
            acc_msg = FONT.render(f"Accuracy: {last_accuracy}%", True, BLACK)
            screen.blit(acc_msg, (WIDTH // 2 - 80, HEIGHT // 2 + 30))

    # Display trial number
    trial_msg = FONT.render(f"Trial: {trial}", True, BLACK)
    screen.blit(trial_msg, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()