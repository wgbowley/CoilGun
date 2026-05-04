"""
Filename: main.py

Description:
    Loads parameters and uts and than initializes and manages 
    the "coilgun" class and routes simulation results to matplotlib 
    for plotting.
"""

import matplotlib.pyplot as plt


from pathlib import Path
from picounits.extensions.parser import Parser

from modules.model import CoilGun

BASE_DIR = Path(__file__).parent
parameter = Parser.open(BASE_DIR / "parameters.uiv", BASE_DIR / "units.ut")

coilgun = CoilGun(parameter)
# Unpack the six variables
time, pos, velocity, force = coilgun.simulate()

fig, axes = plt.subplots(3, 1, figsize=(10, 14), sharex=True)
(ax_pos, ax_vel, ax_force) = axes

# 1. Position Plot
ax_pos.plot(time, pos, color='#2ecc71', linewidth=2, label='Displacement')
ax_pos.set_ylabel('Position (m)')
ax_pos.set_title('CoilGun System Diagnostic')
ax_pos.grid(True, alpha=0.3)
ax_pos.legend(loc='upper left')

# 2. Velocity Plot
ax_vel.plot(time, velocity, color='#3498db', linewidth=2, label='velocity (m/s)')
ax_vel.set_ylabel('velocity (m/s)')
ax_vel.grid(True, alpha=0.3)
ax_vel.legend(loc='upper left')

# 5. Force Plot
ax_force.plot(time, force, color='#e74c3c', linewidth=2, label='Net Force')
ax_force.axhline(0, color='black', linewidth=1)
ax_force.set_xlabel('Time (s)')
ax_force.set_ylabel('Force (N)')
ax_force.grid(True, alpha=0.3)
ax_force.legend(loc='upper left')

plt.tight_layout()
plt.show()