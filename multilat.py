#https://www.alanzucconi.com/2017/03/13/understanding-geographical-coordinates/
#https://www.alanzucconi.com/2017/03/13/positioning-and-trilateration/

from scipy.optimize import minimize
import math
import matplotlib.pyplot as plt
import numpy as np
import net
import time
import netmode

def euclidian(x,y,z,r):
    return math.sqrt(math.pow(x-z,2)+math.pow(y-r,2)) 

# Mean Square Error
# locations: [ (lat1, long1), ... ]
# distances: [ distance1, ... ]
def mse(x, locations, distances):
    mse = 0.0
    for location, distance in zip(locations, distances):
        #distance_calculated = great_circle_distance(x[0], x[1], location[0], location[1])
        distance_calculated = euclidian(x[0], x[1], location[0], location[1])
        mse += math.pow(distance_calculated - distance, 2.0)
    return mse / len(locations)

def multilaterate(locations, distances):
    data = []
    for i in range(len(distances)):
        data = data + [{'location':locations[i],'distance':distances[i]}]
    
    # Initial point: the point with the closest distance
    min_distance     = float('inf')
    closest_location = None
    for member in data:
        # A new closest point!
        if member['distance'] < min_distance:
            min_distance = member['distance']
            closest_location = member['location']
    initial_location = closest_location

    # initial_location: (lat, long)
    # locations: [ (lat1, long1), ... ]
    # distances: [ distance1,     ... ] 
    result = minimize(
        mse,                         # The error function
        initial_location,            # The initial guess
        args=(locations, distances), # Additional parameters for mse
        method='L-BFGS-B',           # The optimisation algorithm
        options={
            'ftol':1e-5,         # Tolerance
            'maxiter': 1e+7      # Maximum iterations
        })
    location = result.x
    print(location)
    return location

if __name__ == "__main__":
    plt.ion()
    fig, ax = plt.subplots() # note we must use plt.subplots, not plt.subplot
    netmode.plot_ergasthrio(ax) 
    
    # ca-access-point, node14ap, node19ap, node20ap
    #locations = [ (-7.3,15), (-2.3,16), (2.3,6) , (0.2,10)]
    #distances = [ 2.712, 1.259, 1.585, 4.299 ]	
    Node_coords = {'ca-access-point':(-7.3,15), 
                   'node14ap':(-2.3,16),
                   'node19ap':(2.3,6),
                   'node20ap':(0.2,10),
                   'COSMOTE-49AACE':(0.0,0.0)
    }
    Node_indices = {i:0 for i in Node_coords}
    Node_mean_distances = {i:0 for i in Node_coords}    

    ids = net.find_network_id2()
    wifi_monitor = net.wifi_mon(interface = 'wlp2s0')
    ax.plot(1.2, 12, 'o', color='red')
    stop = False
    while not stop:
        try:
            start = time.time()
            #cells = net.parse_scan(ids, wifi_monitor)
            cells = net.parse_scan(Node_coords, wifi_monitor)
            locations = [Node_coords[cell['ssid']] for cell in cells]
            distances = [float(cell['distance']) for cell in cells]
            for cell in cells: 
                Node_mean_distances[cell['ssid']] *= Node_indices[cell['ssid']]
                Node_mean_distances[cell['ssid']] += float(cell['distance'])
                Node_indices[cell['ssid']] += 1
                Node_mean_distances[cell['ssid']] /= Node_indices[cell['ssid']]
            #distances = [Node_mean_distances[cell['ssid']] for cell in cells]
            print(locations)

            location = multilaterate(locations, distances)
            print("Total time {:.3f} seconds".format(time.time()-start))
            point, = ax.plot([location[0]], [location[1]], 'o', color='black')
            colors = ['r','g','b','y']
            #x = np.array(ax.get_xlim())
            circles = []
            for i in range(len(locations)):
                circle = plt.Circle(locations[i], distances[i], color=colors[i], fill=False, clip_on=False)
                ax.add_artist(circle) 
                circles.append(circle)
            #mng = plt.get_current_fig_manager()
            #mng.resize(*mng.window.maxsize())  
            fig.canvas.draw()
            for circle in circles: circle.remove()
            point.remove()
            #plt.show()
        except KeyboardInterrupt:
            print("=====STOPPED======")
            stop = True
            plt.ioff()
            plt.show()
    
    wifi_monitor.close()
