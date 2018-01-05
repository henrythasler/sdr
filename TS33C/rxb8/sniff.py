from datetime import datetime
import matplotlib
import pigpio as gpio
from time import sleep

# Force matplotlib to not use any Xwindows backend.
#matplotlib.use('Agg')

import matplotlib.pyplot as plt

RECEIVED_SIGNAL = [[], []]  #[[time of reading], [signal reading]]
RECEIVE_PIN = 17

startticks = 0

def cbf(gpio, level, tick):
    global startticks
    RECEIVED_SIGNAL[0].append(tick-startticks)
    RECEIVED_SIGNAL[1].append(level)

def main():
    pi = gpio.pi("rfpi")
    if not pi.connected:
        print "Could not connected to rfpi"
        exit()
    startticks = pi.get_current_tick()

    pi.set_glitch_filter(RECEIVE_PIN, 150)
    
    print '**Started recording**'
    cb1 = pi.callback(RECEIVE_PIN, gpio.EITHER_EDGE, cbf)    
    sleep(1)
    cb1.cancel()
    print '**Ended recording**'

    print len(RECEIVED_SIGNAL[0]), 'samples recorded'

    print '**Plotting results**'
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.set_size_inches(18.5, 10.5)
    #ax.plot(RECEIVED_SIGNAL[0], RECEIVED_SIGNAL[1], linewidth=1)
    ax.step(RECEIVED_SIGNAL[0], RECEIVED_SIGNAL[1], linewidth=1, where='post')
    ax.grid(True)
    plt.show()
    #fig.savefig('sniff.png')
    #plt.close(fig)    # close the figure    
    pi.stop()

if __name__ == "__main__":
    main()