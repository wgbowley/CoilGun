"""
File: main.py
Author: William Bowley
Version: 2.0
Date: 2025-08-08
Description:
    Simulates a multi-stage coilgun using a simplified
    physical model.

    Parameters are loaded via a YAML configuration file.

Units used throughout:
    Time: seconds (s)
    Distance/Length: meters (m)
    Current: amperes (A)
    Voltage: volts (V)
    Resistance: ohms (Ω)
    Inductance: henrys (H)
    Magnetic field (B): teslas (T)
    Permeability (µ): henrys per meter (H/m)
    Force: newtons (N)
"""

from math import pi
import matplotlib.pyplot as plt
from yaml import safe_load

from sim_math import (
    inst_current_charging,
    inst_current_discharging,
    position_b_field,
    inst_force
)

# Constants
PARAMETER_FILE = "simulator/parameters.yaml"
VACUUM_PERMEABILITY: float = 4 * pi * 1e-7
TIME_STEP = 1e-5  # Time step for Euler integration (seconds)

# Load parameter file
with open(PARAMETER_FILE, "r", encoding="utf-8") as file:
    params = safe_load(file)

# Pre-load variables from YAML
flyback = params["model"]["flyback"]
stages = params["model"]["number_stages"]
voltage = params["model"]["voltage"]

length = params["coil"]["axial_length"]
outer_radius = params["coil"]["outer_radius"]
inner_radius = params["coil"]["inner_radius"]

resistance = params["coil"]["resistance"]
inductance = params["coil"]["inductance"]
turns = params["coil"]["turns"]

relative_perm = params["projectile"]["relative_perm"]
projectile_radius = params["projectile"]["radius"]
projectile_mass = params["projectile"]["mass"]

# Calculated parameters
projectile_prem = VACUUM_PERMEABILITY * relative_perm
turns_per_meter = turns / length
avg_radius = (outer_radius + inner_radius) / 2

# Global accumulators for plotting
total_time_data = []
total_velocity_data = []
cumulative_time = 0.0

initial_velocity = 0.0
results = []

for stage in range(stages):
    time = 0.0
    position = 0.0
    velocity = initial_velocity
    time_offset = 0.0
    initial_current = 0.0
    direction = 1

    while position < length:
        current = 0.0

        if position > 0.5 * length:
            if not flyback:
                direction = -1
                current = inst_current_discharging(
                    time=time,
                    initial_current=initial_current,
                    coil_resistance=resistance,
                    coil_inductance=inductance,
                    time_offset=time_offset
                )
        else:
            current = inst_current_charging(
                time=time,
                supply_voltage=voltage,
                coil_resistance=resistance,
                coil_inductance=inductance,
            )
            initial_current = current
            time_offset = time

        b_field = position_b_field(
            position=position,
            current=current,
            number_turns=turns_per_meter,
            coil_length=length,
            avg_coil_radius=avg_radius,
            permeability=projectile_prem
        )

        force = inst_force(
            b_field=b_field,
            permeability=projectile_prem,
            projectile_outer_radius=projectile_radius,
            force_direction=direction
        )

        # Calculate acceleration (F = ma)
        inst_acceleration = force / projectile_mass

        # Euler integration for velocity and position
        velocity += inst_acceleration * TIME_STEP
        position += velocity * TIME_STEP
        time += TIME_STEP

        # Append cumulative time and velocity for plotting
        total_time_data.append(cumulative_time + time)
        total_velocity_data.append(velocity)

    velocity_exit = velocity
    delta_v = velocity_exit - initial_velocity

    results.append({
        "Stage": stage + 1,
        "Entry Speed (m/s)": initial_velocity,
        "Exit Speed (m/s)": velocity_exit,
        "Transit Time (ms)": time * 1e3,
        "DeltaV (m/s)": delta_v,
    })

    print(
        f"Stage {stage + 1}: entry={initial_velocity:.3f} m/s, "
        f"exit={velocity_exit:.3f} m/s, transit={time*1e3:.3f} ms"
    )

    # Update cumulative time and initial velocity for next stage
    cumulative_time += time
    initial_velocity = velocity_exit

# Plot combined velocity vs time for all stages
plt.plot(total_time_data, total_velocity_data)
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title(f'Velocity vs. Time for All {stages} Stages')
plt.grid(True)
plt.show()
