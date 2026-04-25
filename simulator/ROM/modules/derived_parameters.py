"""
Filename: derived_parameters.py

Description:
    Equations for constructing the reduced order
    coil-gun model specifically derived parameters.
"""

from math import pi, floor
from builtins import float as f

def compute_projectile_mass(axial_length: f, radius: f, density: f) -> f:
    """ 
    Computes the mass of the projectile assuming that the projectile is cylindrically
    symmetric in density.
    """
    volume = pi * radius ** 2 * axial_length
    return volume * density


def compute_turns(axial_length: f, radial_thickness: f, wire_diameter: f, fill_factor: f) -> f:
    """
    Computes the number of turns via calculating the slot and wire cross sectional area than
    scaling the slot area down by fill factor to account for insulation and stacking. After
    which the floor is takin to approximate the number of turns.
    """
    slot_section = axial_length * radial_thickness
    wire_section = pi * (wire_diameter / 2) ** 2

    effective_area = slot_section * fill_factor
    return floor(effective_area / wire_section)


def compute_resistance(turns: f, mean_radius: f, wire_diameter: f, resistivity: f) -> f:
    """ 
    Computes the coils resistance by assuming mean pi*radius approximates the mean turn
    length and than uses conductor cross section and resistivity to get resistance. 
    """
    turn_length = turns * pi * mean_radius
    cross_section = pi * (wire_diameter / 2) ** 2

    return resistivity * turn_length / cross_section


