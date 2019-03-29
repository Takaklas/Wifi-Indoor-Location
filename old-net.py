import subprocess
import re
import time
import pprint
import math

# list_of_APs = ['Redmi','NetFasteR IAD (PSTN)','Wind WiFi E0CF88','Aspire-A715-71G']
interface = "wlan0"
time_to_wait = 1.5

def calculateDistance3(rssi):
	n = 3.0
	C = -39.0
	diff = C - rssi
	coeff = diff/(10*n)

	distance = math.pow(10,coeff)
	return distance 

def find_network_id():
    dictionary = {}
    cmd = ["wpa_cli", "list_networks"] #, "| grep", ssid]
    #proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #lines = proc.stdout.readlines()[2:] #.decode('utf-8')
    proc = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    lines = proc.readlines()[2:] #.decode('utf-8')
    for line in lines:
        for ssid in list_of_APs:
            if ssid in line:
                dictionary[ssid] = re.search(r'\d+', line).group()
    return dictionary

# list_of_IDs = [find_network_id(ssid) for ssid in list_of_APs]
# list_of_APs_n_IDs = zip(list_of_APs, list_of_IDs)
# dict_of_APs_n_IDs = dict(list_of_APs_n_IDs)
# dict_of_APs_n_IDs = {ssid: find_network_id(ssid) for ssid in list_of_APs}
 
def find_network_id2():
    dictionary = {}
    current_connected = 'Uknown!'
    cmd = ["wpa_cli", "list_networks", "-i", interface] #, "| grep", ssid]
    # proc = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = proc.stdout.readlines()[1:] #.decode('utf-8')
    # content = network id / ssid / bssid / flags
    for line in lines:
        line = line.rstrip("\n").split("\t") 
        network_id, ssid, bssid, flags = line
        if flags == '[CURRENT]':
            current_connected = ssid
            print("Currently connected to: %s" % current_connected)
        dictionary[ssid] = network_id
    return dictionary   

def parse_scan(known_nets):
    cells = []
    freqs = "freq=2412,2417,2422,2427,2432,2437,2442,2447,2452,2457,2462"
    cmd = ["wpa_cli", "scan", "-i", interface,freqs]
    proc = subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(time_to_wait)
    cmd = ["wpa_cli", "scan_results", "-i", interface] #, "| grep", ssid]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = proc.stdout.readlines()[1:] #.decode('utf-8')
    print("Number of networks found: %d" % len(lines))
    content = ['bssid', 'frequency', 'signal level', 'flags', 'ssid']
    loops = range(len(content))
    for line in lines:
        line = line.rstrip("\n").split("\t")
        if line[4] in known_nets:        
            dictionary = {content[i]: line[i] for i in loops}
            dictionary['distance'] = calculateDistance3(float(line[2]))
            cells.append(dictionary)
    # sort cells by signal level
    sortby = 'signal level'
    reverse = False
    cells.sort(None, lambda el: el[sortby], reverse)
    return cells

def show_only_found(ids,cells):
    list_of_found_nets = [cell['ssid'] for cell in cells] 
    dictionary2 = {ssid: ids[ssid] for ssid in ids if ssid in list_of_found_nets}
    return dictionary2    

def connect_to_strongest(cells,ids):
    strongest_ssid = cells[0]['ssid']
    try:
        strongest_id = ids[strongest_ssid]
    except KeyError:
        print("{} not found in database!".format(strongest_ssid))
    strongest_id = str(input("Enter a net id to connect: "))
    start = time.time()
    cmd = ["wpa_cli", "select_network", strongest_id, "-i", interface]
    proc = subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    connected = False
    taken_ip = False
    while not connected:
        cmd = ["iw", interface, "link"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = proc.stdout.readline().split(" ")
        #print status[0]
        if status[0] == 'Connected':
            connected = True
            print(time.time()-start)
            #print 'Connected to {}!'.format(strongest_ssid)
            connected_ssid = proc.stdout.readline().strip().split(" ")[1]
            print('Connected to {}!'.format(connected_ssid))
    time.sleep(0.2)
    while not taken_ip:
        cmd = ["ifconfig", interface]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = proc.stdout.readlines()[1].strip().split(" ")
        #print status[0]
        if status[0] == 'inet':
            taken_ip = True
            print(time.time()-start)
            print('with ip {}!'.format(status[1]))
    return taken_ip
# a = s.check_output(['ip','-4','-o','addr','show','wlp2s0'])
# ip =  a.split()[3].split('/')[0]
 
# cell['id'] = [i for i, s in list_of_APs_n_IDs if cell['essid'] in s][0]
# next(number for (name, number) in items if name == 'show_scllo1')
# indx = [items.index(tupl) for tupl in items if tupl[0] == s][0]

if __name__ == "__main__":
    # print find_network_id()
    ids = find_network_id2()
    # pprint.pprint(ids)
    cells = parse_scan(ids)
    pprint.pprint(cells)
    select = show_only_found(ids,cells)
    pprint.pprint(select)
    connect_to_strongest(cells,ids)


