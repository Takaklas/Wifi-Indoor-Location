import subprocess
import re
import time
import pprint
import math
import wpaspy
from iw_parse import get_parsed_cells, print_cells

# list_of_APs = ['Redmi','NetFasteR IAD (PSTN)','Wind WiFi E0CF88','Aspire-A715-71G']
interesting_APs = ['node10ap', 'node14ap', 'node19ap', 'node20ap', 'ca-access-point']
interface = "wlan0"
time_to_wait = 1.5

def wpas_connect(host=None, port=9877):
    try:
        wpas = wpaspy.Ctrl(host, port)
        return wpas
    except:
        print("Could not connect to host: ", host)
        return None

def wifi_mon(interface=None, port=9877):
    wpas_ctrl = '/var/run/wpa_supplicant/'
    host = wpas_ctrl + interface
    print("Attemting wpa_supplicant control interface connection")
    wpas = wpas_connect(host, port)
    if wpas is None:
        return
    print("Connected to wpa_supplicant")
    print(wpas.request('PING'))

    mon = wpas_connect(host, port)
    if mon is None:
        print("Could not open event monitor connection")
        return

    mon.attach()
    return mon

def calculateDistance3(network, rssi):
    # RSSI = -10*n*log(d)+C
    # d = 10^((C-RSSI) / (10*n))
    if network=='ca-access-point':
        n = 1.116
        C = -37.709
    elif network=='node14ap':
        n = 0.668
        C = -35.554
    elif network=='node19ap':
        n = 2.36
        C = -37.624
    elif network=='node20ap':
        n = 3.208
        C = -29.94
    else:
        print("WTF NET")
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
    proc = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

def simple_scan():
    # freqs = "freq=2412,2417,2422,2427,2432,2437,2442,2447,2452,2457,2462"
    freqs = "freq=2412,2432,2437"
    cmd = ["wpa_cli", "scan", "-i", interface,freqs]
    proc = subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(time_to_wait)
    cmd = ["wpa_cli", "scan_results", "-i", interface] #, "| grep", ssid]
    proc = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = proc.stdout.readlines()[1:] #.decode('utf-8')
    return lines

def scan_with_monitor(mon):
    print("Scan")
    #freqs = "freq=2412,2417,2422,2427,2432,2437,2442,2447,2452,2457,2462"
    freqs = "freq=2412,2432,2437,2452,2462"
    print(mon.request('SCAN ' + freqs))

    while True:
        while mon.pending():
            ev = mon.recv()
            #print(ev)
            if 'CTRL-EVENT-SCAN-RESULTS' in ev:
                print('Scan completed')
                return mon.request('SCAN_RESULTS').split('\n')[1:-1]

def parse_scan(known_nets, wifi_monitor):
    cells = []
    cells2 = []
    start = time.time()
    # lines = simple_scan()
    lines = scan_with_monitor(wifi_monitor)
    print("Scan took %f seconds" % (time.time()-start))
    print("Number of networks found: %d" % len(lines))
    content = ['bssid', 'frequency', 'signal level', 'flags', 'ssid']
    loops = range(len(content))
    for line in lines:
        #print(line)
        line = line.rstrip("\n").split("\t")
        if known_nets == None:
            dictionary = {content[i]: line[i] for i in loops}
            dist = calculateDistance3(line[4], float(line[2]))
            dictionary['distance'] = '{:.3f}'.format(dist)
            cells.append(dictionary)
        elif line[4] in known_nets:        
            dictionary = {content[i]: line[i] for i in loops}
            dist = calculateDistance3(line[4], float(line[2]))
            dictionary['distance'] = '{:.3f}'.format(dist)
            cells.append(dictionary)
    # sort cells by signal level
    sortby = 'signal level'
    reverse = False
    cells.sort(key = lambda el: el[sortby], reverse = reverse)
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
        return
    except IndexError:
        print("No known network found")
    strongest_id = str(input("Enter a net id to connect: "))
    start = time.time()
    cmd = ["wpa_cli", "select_network", strongest_id, "-i", interface]
    proc = subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    connected = False
    taken_ip = False
    while not connected:
        cmd = ["iw", interface, "link"]
        proc = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = proc.stdout.readline().split()
        #print status[0]
        if status[0] == 'Connected':
            connected = True
            print(time.time()-start)
            #print 'Connected to {}!'.format(strongest_ssid)
            connected_ssid = proc.stdout.readline().split()[1]
            print('Connected to {}!'.format(connected_ssid))
    time.sleep(0.2)
    while not taken_ip:
        cmd = ["ifconfig", interface]
        proc = subprocess.Popen(cmd, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = proc.stdout.readlines()[1].split()
        #print status[0]
        if status[0] == 'inet':
            taken_ip = True
            print(time.time()-start)
            print('with ip {}!'.format(status[1]))
    return taken_ip
# a = s.check_output(['ip','-4','-o','addr','show','wlp2s0'])
# ip =  a.split()[3].split('/')[0]

def print_known_cells(cells):
    # You can choose which columns to display here, and most importantly
    # in what order. Of course, they must exist as keys in the dict rules.
    columns = [
        "ssid",
        "bssid",
        "frequency",
        #"flags",
        "signal level",
        #"distance"
    ]
    
    sortby = 'distance'
    reverse = False
    cells.sort(key = lambda el: el[sortby], reverse = reverse)

    print_cells(cells, columns)
 
# cell['id'] = [i for i, s in list_of_APs_n_IDs if cell['essid'] in s][0]
# next(number for (name, number) in items if name == 'show_scllo1')
# indx = [items.index(tupl) for tupl in items if tupl[0] == s][0]

if __name__ == "__main__":
    # print find_network_id()
    ids = find_network_id2()
    pprint.pprint(ids)
    wifi_monitor = wifi_mon(interface = interface)
    # cells = returns wifi cells in ids
    # if ids = None: return all wifi cells found
    cells = parse_scan(ids, wifi_monitor)
    #pprint.pprint(cells)
    print_known_cells(cells)
    select = show_only_found(ids,cells)
    pprint.pprint(select)
    connect_to_strongest(cells,ids)
    wifi_monitor.close()


