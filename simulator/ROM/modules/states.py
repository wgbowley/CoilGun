"""
Filename: states.py

Description:
    Defines the 'Coil' & 'Projectile' dataclasses which holds the states of those
    components during simulation specifically physical and non-physical parameters.
"""

from builtins import float as f
from dataclasses import dataclass


@dataclass(slots=True)
class ProjectileData:
    """ Projectile parameters specifically mass, position and velocity """
    mass: f
    position: f
    velocity: f
    
@dataclass(slots=True)
class CoilData:
    """ Coil parameters specifically position, voltage & current. Also inductance & resistance"""
    position: f
    voltage: f
    current: f
    turns: f
    inductance: f
    resistance: f