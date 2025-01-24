# LHNT_Rover
The code and files used to make Longhorn Neurotech's RC Rover.

The rover uses an ESP32 that can be connected to by a computer using WiFi (currently) and communicates using Python running on a connected computer. 
There are six degrees of freedom that move the rover: forward, backward, turn left, turn right, strafe left, strafe right. 
The current version of the rover's code requires a specific 'STOP' command, which needs an extra degree of freedom. 

Once a computer is connected to the ESP32's WiFi, the python file can take integer or keyboard inputs which will be sent to the rover's ESP32 as an integer. 
The rover will evaluate which motion it should make based on the given integer. It will continue that motion indefinitely (currently). 
