from tabulate import tabulate

# Constants
OUTER_SHELL_PERMEABILITY = 5.021568627e-6
INPUT_VOLTAGE = 36
VOLTAGE_DROP = 12
COIL_TURNS = 175
COIL_RESISTANCE = 0.160
TRACE_RESISTANCE_BASE = 0.0023

PROJECTILE_LENGTH = 0.054
PROJECTILE_MASS = 0.019

COIL_LENGTHS = [0.052, 0.051, 0.056, 0.053, 0.053, 0.051, 0.053, 0.051, 0.050, 0.051]
ADJUSTMENT_CONSTANT = 0.003
TLC_RESISTANCE_BASE = 220

NUM_STAGES = 10
TIMING_CAPACITOR = 1e-6

# Variables
modified_coil_lengths = [length + ADJUSTMENT_CONSTANT for length in COIL_LENGTHS]
tlc_constant = 1.1 * TIMING_CAPACITOR
initial_velocity = 0
results = []

# Main loop
for stage in range(NUM_STAGES):
    # Calculate current, magnetic force, and acceleration
    trace_resistance = TRACE_RESISTANCE_BASE * stage
    current = (INPUT_VOLTAGE - VOLTAGE_DROP) / (COIL_RESISTANCE + trace_resistance)
    magnetic_force = OUTER_SHELL_PERMEABILITY * COIL_TURNS * (current ** 2)
    acceleration = magnetic_force / PROJECTILE_MASS

    # Calculate initial and extended acceleration
    initial_acceleration = (initial_velocity ** 2 + 2 * acceleration * PROJECTILE_LENGTH) ** 0.5
    extended_length = max(0, modified_coil_lengths[stage] - PROJECTILE_LENGTH)
    extended_acceleration = (initial_acceleration ** 2 + 2 * acceleration * extended_length) ** 0.5
    initial_velocity = extended_acceleration

    # Calculate kinetic energy and tlc555 resistance
    kinetic_energy = 0.5 * PROJECTILE_MASS * initial_velocity ** 2
    time = (extended_acceleration - initial_acceleration) / acceleration
    tlc555_resistance = time / tlc_constant + TLC_RESISTANCE_BASE
    results.append([stage, current, magnetic_force, acceleration, initial_velocity, kinetic_energy, tlc555_resistance])

# Tabular printout
print(tabulate(results, headers=['Stage', 'Current (Amps)', 'Force (Newtons)', 'Acceleration (m/s^2)', 'Velocity (m/s)', 'Kinetic Energy (J)', 'Resistance (Ohms)']))
