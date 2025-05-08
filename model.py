# Coil-Gun resistance predicted for TLC555
# 12th of November, 2023
# William Bowley

# Libraries
from tabulate import tabulate
import matplotlib.pyplot as plt

# Constants
OUTER_SHELL_PERMEABILITY = 5.021568627e-6

# Use to predict current.
# INPUT_VOLTAGE = 5
# VOLTAGE_DROP = 0
# COIL_RESISTANCE = 0.160
# TRACE_RESISTANCE_BASE = 0.0023

current = 40
COIL_TURNS = 175

PROJECTILE_LENGTH = 0.054
PROJECTILE_MASS = 0.010

COIL_LENGTHS = [0.052, 0.051, 0.056, 0.053, 0.053, 0.051, 0.053, 0.051, 0.050, 0.051, 0.052, 0.051, 0.056, 0.053, 0.053, 0.051, 0.053, 0.051, 0.050, 0.051]
ADJUSTMENT_CONSTANT = 0.003
TLC_RESISTANCE_BASE = 220

NUM_STAGES = 20
TIMING_CAPACITOR = 1e-6

# Variables
modified_coil_lengths = [length + ADJUSTMENT_CONSTANT for length in COIL_LENGTHS]
tlc_constant = 1.1 * TIMING_CAPACITOR
initial_velocity = 0
results = []
delta_velocities = []

# Main loop
for stage in range(NUM_STAGES):
    
    # Calculates magnetic force and acceleration
    magnetic_force = OUTER_SHELL_PERMEABILITY * COIL_TURNS * (current ** 2)
    acceleration = magnetic_force / PROJECTILE_MASS

    # Calculate initial and extended acceleration
    
    velocity = (initial_velocity ** 2 + 2 * acceleration * PROJECTILE_LENGTH) ** 0.5
    extended_length = (modified_coil_lengths[stage] - PROJECTILE_LENGTH) * (modified_coil_lengths[stage] > PROJECTILE_LENGTH)
    extra_velocity = (velocity ** 2 + 2 * acceleration * extended_length) ** 0.5

    delta_v = extra_velocity-initial_velocity
    delta_velocities.append(delta_v)

    initial_velocity = extra_velocity

    # Calculate kinetic energy and tlc555 resistance
    kinetic_energy = 0.5 * PROJECTILE_MASS * initial_velocity ** 2
    time = delta_v / acceleration
    tlc555_resistance = time / tlc_constant + TLC_RESISTANCE_BASE
    results.append([stage, current, magnetic_force, acceleration, initial_velocity, kinetic_energy, tlc555_resistance])

# Tabular printout
print(tabulate(results, headers=['Stage', 'Current (Amps)', 'Force (Newtons)', 'Acceleration (m/s^2)', 'Velocity (m/s)', 'Kinetic Energy (J)', 'Resistance (Ohms)']))

# Plot both delta velocity and total velocity vs stage, starting from stage 0 at 0 m/s
stages = list(range(NUM_STAGES + 1))  # Now includes stage 0
projectile_velocity_in_time = [0] + [row[4] for row in results]
delta_velocities = [0] + delta_velocities

plt.figure(figsize=(10, 10))

# ΔVelocity per Stage
plt.subplot(2, 1, 1)
plt.plot(stages, delta_velocities, marker='o', linestyle='-', color='green')
plt.title("ΔVelocity per Stage")
plt.xlabel("Stage")
plt.ylabel("ΔVelocity (m/s)")
plt.grid(True)

# Total Velocity per Stage
plt.subplot(2, 1, 2)
plt.plot(stages, projectile_velocity_in_time, marker='s', linestyle='--', color='blue')
plt.title("Projectile Velocity vs Stage")
plt.xlabel("Stage")
plt.ylabel("Velocity (m/s)")
plt.grid(True)

plt.tight_layout()
plt.show()
