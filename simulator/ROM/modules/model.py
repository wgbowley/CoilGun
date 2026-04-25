"""
Filename: model.py

Description:
    Defines the 'CoilGun' class which validates input parameters than
    runs the simulation and does complex multi-step equations.
"""

from builtins import float as f
from math import pi, ceil

from picounits import strip_quantity as q_strip
from picounits.extensions.loader import DynamicLoader
from picounits.constants import (
    NULLSET, TIME, LENGTH, RESISTANCE, MASS, CURRENT, FLUX_DENSITY
)


from modules.dynamic_physics import *
from modules.derived_parameters import *
from modules.states import ProjectileData, CoilData


class CoilGun:
    """ Reduced order coil-gun model """
    def __init__(self, parameters: DynamicLoader) -> None:
        """ Initializes the class an validates input data """
        self.extract_and_strip(parameters)
        
        self.projectile = ProjectileData(
            mass = compute_projectile_mass(self.proj_len, self.proj_rad, self.proj_density),
            position = -self.proj_len, 
            velocity = 0.0
        )
        
        # Calculates the turns & permeability
        mean_radius = (self.coil_outer_rad + self.coil_inner_rad) / 2
        turns = compute_turns(self.coil_len, mean_radius, self.coil_wire_dia, self.fill_factor)
        permeability = 4 * pi * 10 ** -7

        self.coils: list[CoilData] = []
        for index in range(self.number_stages): 
            coil = CoilData(
                position = self.proj_len * (index + 1) + self.stage_gap * index,
                voltage = 0.0,
                current = 0.0,
                turns = turns,
                inductance = compute_inductance(turns, self.coil_len, mean_radius, permeability),
                resistance = compute_resistance(
                    turns, mean_radius, self.coil_wire_dia, self.coil_resistivity
                )
            )
            self.coils.append(coil)
        
    def _compute_proj_force(self, dz: f) -> f:
        """ 
        Computes the force via using taking the derivative of the energy distributed
        over the projectile volume.
        """
        pos_step, neg_step = self.proj_pos + dz, self.proj_pos - dz
        
        # Calculates the energy one step forwards and one backwards
        pos = self._compute_energy_state(pos_step, dz)
        neg = self._compute_energy_state(neg_step, dz)
        
        return (pos - neg) / (2 * dz)

    def _compute_energy_state(self, proj_pos: f, dz: f) -> f:
        """ 
        Computes the energy distributed throughout the projectile volume. 
        Assumes energy distributed within the coil doesn't contribute to the force.
        
        NOTE:
        Assumes the permeability of the projectile is uniform and follows the 
        BH-curve of the projectile material only.
        """
        energy = 0.0
        proj_pos = proj_pos - self.proj_len
        for _ in range(ceil(self.proj_len / dz)):
            h_z = self._compute_z_field_strength(proj_pos)

            # Calculates field density & energy
            b_z = self._lookup_density(h_z)
            energy += 0.5 * b_z * h_z * dz

            proj_pos += dz
            
        radial_term = self.proj_rad ** 2 * pi
        return radial_term * energy

    def _compute_z_field_strength(self, z_pos: f) -> f:
        """ 
        Calculates the field strength across the z-axis including all coils within the domain 
        """
        b_z = 0.0
        for coil in self.coils:
            b_z += compute_z_field_strength(
                z_pos, coil.position, coil.current, coil.turns, self.coil_len, self.coil_inner_rad
            )

        return b_z
    
    def _lookup_density(field_strength: f) -> f:
        """ lookups the field density for a specific field_strength """
        return
  
    def extract_and_strip(self, parameters: DynamicLoader) -> None:
        """ Extracts than validates and finally strips the parameter from configuration file """
        self.number_stages = q_strip(parameters.model.number_stages, NULLSET)
        self.time_step = q_strip(parameters.model.time_steps, TIME)
        self.stage_gap = q_strip(parameters.model.stage_gap, LENGTH)
        self.battery_est = q_strip(parameters.model.battery_esr, RESISTANCE)
        self.atmospheric_density = q_strip(parameters.model.atmospheric_density, MASS/LENGTH **3)
        
        self.proj_rad = q_strip(parameters.projectile.radius, LENGTH)
        self.proj_len = q_strip(parameters.projectile.axial_length, LENGTH)
        self.proj_coe_drag = q_strip(parameters.projectile.coefficient_drag, NULLSET)
        self.proj_density = q_strip(parameters.projectile.density, MASS/LENGTH **3)
        
        # Strips magnetic hysteresis table (b, h)
        hysteresis = parameters.projectile.magnetic_hysteresis
        
        # Constructs the field_strength (h -> b) lookup table
        proj_hysteresis = []
        for row in hysteresis:
            field_density = q_strip(row[0], FLUX_DENSITY)
            field_strength = q_strip(row[1], CURRENT / LENGTH)
            
            proj_hysteresis.append([field_strength, field_density])
        
        self.coil_len = q_strip(parameters.coil.axial_length, LENGTH)
        self.coil_outer_rad = q_strip(parameters.coil.outer_radius, LENGTH)
        self.coil_inner_rad = q_strip(parameters.coil.inner_radius, LENGTH)
        
        self.coil_wire_dia = q_strip(parameters.coil.wire_diameter, LENGTH)
        self.coil_resistivity = q_strip(parameters.coil.resistivity, RESISTANCE * LENGTH)
        self.fill_factor = q_strip(parameters.coil.fill_factor, NULLSET)