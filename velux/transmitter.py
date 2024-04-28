#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Trigger VELUX INTEGRA remote control via GPIO"""

import sys
from time import sleep
import pigpio as gpio

# define pigpio GPIO-pins where the remote control is connected
GPIO_STOP = 2
GPIO_OPEN = 3
GPIO_CLOSE = 4

# define pigpio-host 
HOST = "localhost"

# mapping of remote control command to GPIO pins
COMMANDS={
    'stop': GPIO_STOP,
    'open': GPIO_OPEN,
    'close': GPIO_CLOSE,
    }

def main(pin):
    """ main function """
    pi = gpio.pi(host=HOST)
    if not pi.connected:
        exit()

    # prepare GPIO-Pin
    pi.set_mode(pin, gpio.OUTPUT)
    sleep(0.2)

    pi.write(pin, 0)
    sleep(0.2)
    pi.write(pin, 1)

    pi.stop()

if __name__ == "__main__":
    try:
        if len(sys.argv) >= 2:
            cmd = sys.argv[1].lower()
            if cmd in COMMANDS:
                main(COMMANDS[cmd])
            else:
                print("Unknown command:", cmd)
        else:
            print("argument missing: open|close|down")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        # just make sure we don't transmit forever
        pi = gpio.pi(host=HOST)
        pi.stop()
    finally:
        #print("done")
        pass
