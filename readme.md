# Battery-Powered Electromagnetic Gun (aka Coil Gun)
![Fusion Model 10 stages](images/10-stage-side-profile-fusion-360.png) 

## Background

A coilgun is made up of several modules that speed up the projectile. Each module has three parts: a sensor, a switch, and a coil. When the sensor detects the projectile, it tells the switch to turn on the coil. The coil creates a magnetic field that pulls the ferromagnetic projectile toward the center of the coil. To get the fastest speed, the coil is turned off just before the projectile reaches the center. If the coil stayed on, the projectile would slow down and move back and forth before stopping.

![FEMM Post-processor Output](images/Finite-element-magnetic-methods-output.png)  
<b>Fig 1:</b> FEMM post-processor output of the coil & projectile

## Results

<img src="images/10-stages-finished.png" alt="Final Product" width="400"/>
  
<b>Fig 2:</b> One of the only photos I have of the final build (my phone broke)

The 10-stage coil gun I built reached a maximum velocity of about 12–14 m/s. One of the main limitations comes from the 2N2222A transistor used in the switching circuit — it has a maximum collector-emitter voltage of 40VDC. This caps the voltage that can be safely applied to the system, which in turn limits the current the coil can draw. It also means that a capacitor bank can't be used to power the coil. That said, this wasn’t an issue since the design wasn't intended to use capacitors.

[![Watch the demo](https://img.youtube.com/vi/GZpUrEFjWWc/0.jpg)](https://youtu.be/GZpUrEFjWWc)
<br>(3 Stage Verison @ ~30 Volts)

<b>Note</b>: A more in-depth article will be published on my upcoming website once development of my open-source linear motor, Project BlueShark, is complete.  

**Coil Specs:**
- Inductance: ~0.750 mH 
- Resistance: 0.45 Ohms
- Number of turns: 175
- Yoke: 1.5 mm iron wire (2 layers)
- Wire: 1.25 mm enamel copper wire (5 layers)
- "Barrel": Carbon fiber tube  
  _(Avoid conductive or magnetic material to prevent eddy currents)_

**Battery:**
- Voltage: 20V
- Max Discharge Current: 40A

For anyone considering building one: the velocity gain per stage decreases as you add more stages. After about 15–20 stages, the improvements become less — extra stages may not be worth the cost (see Figure 3). I also lost the original PCB files, so you'll need to design your own (Sorry).

![Velocity vs Stage](images/20-stages-graph.png)  
<b>Fig 3:</b> Velocity vs Stage graph for 20-stage coil gun with 40A supply

## Possible Improvements

- Use a separate power supply for the NMOS driver circuitry to allow higher coil voltages without exceeding component limits.
- Apply random search or evolutionary algorithms to design more efficient coil geometries.
- Use a capacitor bank to achieve higher velocity (though with lower overall efficiency).
