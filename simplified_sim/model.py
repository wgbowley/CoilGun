"""
File: motor.py
Author: William Bowley
Version: 1.1
Date: 2025-08-08

Description:
    Simulates a multi-stage coilgun using a simplified
    physical model.

    Parameters are loaded from a YAML configuration file.

Requirements:
    - matplotlib
    - pyyaml
"""

import math
import yaml
import matplotlib.pyplot as plt

# CONSTANTS
PARAMETER_FILE = "simplified_sim/coilgun.yaml"
VACCUM_PERM = 4 * math.pi * 1e-7

# Loads in parameters file
with open(PARAMETER_FILE, "r", encoding="utf-8") as file:
    params = yaml.safe_load(file)

# Calculated Model parameters
projectile_prem = VACCUM_PERM * params["projectile"]["relative_perm"]
time_constant = params["coil"]["inductance"] / params["coil"]["resistance"]


def acceleration(
    time: float,
    supply_current: float,
    lr_constant: float,
    permeability: float,
    number_turns: float,
    projectile_mass: float,
) -> float:
    """
    Calculate instantaneous acceleration based on coil current ramp.
    Based on lorentz force formula and Transient behaviour of inductors

    Args:
        time: Time since coil energized (s).
        supply_current: Max coil current (A).
        lr_constant: Coil L/R time constant (s).
        permeability: Effective permeability (H/m).
        number_turns: Coil turns.
        projectile_mass: Projectile mass (kg).

    Returns:
        Instantaneous acceleration (m/s^2).
    """
    inst_current = supply_current * (1 - math.exp(-time / lr_constant))
    constant = (permeability * number_turns) / projectile_mass
    return constant * inst_current ** 2


# Data logging & initial conditions
initial_velocity = 0.0
time_step = 1e-5
stage_data = []

for stage in range(params["number_stages"]):
    elaps_time = 0.0
    position = 0.0
    velocity = initial_velocity

    # Accelerate projectile through half coil length
    while position < 0.5 * params["coil"]["length"]:
        inst_acceleration = acceleration(
            elaps_time,
            params["current"],
            time_constant,
            projectile_prem,
            params["coil"]["turns"],
            params["projectile"]["mass"],
        )

        # Calculates upwards from a->v->p with respect to dt
        velocity += inst_acceleration * time_step
        position += velocity * time_step
        elaps_time += time_step

    velocity_exit = velocity
    delta_v = velocity_exit - initial_velocity

    stage_data.append({
        "Stage": stage + 1,
        "Entry Speed (m/s)": initial_velocity,
        "Exit Speed (m/s)": velocity_exit,
        "Transit Time (ms)": elaps_time * 1e3,
        "Δv (m/s)": delta_v,
    })

    print(
        f"Stage {stage + 1}: entry={initial_velocity:.3f} m/s, "
        f"exit={velocity_exit:.3f} m/s, transit={elaps_time*1e3:.3f} ms"
    )
    initial_velocity = velocity_exit


# Prepare data for plots
stages = [0] + [d["Stage"] for d in stage_data]
delta_velocities = [0] + [d["Δv (m/s)"] for d in stage_data]
projectile_velocity_in_time = [0] + [d["Exit Speed (m/s)"] for d in stage_data]

# Change in velocity between stages (0-1, 1-2, 2-3, etc)
plt.subplot(2, 1, 1)
plt.plot(
    stages,  # X-axis
    delta_velocities,  # Y-axis
    marker='o',
    linestyle='-',
    color='green')
plt.title("Delta Velocity per Stage")
plt.xlabel("Stage")
plt.ylabel("Delta Velocity (m/s)")
plt.grid(True)

# Change in velocity over stages
plt.subplot(2, 1, 2)
plt.plot(
    stages,  # X-axis
    projectile_velocity_in_time,  # Y-axis
    marker='s',
    linestyle='--',
    color='blue'
)
plt.title("Projectile Velocity vs Stage")
plt.xlabel("Stage")
plt.ylabel("Velocity (m/s)")
plt.grid(True)

plt.tight_layout()
plt.show()
