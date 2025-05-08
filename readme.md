# Battery-Powered Electromagnetic Gun (aka Coil Gun)
![Fusion Model 10 stages](images/10-stage-side-profile-fusion-360.png) 

## Background

The setup consists of a solenoid coil, a photogate, and switching circuitry. When the photogate detects a projectile, it triggers current to flow through the coil, generating a magnetic field. The projectile, being ferromagnetic, seeks an arrangement that minimizes potential energy. This change creates a force that accelerates the projectile toward the center of the coil. Once the projectile reaches the center, the current is switched off, collapsing the magnetic field and allowing the projectile to continue its motion toward the next stage. If the magnetic field doesn't collapse, the projectile will oscillate until it settles in the center.

![FEMM Post-processor Output](images/Finite-element-magnetic-methods-output.png)  
<b>Fig 1:</b> FEMM post-processor output of the coil & projectile

## Results

<img src="images/10-stages-finished.png" alt="Final Product" width="400"/>
  
<b>Fig 2:</b> One of the only photos I have of the final build (my phone broke)

The 10-stage coil gun I built reached a maximum velocity of about 12–14 m/s. One of the main limitations comes from the 2N2222A transistor used in the switching circuit — it has a maximum collector-emitter voltage of 40VDC. This caps the voltage that can be safely applied to the system, which in turn limits the current the coil can draw. It also means that a capacitor bank can't be used to power the coil. That said, this wasn’t an issue since the design wasn't intended to use capacitors.

**Coil Specs:**
- Number of turns: 175
- Yoke: 1.5 mm iron wire (2 layers)
- Wire: 1.25 mm enamel copper wire (5 layers)
- "Barrel": Carbon fiber tube  
  _(Avoid conductive or magnetic material to prevent eddy currents)_

**Battery:**
- Voltage: 20V
- Max Discharge Current: 40A

For anyone considering building one: the velocity gain per stage decreases as you add more stages. After about 15–20 stages, the improvements become marginal — extra stages may not be worth the added complexity or cost (see Figure 3). I also lost the original PCB files, so you'll need to design your own (Sorry).

![Velocity vs Stage](images/20-stages-graph.png)  
<b>Fig 3:</b> Velocity vs Stage graph for 20-stage coil gun with 40A supply

## Possible Improvements

- Use a separate power supply for the NMOS driver circuitry to allow higher coil voltages without exceeding component limits.
- Apply random search or evolutionary algorithms to design more efficient coil geometries.
- Use a capacitor bank to achieve higher velocity (though with lower overall efficiency).
