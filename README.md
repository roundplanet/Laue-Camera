# Laue Camera

This project was coded to simplify the usage of a backscattered Laue Camera from
 Photonic Science with the NTXLaue Software at the Chair of Experimental Physics 6 
 from the University of Augsburg. The NTX Software unfortunatly only runs at a 
 Windows 7 system and furthermore the setup includes four electrical 
 stepping motors controllable by a raspberry pi for rotating and translating the sample. 
 Therefore a comunication network was implemented to supervise all actions on a Linux 
 computer, for which this code was written. 



## Main Features

- GUI
- Interaction with Laue Camera and stepping motors
- Sample alignment with feedback
- Image processing with background subtraction
- Grid analysis and sample characterisation
- Help to all functions with explanations to basic models


## Upcoming Improvements

- Simulation of Laue Pattern
- Overlap of different directions from one Laue Pattern


## Authors

- [Julian Kaiser](https://www.github.com/roundplanet) (GUI, grid analysis, sample alignment, improved background subtraction, image processing)

- [Marvin Klinger](https://www.github.com/Marvin-Klinger) (network implementation, sample movement, model for background subtraction, image conversion)
