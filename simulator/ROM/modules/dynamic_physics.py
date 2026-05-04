"""
Filename: dynamic_physics.py

Description:
    Equations for modelling the dynamics within the reduced order coil-gun model.
"""

from builtins import float as f
from math import pi


def compute_proj_drag(velocity: f, density: f, coefficient: f, proj_radius: f) -> f:
    """ 
    Calculates the magnitude and direction (-,+) of drag acting on a uniform 
    cylindrical projectile. Uses the velocity 
    """
    area = pi * proj_radius ** 2
    speed = abs(velocity)
    
    direction = velocity / speed if speed != 0 else 0.0
    drag_force = -0.5 * density * speed **2 * area * coefficient * direction
    return drag_force

def compute_inductance(turns: f, coil_len: f, mean_radius: f, permeability: f) -> f:
    """ Calculates the coils self-inductance independent of mutual inductance between coils """
    area = pi * mean_radius ** 2
    return (turns ** 2 * permeability * area) / coil_len


def computes_inductor_voltage(
    supply_voltage: f, current: f, resistance: f, induced_voltage: f
) -> f:
    """ 
    Computes the potential difference across the inductor as current and induced voltage changes.
    """
    voltage_drop = current * resistance
    return supply_voltage - voltage_drop + induced_voltage


def compute_current(
    current: f, voltage: f, inductance: f, resistance: f, time_step: f
) -> tuple[f, f]:
    """ 
    Computes the current using 2nd oder ralston's method however assumes the current changes 
    between frames but the induced voltage term does not (semi-implicit integration)
    """
    k1 = voltage / inductance
    
    # Updates the voltage for the next predicted frame
    voltage = voltage - resistance * 3 / 4 * k1 * time_step
    k2 = voltage / inductance
    
    di_dt = (1/3 * k1 + 2/3 * k2)
    current += di_dt * time_step
    return current, di_dt


def computes_occupancy(
    proj_z: f, coil_z: f, coil_rad: f, coil_len: f, proj_rad: f, proj_len: f
) -> f:
    """
    Computes the occupancy of the projectile within a specific coil via using axis 
    aligned bounding boxes. Positions (proj_z & coil_z) are in reference to the front 
    of the components. The occupancy is calculated assuming an axial-symmetric model (Z, R)
    with the result being the occupancy ratio in the radial plane. 
    
    NOTE: 
    - 'coil_rad' is the outer radius. It is assumed that the core can never fully occupy the coil
    """
    # Calculates the rectangular bounding boxes of projectile and coil
    px_min, py_min, px_max, py_max = proj_z - proj_len, 0, proj_z, proj_rad
    cx_min, cy_min, cx_max, cy_max = coil_z - coil_len, 0, coil_z, coil_rad
    
    # Calculates the width and height of the overlap
    overlap_x = max(0, min(px_max, cx_max) - max(px_min, cx_min))
    overlap_y = max(0, min(py_max, cy_max) - max(py_min, cy_min))
    
    # Calculates the intersection area and ratio
    in_area = overlap_x * overlap_y
    occupancy = in_area / (coil_rad * coil_len)

    # Restricts occupancy to 0 -> 1
    return min(1.0, max(0.0, occupancy))


def compute_z_permeability(occupied: f, field_strength: f, field_density: f) -> f:
    """ 
    Computes the permeability at a point on the z-axis using field density and strength to get
    core_permeability and than coil_occupancy to scale the core permeability. And than uses 
    the non-occupied ratio (1-occupied) to add the free space permeability. 
    """
    mu_core = field_density / field_strength  if field_strength != 0 else 0.0
    mu_air = 4 * pi * 10 ** -7

    return occupied * mu_core + (1-occupied) * mu_air


def compute_z_field_strength(
    z_pos: f, z_coil: f, current: f, turns: f, coil_len: f, coil_rad: f
) -> f:
    """
    Computes the field strength at a position z within or outside of the coil using the finite
    continuous solenoid model in axial-symmetric modelling (Z, R).
    
    'z_coil' is in reference to the front of the coil. Hence center is shifted back coil_len / 2
    """
    half_length = coil_len / 2
    coil_center = z_pos - (z_coil - half_length)
    
    # Calculates the axial field components (term 1 & term 2)
    denom1 = coil_len * (coil_rad ** 2 + (coil_center + half_length)**2) ** 0.5
    term1 = (coil_center + half_length) / denom1
    
    denom2 = coil_len * (coil_rad ** 2 + (coil_center - half_length)**2) ** 0.5
    term2 = (coil_center - half_length) / denom2
    
    # Calculates maximal field_strength and returns position dependent strength
    h_term = turns * current / 2 
    return h_term * (term1 - term2)