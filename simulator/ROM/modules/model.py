"""
Filename: model.py

Description:
    Defines the 'CoilGun' class which validates input parameters than
    runs the simulation and does complex multi-step equations.
"""

from builtins import float as f
from modules.dynamic_physics import *

from math import pi, ceil

class CoilGun:
    """ Reduced order coil-gun model """
    def __init__(self):
        self.proj_pos = None
        self.proj_length = None
        self.coil_pos = None
        self.coil_rad = None 
        self.coil_len = None 
        self.proj_rad = None
        self.proj_len = None
        self.turns = None
        self.current = None
        
    def _compute_proj_force(
        self, dz: f, current: f, coil_pos: f, coil_rad: f, coil_len: f,
    ) -> f:
        """ 
        Computes the force via using taking the derivative of the energy distributed
        over the projectile volume.
        """
        pos_step, neg_step = self.proj_pos + dz, self.proj_pos - dz
        
        # Calculates the energy one step forwards and one backwards
        pos = self._compute_energy_state(pos_step, current, coil_pos, coil_rad, coil_len, dz)
        neg = self._compute_energy_state(neg_step, current, coil_pos, coil_rad, coil_len, dz)
        
        return (pos - neg) / (2 * dz)


    def _compute_energy_state(
        self, proj_pos: f, current: f, coil_pos: f, coil_rad: f, coil_len: f, dz: f
    ) -> f:
        """ 
        Computes the energy distributed throughout the projectile volume. 
        Assumes energy distributed within the coil doesn't contribute to the force.
        """
        energy = 0.0
        proj_pos = proj_pos - self.proj_length
        for _ in range(ceil(self.proj_length / dz)):
            h_z = compute_z_field_strength(
                proj_pos, coil_pos, current, self.turns, coil_len, coil_rad
            )
            
            # Calculates permeability via occupancy and field strength
            occupancy = computes_occupancy(
                proj_pos, coil_pos, coil_rad, coil_len, self.proj_rad, self.proj_len
            )
            
            field_density = self._lookup_density(h_z)
            permeability = compute_z_permeability(occupancy, h_z, field_density)
            
            energy += 0.5 * permeability * h_z ** 2 * dz
            proj_pos += dz
            
        radial_term = self.proj_rad ** 2 * pi
        return radial_term * energy

    def _lookup_density(field_strength: f) -> f:
        """ lookups the field density for a specific field_strength """
        return
  