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
    
    @property
    def name(self) -> str:
        """ Returns the dataclasses name """
        return(
            f"<Proj(mass:{self.mass:.5f}kg" 
            f", position:{self.position:.5f}m"
            f", velocity:{self.velocity:.5f}m/s)>"
        )
        
    def __repr__(self) -> str: return self.name
   
        
    
@dataclass(slots=True)
class CoilData:
    """ Coil parameters specifically position, voltage & current. Also inductance & resistance"""
    position: f
    supply_voltage: f
    inductor_voltage: f
    induced_voltage: f
    current: f
    turns: f
    inductance: f
    resistance: f
    b_field: f
    
    @property
    def name(self) -> str:
        """ Returns the dataclasses name """
        return (
            f"<Coil(pos:{self.position:.5f}m" 
            f", V_s:{self.supply_voltage:.5f}v"
            f", V_L:{self.inductor_voltage:.5f}v"
            f", V_i:{self.induced_voltage:.5f}v"
            f", I:{self.current:.5f}A"
            f", L:{self.inductance:.5f}H"
            f", R:{self.resistance:.5f}Ω)>"
            f", B:{self.b_field:.5f}T"
        )
        
    def __repr__(self) -> str: return self.name