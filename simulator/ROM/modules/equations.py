"""
Filename: equations.py

Description:
    Equations for a reduced order coil-gun model. 
"""

from math import pi, ceil
from builtins import float as f


def projectile_mass(axial_length: f, radius: f, density: f) -> f:
    """ Calculates the mass of the projectile """
    volume = pi * radius ** 2 * axial_length

    return volume * density


def estimate_turns(
    axial_length: f, inner_radius: f, outer_radius: f, wire_diameter: f, fill_factor: f
) -> f:
    """ Estimates the number of turns that can fit in a rectangular coil """
    slot_area = axial_length * (outer_radius - inner_radius)
    wire_area = wire_diameter ** 2
    effective_area = slot_area * fill_factor

    turns = effective_area / wire_area
    return ceil(turns)


def cal_resistance(turns: f, mean_radius: f, wire_diameter: f, resistivity: f) -> f:
    """ Calculates the resistance of the inductor """
    length = turns * pi * mean_radius
    area = pi * (wire_diameter / 2) ** 2
    return resistivity * length / area

