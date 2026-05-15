"""
Filename: model.py

Description:
    Defines the 'CoilGun' class which validates input parameters than
    runs the simulation and does complex multi-step equations.
"""

import os
import matplotlib.pyplot as plt

from builtins import float as f
from math import pi, ceil, log, isclose

from picounits import strip_quantity as q_strip, Q
from picounits.extensions.loader import DynamicLoader
from picounits.constants import (
    NULLSET, TIME, LENGTH, RESISTANCE, MASS, CURRENT, FLUX_DENSITY, VOLTAGE
)


from modules.dynamic_physics import *
from modules.derived_parameters import *
from modules.states import ProjectileData, CoilData


class CoilGun:
    """ Reduced order coil-gun model """
    def __init__(self, parameters: DynamicLoader) -> None:
        """ Initializes the class an validates input data """
        self.extract_and_strip(parameters)
        
        # Class variables
        self.projectile: ProjectileData = None
        self.coils: list[CoilData] = []
        self.free_space = 4 * pi * 10 ** -7
        self.derivative_epsilon = 1e-4

    def simulate(self) -> Q:
        """ Simulates the coilgun and saves H-field snapshots to disk """
        self.generate_projectile_and_coils()
        
        # Create a directory for the frames if it doesn't exist
        if not os.path.exists('sim_frames'):
            os.makedirs('sim_frames')
            
        time = 0.0
        step_count = 0
        time_list, position_list, velocity_list, force_list = [], [], [], []

        # Define spatial domain for plotting
        z_max = 1.5 * self.coils[-1].position
        z_axis = [i * 0.001 for i in range(int(z_max / 0.001))]

        while self.projectile.position < z_max:
            self._electrical_domain()
            print(time)
            # Save a photo every 10 steps
            if step_count % 10 == 0:
                h_profile = [self._compute_z_field_strength(z) for z in z_axis]
                self._save_h_frame(z_axis, h_profile, time, step_count)
            
            force = self._compute_proj_force(self.derivative_epsilon)
            force += compute_proj_drag(
                self.projectile.velocity, 
                self.atmospheric_density, 
                self.proj_coe_drag, 
                self.proj_rad
            )
            
            # Euler Integration
            acceleration = force / self.projectile.mass
            self.projectile.velocity += acceleration * self.time_step
            self.projectile.position += self.projectile.velocity * self.time_step
            
            # Data Logging
            time_list.append(time)
            position_list.append(self.projectile.position)
            velocity_list.append(self.projectile.velocity)
            force_list.append(force)
            
            time += self.time_step
            step_count += 1
            
        return time_list, position_list, velocity_list, force_list

    def _save_h_frame(self, z_axis: list[f], h_vals: list[f], current_time: f, step: int):
        """ Saves a static PNG of the current H-field state """
        plt.figure(figsize=(12, 6))
        
        # Plotting the field
        plt.plot(z_axis, h_vals, color='black', linewidth=1.5, label='Total H-Field')
        
        # Visualizing the Projectile (Blue) and Coils (Red outlines)
        plt.axvspan(self.projectile.position - self.proj_len, 
                    self.projectile.position, color='blue', alpha=0.3, label='Projectile')
        
        for coil in self.coils:
            plt.axvline(x=coil.position - self.coil_len, color='red', linestyle=':', alpha=0.4)
            plt.axvline(x=coil.position, color='red', linestyle=':', alpha=0.4)

        plt.title(f"H-Field Profile | Time: {current_time:.6f}s | Step: {step}")
        plt.xlabel("Z-Position (m)")
        plt.ylabel("H-Field (A/m)")
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper right')
        
        # Save with leading zeros so the files sort correctly in your viewer
        plt.savefig(f'sim_frames/frame_{step:05d}.png')
        plt.close() # Important to close to free up memory

    def _electrical_domain(self) -> None:
        """ Managements the connection of the supply source to the coil """
        proj_pos = self.projectile.position

        for coil in self.coils:
            coil_activation_pos = coil.position - self.coil_len
            coil_disconnection_pos = coil_activation_pos + self.coil_activation
            
            if proj_pos >= coil_activation_pos and proj_pos < coil_disconnection_pos:
                coil.supply_voltage = self.supply_voltage
            else:
                # TEMP. TESTING -> REMOVE LATER
                coil.supply_voltage = -self.supply_voltage if coil.current > 0 else 0.0
            
            # # Calculates the occupancy & permeability
            occupancy = computes_occupancy(
                self.projectile.position, coil.position, self.coil_outer_rad,
                self.coil_len, self.proj_rad, self.proj_len
            )
            
            # Computes field strength and than looks up b field
            h_z = self._compute_z_field_strength(coil.position - self.coil_len / 2)
            b_z = self._lookup_density(h_z)
            
            permeability = compute_z_permeability(occupancy, h_z, b_z)
            inductance = compute_inductance(coil.turns, self.coil_len, self.coil_mean_rad, permeability)

            # Calculates the induced voltage due to the change in the projectile position
            dz_dt = self.projectile.velocity
            dl_dz = 0.0

            if dz_dt != 0.0: dl_dz = (inductance - coil.inductance) / (dz_dt * self.time_step)

            coil.induced_voltage = coil.current * dz_dt * dl_dz
            coil.inductance = inductance

            # Calculates inductor voltage & current for the electromagnetic & mechanical domain
            coil.inductor_voltage = computes_inductor_voltage(
                coil.supply_voltage, coil.current, coil.resistance, coil.induced_voltage
            )
            
            series_res = self.battery_esr + coil.resistance
            coil.current, _ = compute_current(
                coil.current, coil.inductor_voltage, coil.inductance, series_res, self.time_step
            )

    def _compute_proj_force(self, dz: f) -> f:
        """ 
        Computes the force via using taking the derivative of the energy distributed
        over the projectile volume.
        """
        pos_step, neg_step = self.projectile.position + dz, self.projectile.position - dz
        
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
            energy += 0.5 * h_z * b_z * dz

            proj_pos += dz
            
        radial_term = self.proj_rad ** 2 * pi
        return radial_term * energy

    def _compute_z_field_strength(self, z_pos: f) -> f:
        """ 
        Calculates the field strength across the z-axis including all coils within the domain 
        """
        proj_c = self.projectile.position - self.proj_len / 2
        a = 0.8
        r = 1

        # Distance from projectile center
        trans = proj_c - z_pos
        r_sq = r ** 2
        dist_sq = r_sq + trans ** 2
        
        # transform
        d_z = a * trans / dist_sq
        jacobian = 1 + a * ((trans**2 - r_sq) / (dist_sq**2))

        h_z_global = 0.0
        z_warped = z_pos - d_z
        for coil in self.coils: 
            h_z = compute_z_field_strength(
                z_warped, 
                coil.position, 
                coil.current, 
                coil.turns, 
                self.coil_len, 
                self.coil_inner_rad
            )

            h_z_global += h_z

        return h_z_global * abs(jacobian)
    
    def _lookup_density(self, field_strength: f) -> f:
        """ 
        lookups the field density for a specific field_strength using linear interpolation for region
        of low field strength. And uses log-linear interpolation for larger values to improve stability.
        """
        # Enforces field strength boundaries
        if field_strength <= self.proj_h[0]: 
            return self.proj_b[0]

        if field_strength >= self.proj_h[-1]: 
            return self.proj_b[-1]
        
        num = 0
        for i in range(self.proj_bh_length - 1):
            if field_strength < self.proj_h[i+1]:
                num = i
                break
            
        # Approximates using linear interpolation if field strength is very simple
        if field_strength < 1.0:
            frac = (field_strength - self.proj_h[num]) / (self.proj_h[num+1] - self.proj_h[num])
            return self.proj_b[num] + frac * (self.proj_b[num+1] - self.proj_b[num])
        
        # Log-linear interpolation (for large field strength values)
        log_field_strength = log(field_strength)
        log_low, log_high = self.proj_log_h[num], self.proj_log_h[num+1]
        
        frac = (log_field_strength - log_low) / (log_high - log_low)
        return self.proj_b[num] + frac * (self.proj_b[num+1] - self.proj_b[num])

    def generate_projectile_and_coils(self) -> None:
        """ 
        Generates the dataclasses for the projectiles and coil positions within the simulation domain via
        creating their instances
        """
        self.projectile = ProjectileData(
            mass = compute_projectile_mass(self.proj_len, self.proj_rad, self.proj_density),
            position = 0.0, velocity = 0.0
        )
        
        # Calculates the turns & permeability
        mean_radius = (self.coil_outer_rad + self.coil_inner_rad) / 2
        turns = compute_turns(self.coil_len, mean_radius, self.coil_wire_dia, self.fill_factor)

        for index in range(self.number_stages): 
            coil = CoilData(
                position = self.coil_len * (index + 1) + self.stage_gap * index,
                supply_voltage = 0.0,
                inductor_voltage = 0.0,
                induced_voltage = 0.0,
                current = 0.0,
                turns = turns,
                inductance = compute_inductance(turns, self.coil_len, mean_radius, self.free_space),
                resistance = compute_resistance(
                    turns, mean_radius, self.coil_wire_dia, self.coil_resistivity
                ),
                b_field=0.0
            )
            self.coils.append(coil)

    def extract_and_strip(self, parameters: DynamicLoader) -> None:
        """ Extracts than validates and finally strips the parameter from configuration file """
        self.number_stages = q_strip(parameters.model.number_stages, NULLSET)
        self.time_step = q_strip(parameters.model.time_steps, TIME)
        self.stage_gap = q_strip(parameters.model.stage_gap, LENGTH)
        self.supply_voltage = q_strip(parameters.model.voltage, VOLTAGE)
        
        self.battery_esr = q_strip(parameters.model.battery_esr, RESISTANCE)
        self.atmospheric_density = q_strip(parameters.model.atmospheric_density, MASS/LENGTH **3)
        
        self.proj_rad = q_strip(parameters.projectile.radius, LENGTH)
        self.proj_len = q_strip(parameters.projectile.axial_length, LENGTH)
        self.proj_coe_drag = q_strip(parameters.projectile.coefficient_drag, NULLSET)
        self.proj_density = q_strip(parameters.projectile.density, MASS/LENGTH **3)
        self.proj_alpha = q_strip(parameters.projectile.alpha, NULLSET)
        
        # Strips magnetic hysteresis table (b, h)co
        hysteresis = parameters.projectile.magnetic_hysteresis
        
        # Constructs the field_strength (h -> b) lookup table
        self.proj_h, self.proj_log_h, self.proj_b = [], [], []
        for row in hysteresis:
            field_density = q_strip(row[0], FLUX_DENSITY)
            field_strength = q_strip(row[1], CURRENT / LENGTH)
            
            self.proj_b.append(field_density)
            
            self.proj_h.append(field_strength)
            
            # Ensures that log(0) isn't performed
            value = 1e-9
            if field_strength > 0: 
                value = log(field_strength)

            self.proj_log_h.append(value)
            
        self.proj_bh_length = len(self.proj_h)

        self.coil_len = q_strip(parameters.coil.axial_length, LENGTH)
        self.coil_activation = self.coil_len * 0.5

        self.coil_outer_rad = q_strip(parameters.coil.outer_radius, LENGTH)
        self.coil_inner_rad = q_strip(parameters.coil.inner_radius, LENGTH)
        self.coil_mean_rad = (self.coil_outer_rad + self.coil_inner_rad) / 2
        
        self.coil_wire_dia = q_strip(parameters.coil.wire_diameter, LENGTH)
        self.coil_resistivity = q_strip(parameters.coil.resistivity, RESISTANCE * LENGTH)
        self.fill_factor = q_strip(parameters.coil.fill_factor, NULLSET)