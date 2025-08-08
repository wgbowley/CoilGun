"""
File: sim_math.py
Author: William Bowley
Version: 2.0
Date: 2025-08-08
Description:
    Physics functions to model coilgun behavior. Includes:
    - First-order RL circuit response (Inductor transient response)
    - Position-dependent B-field within a solenoid coil
    - Magnetic force on the projectile based on position and time

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

from math import exp, sqrt, pi


def inst_current_charging(
    time: float,
    supply_voltage: float,
    coil_resistance: float,
    coil_inductance: float,
    time_offset: float = 0.0
) -> float:
    """
    Calculate the instantaneous current during charging in an RL circuit.

    Args:
        time (float): Current simulation time (s)
        supply_voltage (float): Voltage applied across the coil (V)
        coil_resistance (float): Resistance of the coil (Ω), > 0
        coil_inductance (float): Inductance of the coil (H), > 0
        time_offset (float): Time when charging begins (s)

    Returns:
        float: Instantaneous current in amperes (A)
    """
    if coil_resistance <= 0:
        raise ValueError(f"Resistance must be > 0, got {coil_resistance}")
    if coil_inductance <= 0:
        raise ValueError(f"Inductance must be > 0, got {coil_inductance}")

    tau = coil_inductance / coil_resistance
    max_current = supply_voltage / coil_resistance

    return max_current * (1 - exp(-(time - time_offset) / tau))


def inst_current_discharging(
    time: float,
    initial_current: float,
    coil_resistance: float,
    coil_inductance: float,
    time_offset: float = 0.0
) -> float:
    """
    Calculate the instantaneous current during discharging in an RL circuit.

    Args:
        time (float): Current simulation time (s)
        initial_current (float): Current at the start of discharge (A)
        coil_resistance (float): Resistance of the coil (Ω), > 0
        coil_inductance (float): Inductance of the coil (H), > 0
        time_offset (float): Time when discharging begins (s)

    Returns:
        float: Instantaneous current in amperes (A), decays toward 0
    """
    if coil_resistance <= 0:
        raise ValueError(f"Resistance must be > 0, got {coil_resistance}")
    if coil_inductance <= 0:
        raise ValueError(f"Inductance must be > 0, got {coil_inductance}")

    tau = coil_inductance / coil_resistance

    return initial_current * exp(-(time - time_offset) / tau)


def position_b_field(
    position: float,
    current: float,
    number_turns: int,
    coil_length: float,
    avg_coil_radius: float,
    permeability: float,
) -> float:
    """
    Calculate the axial B-field inside a solenoid based on projectile position.

    Args:
        position (float): Distance from the coil origin (m)
        current (float): Current through the coil (A), must be >= 0
        number_turns (int): Number of turns per unit length (turns/m), > 0
        coil_length (float): Axial length of the solenoid (m), > 0
        avg_coil_radius (float): Average radius of the coil (m), > 0
        permeability (float): Magnetic permeability of the projectile (H/m)

    Returns:
        float: Magnetic field strength at the given position (T)
    """

    if coil_length <= 0:
        msg = f"Coil length must be > 0, got {coil_length}"
        raise ValueError(msg)

    if avg_coil_radius <= 0:
        msg = f"Avg coil radius must be > 0, got {avg_coil_radius}"
        raise ValueError(msg)

    if number_turns <= 0:
        msg = f"Number of turns must be > 0, got {number_turns}"
        raise ValueError(msg)

    b_const = 0.5 * permeability * number_turns * current

    denom1 = sqrt(position**2 + avg_coil_radius**2)
    term1 = position / denom1

    delta = position - coil_length
    denom2 = sqrt(delta**2 + avg_coil_radius**2)
    term2 = delta / denom2

    return b_const * (term1 - term2)


def inst_force(
    b_field: float,
    permeability: float,
    projectile_outer_radius: float,
    force_direction: int = 1  # +1 for forward, -1 for backward
) -> float:
    """
    Calculate instantaneous force on a ferromagnetic projectile.

    Based on energy density in a magnetic field:
    F ≈ (1/2) * (B^2 / µ) * A, where A is the cross-sectional area.

    Args:
        b_field (float): Magnetic field strength at the projectile (T), >= 0
        permeability (float): Magnetic permeability of the projectile (H/m)
        projectile_outer_radius (float): Radius of the projectile (m), > 0
        force_direction (int): +1 or -1 to flip force direction

    Returns:
        float: Instantaneous force on the projectile (N)
    """
    if projectile_outer_radius <= 0:
        msg = f"Projectile radius must be > 0, got {projectile_outer_radius}"
        raise ValueError(msg)

    cross_section = pi * projectile_outer_radius**2
    force_magnitude = 0.5 * (b_field**2 / permeability) * cross_section

    return force_magnitude * force_direction
