bilt 
==========

modules to control bilt power supplies from the database

listener.py runs on a raspberry pi and communicates command documents from the database to the power supply via bilt.py.

bilt.py provides functions to read out and set values to the bilt sources.

configuration, i.e. possible voltage and current ranges and the assignment which coil is connected to which power supply, is done with a dictionary on the database with the id "bilt_config"

