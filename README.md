# Wifi Indoor Localization Techniques

A Collection of python scripts used for Indoor Localization.

Check out net.py for a convenient script to search for wifi networks and connect using only the command line. (given that the network you want to connect is within range and set up in your wpa_supplicant.conf file.)

The other scripts are mainly used for collecting wifi data, plotting a heatmap, using gathered data (eg. positions.csv) to find position in space using Multilateration and Fingerprinting techniques etc. 

For convenience:
- wpaspy.py, iw_parse.py: borrowed code from respective sources, needed for wpa supplicant socket control and for the pretty print methods, respectively 
- net.py: contains methods for controlling the wifi interface (scanning, parsing scan, parsing preconfigured networks, connecting)
- netmode.py: contains code to plot a rather simple drawing of a map of the NETMODE NTUA laboratory
- positions.py: contains a mapping from actual positions in the NETMODE NTUA laboratory to relative positions (unique id, X Y coordinates)
- fingerprinting.py: used for creating the WIFI Fingreprints database. It saves results to positions.csv file by default, usage->run script and then for each relative position in the positions.py file, enter position and wait for a couple of seconds to gather data
- localization_fingerprinting: reads positions.csv database and positions.py file and with the help of some machine learning algorithm (knn used for this problem, performs quite nice and fast learning) performs localization using fingerprinting method eg. scans for wifi networks in range and plots the position in real time.
- multilateration.py: same as localization_fingerprinting, but implements a multilateration algorithm where only wifi network emitters position is known and distance is measured using the simple form of the Log-distance path loss model (L=10*n*log{10}(d)+C)
- heatmap.py: using the positions.csv database it plots a heatmap of wifi emitters signal strength, also calculates optimal fit curve of each emitter to the Log-distance path loss model (n, C).

Repo is totally unstructured, open to everyone seeking some ideas burined in the code :) .For anything else, contact me at konapostolo95@gmail.com
