"""
Filename: equations.py
Author: William Bowley
Version: 0.1

Description:
    Equations for a analytical coil-gun model
    as an example, for the picounits library
"""

from math import pi, ceil
from picounits.core import unit_validator, Quantity as q

from picounits.constants import (
    CURRENT, VOLTAGE, FLUX_DENSITY, FORCE, TIME, MASS, LENGTH,
    INDUCTANCE, IMPEDANCE, DIMENSIONLESS, PERMEABILITY
)


@unit_validator(MASS)
def projectile_mass(axial_length: q, radius: q, density: q) -> q:
    """ Calculates the mass of the projectile """
    volume = pi * radius ** 2 * axial_length
    return volume * density


@unit_validator(DIMENSIONLESS)
def estimate_turns(
    axial_length: q, inner_radius: q, outer_radius: q,
    wire_diameter: q, fill_factor: q
) -> q:
    """ Estimates the number of turns that can fit in a rectangular coil """
    slot_area = axial_length * (outer_radius - inner_radius)
    wire_area = wire_diameter ** 2
    effective_area = slot_area * fill_factor

    turns = effective_area / wire_area
    return ceil(turns)


@unit_validator(PERMEABILITY)
def calculate_approximate_core_permeability(
    position: q, permeability: q, relative: q, coil_length: q,
    proj_length: q, coil_outer_radius: q, proj_radius: q
) -> q:
    """ Calculates the approximate permeability as the coil moves through """
    # Calculates the cross sectional axial-area
    coil_area = 2 * coil_outer_radius * coil_length

    # Calculates the rectangular bounding boxes of projectile and coil
    px_min, py_min = position - proj_length, -proj_radius
    px_max, py_max = position, +proj_radius

    cx_min, cy_min = 0 * LENGTH, -coil_outer_radius
    cx_max, cy_max = coil_length, +coil_outer_radius

    # Calculates the width and height of the overlap
    overlap_x = max(0 * LENGTH, min(px_max, cx_max) - max(px_min, cx_min))
    overlap_y = max(0 * LENGTH, min(py_max, cy_max) - max(py_min, cy_min))

    # Calculates the intersection area and ratio
    in_area = overlap_x * overlap_y
    occupancy = in_area / coil_area

    # Restricts to 0 -> 1
    occupancy = min(1.0, max(0.0, occupancy))

    # Returns weighted permeability of the core
    return permeability * (1 + (relative - 1) * occupancy)


@unit_validator(IMPEDANCE)
def cal_resistance(
    turns: q, mean_radius: q, wire_diameter: q, resistivity: q
) -> q:
    """ Calculates the resistance of the inductor """
    length = turns * pi * mean_radius
    area = pi * (wire_diameter / 2) ** 2
    return resistivity * length / area


@unit_validator(INDUCTANCE)
def cal_inductance(
    turns: q, axial_length: q, mean_radius: q, permeability: q
) -> q:
    """ Calculates the inductance of solenoid """
    # Defines the permeability of free space
    area = pi * mean_radius ** 2
    return (turns ** 2 * area * permeability) / axial_length


@unit_validator(FORCE)
def projectile_drag(velocity: q, density: q, coefficient: q, radius: q) -> q:
    """ Calculates the drag force on the projectile """
    area = pi * radius ** 2
    velocity = velocity * abs(velocity)
    drag_force = -0.5 * density * velocity * area * coefficient
    return drag_force


@unit_validator(CURRENT / TIME)
def differential_currents(voltage: q, inductance: q) -> q:
    """ Differential equation for current within the system """
    return voltage / inductance


@unit_validator(CURRENT)
def clipping_current(current_limit: q, current: q) -> q:
    """ Limits the current to simulate a current limiting supply"""
    return min(current_limit, current)


@unit_validator(VOLTAGE)
def inductor_voltage(
    supply_voltage: q, current: q, resistance: q, induced_voltage: q
) -> q:
    """ Computes the inductor voltage during simulation"""
    voltage_drop = current * resistance
    return supply_voltage - voltage_drop + induced_voltage


@unit_validator(CURRENT)
def rk_2nd_order_current(
    current: q, voltage: q, inductance: q, resistance: q, step_size: q
) -> q:
    """ Solves the differential equation using Ralston's method"""
    k1 = differential_currents(voltage, inductance)

    # Updates the voltage for the next predicted frame
    voltage = voltage - resistance * 3 / 4 * step_size * k1
    k2 = differential_currents(voltage, inductance)

    current += (1 / 3 * k1 + 2 / 3 * k2) * step_size
    return current


@unit_validator(FLUX_DENSITY)
def position_b_field(
    position: q, current: q, turns: q, coil_length: q,
    coil_radius: q, relative_permeability: q, saturation: q
) -> q:
    """
    Calculates the axial B-field inside a solenoid based on projectile position
    """
    # print(position, current, turns, coil_length, coil_radius)
    b_constant = 0.5 * relative_permeability * turns * current

    denom1 = (position ** 2 + coil_radius ** 2) ** 0.5
    term1 = position / denom1

    delta = position - coil_length
    denom2 = (delta ** 2 + coil_radius ** 2) ** 0.5
    term2 = delta / denom2

    b_field = b_constant * (term1 - term2)

    # Simple switch to mimic B-H curve
    if abs(b_field) > saturation:
        return saturation * (b_field / abs(b_field))

    return b_field


@unit_validator(FORCE)
def inst_force(
    b_field: q, permeability: q, projectile_outer_radius: q, direction: q
) -> q:
    """
    Calculate instantaneous force on a ferromagnetic projectile.

    Based on energy density in a magnetic field:
    F ≈ (1/2) * (B^2 / µ) * A, where A is the cross-sectional area.
    """
    cross_section = pi * projectile_outer_radius ** 2
    force_magnitude = (
        0.5 * (abs(b_field) * b_field / permeability) * cross_section
    )

    return force_magnitude * direction
