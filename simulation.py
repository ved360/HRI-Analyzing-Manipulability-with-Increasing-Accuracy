import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sympy import symbols, Matrix, cos, sin, simplify
from sympy.utilities.lambdify import lambdify
from numpy.linalg import svd
import time

# === Symbolic Definitions ===
theta1, theta2 = symbols('theta1 theta2', real=True)
q = Matrix([theta1, theta2])

# Constant parameters
L1 = 3
L2 = 2.4

# Model Equations (no dynamics)
x1 = L1 * cos(theta1)
y1 = L1 * sin(theta1)
x2 = x1 + L2 * cos(theta1 + theta2)
y2 = y1 + L2 * sin(theta1 + theta2)

# Articulation positions
allartics = Matrix([x1, y1, x2, y2])
allnum_func = lambdify((theta1, theta2), Matrix([[0, 0], [x1, y1], [x2, y2]]), modules='numpy')

# End-effector position
r = Matrix([x2, y2])
Jac_r = simplify(r.jacobian(q))
J_r_num_func = lambdify((theta1, theta2), Jac_r, modules='numpy')

# Articulation Jacobian
Jnumall_func = lambdify((theta1, theta2), allartics.jacobian(q), modules='numpy')

# Scaling matrix
Eq = np.diag([1, 1.5])

# === Load and Prepare Data ===
data = pd.read_csv(r"D:\Study Material\Semester VIII\HRI\Final Project\trace_data\trial_32_20250425-005227.csv")
timestamps = data.iloc[:, 2].values
encoder1 = data.iloc[:, 3].values  # q2 = theta2
encoder2 = data.iloc[:, 4].values  # q1 = theta1

# === Animation ===
theta_ellipse = np.linspace(0, 2 * np.pi, 100)

fig, ax = plt.subplots()

ee_path = []  # Track end-effector path

count = 0

for i in range(len(timestamps)):
    x_center, y_center = 400, 300  # or whatever your spiral center coordinates are

    th2_i = np.radians(encoder1[i])
    th1_i = np.radians(encoder2[i])

    current_pose = np.array(allnum_func(th1_i, th2_i)) * 2
    Jop = np.array(J_r_num_func(th1_i, th2_i))
    Jop_scaled = Jop @ Eq
    U, S_vals, Vt = svd(Jop_scaled)
    S = np.diag(S_vals)
    ttt = Jnumall_func(th1_i, th2_i) @ Eq @ Vt.T

    rop = current_pose[2].reshape(2, 1)
    ellipse_pts = rop + U @ S @ np.vstack((np.cos(theta_ellipse), np.sin(theta_ellipse)))

    # Store end-effector path
    ee_path.append(rop.flatten())

    # Clear and plot
    ax.clear()
    ax.plot(x_center, y_center, 'rx', markersize=12, markeredgewidth=3)  # big red cross
    ax.plot(current_pose[:, 0], current_pose[:, 1], '-o', linewidth=3, color=[0, 0.4, 0.8])
    ax.plot(ellipse_pts[0, :], ellipse_pts[1, :], '-.', linewidth=2, color=[0.8, 0.3, 0.3])

    # Plot end-effector path
    if len(ee_path) > 1:
        path_arr = np.array(ee_path)
        ax.plot(path_arr[:, 0], path_arr[:, 1], '-', color='orange', linewidth=1.5)

    # Plot principal directions at end effector only
    # Coordinates of end effector
    x0, y0 = current_pose[2, 0], current_pose[2, 1]

    # Plot principal direction arrows at end effector
    for j in range(2):
        dx = ttt[0::2, j][1]  # x component of j-th vector at EE
        dy = ttt[1::2, j][1]  # y component of j-th vector at EE
        ax.quiver(x0, y0, dx, dy,
                angles='xy', scale_units='xy', scale=1, width=0.01,
                color=[[0, 0.5, 0], [0.3, 0, 0.7]][j])
    
    for j in range(2):  # 0 -> major, 1 -> minor
        dx = ttt[0::2, j][1]
        dy = ttt[1::2, j][1]
        
        A = -dy
        B = dx
        C = dy * x0 - dx * y0

        min = A*400
        
        if j == 0:
            maj = A*400 + B*300 + C
            if maj == 0:
                count = count + 1
            print(f"Major Axis Equation: {A:.4f} * x + {B:.4f} * y + {C:.4f} = 0")
        else:
            min = A*400 + B*300 + C
            if min == 0:
                count = count + 1
            print(f"Minor Axis Equation: {A:.4f} * x + {B:.4f} * y + {C:.4f} = 0")

    # Plot settings
    ax.set_xlim([-11, 11])
    ax.set_ylim([0, 15.25])
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_title(f"2R Robot Arm Simulation - Frame {i+1}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(["Robot", "Manip. Ellipse", "End-Effector Path", "Principal Dir 1", "Principal Dir 2"])
    plt.pause(0.01)
    if i == 1:
        time.sleep(1)

    print(count)

plt.show()