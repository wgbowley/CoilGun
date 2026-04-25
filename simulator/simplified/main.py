"""
Filename: main.py

Description:
    Analytical lumped-parameter coil-gun model for quick optimization.

    NOTE:
    This is an analytical, lumped-parameter demonstration model.
    It is not intended to match FEM or experimental results.
"""

from math import pi
from pathlib import Path
from plotting import plot

from picounits.extensions.parser import Parser
from picounits.constants import (
    TIME, VELOCITY, LENGTH, CURRENT, VOLTAGE, DIMENSIONLESS, PERMEABILITY, FLUX_DENSITY
)

from equations import (
    inductor_voltage, rk_2nd_order_current, position_b_field, inst_force, clipping_current, 
    projectile_drag, projectile_mass, estimate_turns, cal_resistance, cal_inductance,
    calculate_approximate_core_permeability
)

BASE_DIR = Path(__file__).parent
p = Parser.open(BASE_DIR / "parameters.uiv", BASE_DIR / "units.ut")

# Set calculations
permeability = 4 * pi * 1e-7 * PERMEABILITY
average_radius = (p.coil.outer_radius + p.coil.inner_radius) / 2
turns = estimate_turns(
    p.coil.axial_length, p.coil.inner_radius, p.coil.outer_radius,
    p.coil.wire_diameter, p.coil.fill_factor
)

turns_per_meter = turns / p.coil.axial_length
resistance = cal_resistance(turns, average_radius, p.coil.wire_diameter, p.coil.resistivity)
inductance = cal_inductance(turns, p.coil.axial_length, average_radius, permeability)
mass = projectile_mass(p.projectile.axial_length, p.projectile.radius, p.projectile.density)

# Prints calculated parameters such as projectile mass, inductance, resistance
print("=== Coil Gun derived parameters ===")
print(f"Number of turns @{p.coil.fill_factor:.2f}: {turns:.3f}")
print(f"Coil Resistance: {resistance:.3f}")
print(f"Coil Inductance: {inductance:.3f}")
print("=== Dynamic launch results ===")

# Global accumulators for plotting
total_time_data = []
total_force_data = []
total_velocity_data = []
total_current_data = []

cumulative_time = 0.0 * TIME
cumulative_position = 0.0 * LENGTH

initial_velocity = 0.0 * VELOCITY
results = []

for stage in range(p.model.number_stages.stripped):
    time = 0.0 * TIME
    position = 0.0 * LENGTH
    velocity = initial_velocity
    current = 0.0 * CURRENT
    voltage = 0.0 * VOLTAGE
    b_prev = 0.0 * FLUX_DENSITY
    induced_voltage = 0.0 * VOLTAGE
    motional_inductance = inductance
    motional_permeability = permeability
    direction = 1 * DIMENSIONLESS
    b_gradient = 0 * (FLUX_DENSITY / TIME)

    simulation_length = p.coil.axial_length + p.model.stage_gap
    while position < simulation_length:
        supply_voltage = 0.0 * VOLTAGE
        direction = 1 * DIMENSIONLESS

        # Switches voltage source off half way through the coil
        center = position - 1 / 2 * p.projectile.axial_length
        if position < 0.5 * p.coil.axial_length:
            supply_voltage = p.model.voltage

        # Calculates the inductor voltage, then inductor current & limiting
        voltage = inductor_voltage(supply_voltage, current, resistance, induced_voltage)
        current = rk_2nd_order_current(
            current, voltage, motional_inductance, resistance,
            p.model.time_steps
        )
        current = clipping_current(p.model.current_limit, current)

        # Calculates b-field strength, then force on projectile
        b_now = position_b_field(
            position, current, turns_per_meter, p.coil.axial_length,
            average_radius, motional_permeability,
            p.projectile.magnetic_saturation
        )

        force = inst_force(b_now, motional_permeability, p.projectile.radius, direction)
        force += projectile_drag(
            velocity, p.model.atmospheric_density,
            p.projectile.coefficient_drag, p.projectile.radius
        )

        # Calculates acceleration (f = ma)
        inst_acceleration = force / mass

        # Euler integration for velocity and position
        velocity += inst_acceleration * p.model.time_steps
        delta_p = velocity * p.model.time_steps

        position += delta_p
        time += p.model.time_steps

        # Calculates the dB/dt
        area = pi * p.projectile.radius ** 2
        b_gradient = (b_now - b_prev) / p.model.time_steps
        induced_voltage = - turns * b_gradient * area
        b_prev = b_now

        # Calculates the motional permeability and inductance
        motional_permeability = calculate_approximate_core_permeability(
            position, permeability, p.projectile.relative_permeability,
            p.coil.axial_length, p.projectile.axial_length,
            p.coil.outer_radius, p.projectile.radius
        )
        motional_inductance = cal_inductance(
            turns, p.coil.axial_length, average_radius, motional_permeability
        )

        # Appends cumulative and velocity for plotting (Removes units)
        cumulative_position += velocity * p.model.time_steps

        cumulative_time += p.model.time_steps
        total_time_data.append(cumulative_time.stripped)

        total_force_data.append(force.stripped)
        total_velocity_data.append(velocity.stripped)
        total_current_data.append(current.stripped)

    velocity_exit = velocity
    delta_v = velocity_exit - initial_velocity

    results.append({
        "Stage": stage + 1,
        "Entry Speed:": initial_velocity,
        "Exit Speed:": velocity_exit,
        "Transit Time:": time,
        "DeltaV:": delta_v,
    })

    print(
        f"Stage {stage + 1}: entry={initial_velocity:.3f}, "
        f"exit={velocity_exit:.3f}, transit={time:.3f}"
    )

    # Update cumulative time and initial velocity for next stage
    initial_velocity = velocity_exit

# Close off terminal print with end line
print("==============================")

# Plot combined velocity vs time for all stages
plot(total_time_data, total_current_data, total_force_data, total_velocity_data)
