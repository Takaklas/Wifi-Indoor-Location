#!/usr/bin/python

import threading
import time
import iwlist
import pprint


class threaded_iwparse(threading.Thread):
    def __init__(self, threadID, name, interface, counter, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.interface = interface
        self.counter = counter
        self.delay = delay
        self.cells = None
        self.updated = False
        self.time_taken = None
        self.stopped = False

    def run(self):
        print "Starting " + self.name
        self.print_iwlist()
        print "Exiting " + self.name


    def print_iwlist(self):
        while self.counter:
            if self.stopped:
                #self.name.exit()
                return
            # time.sleep(self.delay)
            start = time.time()

            """ Pretty prints the output of iwlist scan into a table. """
            content = iwlist.scan(self.interface) #(interface='wlan0')
            self.cells = iwlist.parse(content)

            # print cells
            sortby = "signal_level_dBm"
            reverse = False
            self.cells.sort(None, lambda el: el[sortby], reverse)

            self.updated = True
            self.time_taken = time.time()-start

            self.counter -= 1
        
        self.stopped = True
        return


    def read(self):
        # return the cells most recently read
        self.updated = False
        return self.cells

    def update(self):
        return self.updated

    def time(self):
        #return time taken
        return self.time_taken

    def stop(self):
        self.stopped = True

    def running(self):
        return not self.stopped

