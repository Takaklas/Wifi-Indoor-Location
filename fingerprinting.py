import net
import pprint
import positions

if __name__ == "__main__":
    file = open("positions.csv","w")
    Relative_Position = '1'
    {'Relative_Position': {'Position_X': 'node10ap', 'Position_Y': 2412}}
    Positions = positions.Positions

    # print find_network_id()
    ids = net.find_network_id2()

    # all_wifi_bssids -> bssid: ssid, frequency
    #{'mac_of_node10ap': {'ssid': 'node10ap', 'freq': 2412}}
    all_wifi_bssids = {} 
    # for writing beauty favor
    all_wifi_bssids['Relative Position'] = {'ssid': 'Relative Position', 'freq': 'Relative Position'}
    all_wifi_bssids['Position X'] = {'ssid': 'Position X', 'freq': 'Position X'}
    all_wifi_bssids['Position Y'] = {'ssid': 'Position Y', 'freq': 'Position Y'}
    # measurements -> [measurement1,...]
    # measurement -> bssid: signal strength
    # measurements = [{
    measurements = []
    
    wifi_monitor = net.wifi_mon(interface = 'wlp2s0')
    stop = False
    while not stop:
        try:
            cells = net.parse_scan(None, wifi_monitor)
            #print(cells)
            net.print_known_cells(cells)
        except KeyboardInterrupt:
            print("======STOPPED======")
            Relative_Position = input("Enter next location or 0 to stop:")
            print("Relative_Position: {}".format(Relative_Position))
            if (Relative_Position == '0'):
                stop = True
            else: 
                print("======CONTINUE======")
            continue

        try:
            measurement = {}
            for cell in cells:
                if cell['bssid'] not in all_wifi_bssids:
                    all_wifi_bssids[cell['bssid']] = {'ssid': cell['ssid'], 'freq': cell['frequency']}

                measurement[cell['bssid']] = cell['signal level']
            measurement['Relative Position'] = Relative_Position
            measurement['Position X'] = Positions[Relative_Position]['Position_X']
            measurement['Position Y'] = Positions[Relative_Position]['Position_Y']
            measurements.append(measurement)
        except KeyboardInterrupt:
            measurement = {}
            for cell in cells:
                if cell['bssid'] not in all_wifi_bssids:
                    all_wifi_bssids[cell['bssid']] = {'ssid': cell['ssid'], 'freq': cell['frequency']}

                measurement[cell['bssid']] = cell['signal level']
            measurement['Relative Position'] = Relative_Position
            measurement['Position X'] = Positions[Relative_Position]['Position_X']
            measurement['Position Y'] = Positions[Relative_Position]['Position_Y']
            measurements.append(measurement)
    
    pprint.pprint(all_wifi_bssids)
    #pprint.pprint(measurements)

    labels = [all_wifi_bssids[i]['ssid'] for i in all_wifi_bssids]
    for label in labels[:-1]: file.write(label+',')
    file.write(labels[-1])
    file.write("\n")

    labels = [all_wifi_bssids[i]['freq'] for i in all_wifi_bssids]
    for label in labels[:-1]: file.write(label+',')
    file.write(labels[-1])
    file.write("\n")            

    labels = [i for i in all_wifi_bssids]
    for label in labels[:-1]: file.write(label+',')
    file.write(labels[-1])
    file.write("\n")

    for measurement in measurements:
        curr_labels = [i for i in measurement]
        labels_not_in_measurement = set(curr_labels).symmetric_difference(labels)
        for label in labels_not_in_measurement:
            measurement[label] = 100
        for label in labels[:-1]: file.write(str(measurement[label])+',')
        file.write(str(measurement[labels[-1]]))
        file.write("\n")
    features = 1
    file.close()
    wifi_monitor.close()
