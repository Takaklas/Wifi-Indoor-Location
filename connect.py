import time
import pprint
import math
import subprocess
import re

from threaded_iwparse import threaded_iwparse
from iw_parse_fork import get_parsed_cells, print_cells, get_interfaces

interesting_cells = []
#list_of_APs = ['nt','nt5','HOL_TC_7']
#list_of_APs = ['Redmi','NetFasteR IAD (PSTN)','Wind WiFi E0CF88','Aspire-A715-71G']
list_of_APs = ['NETMODE_2.4GHz', 'NETMODE_5GHz']#, 'netmode']
interface = "wlan0"

def parse_scan():
    cells = []
    cmd = ["wpa_cli", "scan_results", "-i", interface] #, "| grep", ssid]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = proc.stdout.readlines()[1:] #.decode('utf-8')
    content = ['bssid', 'frequency', 'signal level', 'flags', 'ssid']
    for line in lines:
        line = line.split("\t")
        loops = range(5)
        dictionary = {content[i]: line[i] for i in loops}
    return dictionary 

def find_network_id():
    dictionary = {}
    current_connected = 'Uknown!'
    cmd = ["wpa_cli", "list_networks", "-i", interface] #, "| grep", ssid]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = proc.stdout.readlines()[1:] #.decode('utf-8')
    # content = network id / ssid / bssid / flags
    for line in lines:
        line = line.split("\t")
        network_id, ssid, bssid, flags = line
        if flags is [CURRENT]:
            current_connected = ssid
        dictionary[ssid] = network_id
    return dictionary 

dict_of_APs_n_IDs = find_network_id()

def show_cells(cells):
    # pprint.pprint(interesting_cells)

    # You can choose which columns to display here, and most importantly
    # in what order. Of course, they must exist as keys in the dict rules.
    # columns = ["essid", "id", "mac", "signal_level_dBm", "channel", "encryption","distance"]
    columns = ["essid", "id", "mac", "signal_level_dBm", "distance"]
    print_cells(cells, columns)

def connect_to_strongest(cells):
    strongest_id = cells[0]['id']
    
def calculateDistance(rssi):
	C = -39.0
	n = 3.0
	diff = C - float(rssi)
	coeff = diff/(10*n)

	distance = math.pow(10,coeff)
	return str(distance)

# Create new threads
# threaded_iwparse ------> threadID, name, interface, counter, delay
thread1 = threaded_iwparse(1, "Threaded_iwlist_parse", interface, 12, 1)

# Start new Threads
thread1.start()
time.sleep(0.1)
# print thread1.read()
print "Enter ctrl-c to stop..."
try:
    while thread1.running():
        if thread1.update():
            cells = thread1.read()
            interesting_cells = []
            for cell in cells:
                if cell['essid'] in list_of_APs:
                    cell['distance'] = calculateDistance(cell['signal_level_dBm'])
                    cell['id'] = dict_of_APs_n_IDs[cell['essid']]
                    interesting_cells.append(cell)
            show_cells(interesting_cells)
            print "Time taken: %.2f s" % thread1.time()
        else:
            print "No updates"
            time.sleep(1)
except KeyboardInterrupt:
    thread1.stop()
    time.sleep(0.1)

print "Exiting Main Thread"

