import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import net
import pprint
from sklearn.neighbors import KNeighborsClassifier as kNN
from positions import Positions
import netmode

plt.ion()
fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot
netmode.plot_ergasthrio(ax)

dataset = pd.read_csv("mean_positions.csv",header = [0,1,2])
features = np.asarray(dataset.iloc[:,3:])
labels = np.asarray(dataset["Relative Position"])

# MACs of networks in dataset
networks = [z for (_,_,z) in list(dataset)[3:]]

# If we want only selected wifis in dataset:
network_names = ['ca-access-point','node14ap','node19ap','node20ap']
networks = [z for (x,_,z) in list(dataset)[3:] if x in network_names]
features = np.asarray(dataset[network_names])

# Current networks found in scan
# Must be of length and order of original networks in dataset
found_networks = [0]*len(networks)

#a = dataset.hist()
#plt.plot(a)

clf = kNN(n_neighbors=2)
print(clf)
clf.fit(features,labels)

wifi_monitor = net.wifi_mon(interface = 'wlp2s0')
stop = False
while not stop:
    try:
        cells = net.parse_scan(None, wifi_monitor)
        #print(cells)
        # [{'bssid': '00:0b:6b:de:ea:36', 'frequency': '2437',
        # 'signal level': '-37', 'flags': '[WPA-PSK-TKIP][WPA2-PSK-TKIP][ESS]',
        # 'ssid': 'node14ap', 'distance': '0.858'},
        net.print_known_cells(cells)
        for i in range(len(found_networks)): found_networks[i] = 100
        for cell in cells:
            mac = cell['bssid']
            if mac not in networks: continue
            rssi = cell['signal level']
            found_networks[networks.index(mac)] = rssi 
        
        position = clf.predict([found_networks])[0]
        pos = Positions[str(position)]
        pos_x = pos['Position_X']
        pos_y = pos['Position_Y']
        #plt.plot(pos_x, pos_y, marker='o', markersize=10, color="black")
        marker = ax.scatter(pos_x, pos_y, marker='o', color="red")
        fig.canvas.draw()
        marker = ax.scatter(pos_x, pos_y, marker='o', color="black")        
        #marker.remove()
        print("Position: {}".format(position))

    except KeyboardInterrupt:
        print("=====STOPPED======")
        stop = True
        plt.ioff()
        plt.show()
    
wifi_monitor.close()

        
