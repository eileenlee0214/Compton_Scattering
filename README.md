# Inconvenienced Electrons
Physics C Final Project by Daniel Caal and Eileen Lee

---
## Overview
We initially wanted to simulate the Compton Scattering effect, which is when a high-energy photon collides with an electron and thereby transfers some of its energy to the electron. The resulting photon will have a longer wavelength due to loss of energy, and the electron will gain kinetic energy. (The effect is negligible if the photon is low-energy, i.e. below X-ray range, and with high energy photons/the right energy the electrons will either jump up to a higher energy orbital or be ejected completely.) This experiment proved the wave-particle duality of light, as well as conversation of momenta and energy.

Initially, we wanted to show the conservation of momentum and energy directly via a graph, as well as the scattering angle histogram (verified using the Klein-Nishina formula). We have resorted to keep the simulation units, because using the real constants have broken the Glowscript animation and were out of feasible range.

## Compton Scattering Mode
You will notice that there are two checkboxes to set the mode below the screen. The default is set to have the Compton Scattering box checked. You will first click the "Place Electron" button to get into electrons placing mode, and use your device input to place electrons (represented as blue spheres) wherever you want (user zoom is disabled in this mode). Then, you should click the "Place Photon" button (this changes depending on which mode you are on) and click on the screen to place them. It is also entirely possible to place photons of different frequencies on the same page.

Notice how the sliders for the frequency isn't linear. It was because we wanted each light spectrum range to take up roughly the same length, but since infrared-ultraviolet has significantly lower frequency, we established some helper functions to scale the exponenets adequately and take the log as follows. The slider shows you which range the photon is placed in, and the color of the photon also changes depending on the frequency (e.g. gamma ray becomes white, x-ray is violet, etc.). 

After you have places all photons and electrons as desired, you could click "run" button to see the simulation. You should see the changes in photons, such as the angle/direction deflecting, the colors/frequency altering after collisions, as well as the elastic collisions between electrons. There is also an option to check the "attach momentum vectors," which allows you to track the velocity of the electrons. If the momentum is too small, the vectors will not be super visible outside of the electrons--in which case you can pop the electrons to verify. The program also allows you to add any additional photons and electrons while the simulation is already running. 

The graphs above are meant to verify Noether's theorem (conservation of energy and momentum), and the histograpm tracks the variations of deflected angles. You should see the blue bar on the very right of each graph (labeled "check") remains the same during the entirety of duration, while the accumulation of energy/momenta of electrons and photons are changing.

To reset, you would just click reset which would take you to the black initial screen. 

## Bohr Model Mode
Our initial idea was to simulate Compton Scattering model with electrons bound to an atom (in this case, hydrogen nucleus). However, after multiple trial and errors, we have found out that the collision probability between photons and electrons were low, so we decided to instead show the emission of photons when electrons in the excited state return back to ground states.

You would start by checking the "Bohr Model" checkbox, which will give you a tiny hydrogen nucleus with six surrounding orbitals. Since the orbitals gets larger on the outer side, we have designed the Bohr Model to allow user zoom. You can then start placing the electrons on whichever orbitals you want by clicking, and place photons (if you choose to) the same way you did for Compton Scattering Mode.

If you choose not to place any photons, and have electron(s) placed in orbital $n=2,3,...$ pressing "run" would show you the spontaneous photon emissions following the returning of electrons. The emissions of photons are randomized, so some might experience one photon emission, and others might take two or more steps to arrive to the ground state. And since the graphs for momentum and energy are for collisions, they don't update if it's just photon emission.

If you have chosen to add photons and collisions have happened, you will notice any affected electrons will turn into yellow spheres. If collided with a high-energy photon (ultraviolet and higher, photoelectric effects), it will escape the orbital entirely because the program calculates the binding energy depending on the orbital energy level (it is worth noting that this simulation does not account for the mutual attraction between nucleus and electron, because it was not directly related to the simulation's purposes.) The ejected yellow electron will then intefinitely maintain the calculated momentum.

Clicking the "reset" button will remove all electrons from the orbital + nucleus graphic, which you can then repeat the simulation.