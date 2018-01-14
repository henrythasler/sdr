#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pigpio as gpio
from time import sleep

pi = None

def cbf(pin, level, tick):
    global pi
    if level < 2:
        pass
    else:
        pi.write(27, 1)
        sleep(.01)
        pi.write(27, 0)

def main():
    """ main function """
    global pi
    pi = gpio.pi(host="rfpi", port=8888)
    if not pi.connected:
        exit()

    pin = 17

    pi.set_mode(27, gpio.OUTPUT) 

    # initialize timestamp for further use
    start_tick = pi.get_current_tick()

    pi.set_glitch_filter(pin, 300)

    # detect frame gap to try decoding of received data
    pi.set_watchdog(pin, 52)

    # watch pin
    callback = pi.callback(pin, gpio.EITHER_EDGE, cbf)

    # wait for something to happen, forever...
    active = True

    try:
        while active:
            sleep(1)
    except KeyboardInterrupt:
        print "cancel"

if __name__ == "__main__":
    main()