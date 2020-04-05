#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Transmit mumbi power outlet codes"""

import sys
from time import sleep
import pigpio as gpio
from lib.rfm69 import Rfm69
import numpy as np

# define pigpio GPIO-pins where RESET- and DATA-Pin of RFM69-Transceiver are connected
RESET = 24
DATA = 25

# define pigpio-host 
HOST = "localhost"

COMMANDS={
    'a_on': [0x19, 0x10, 0x0F, 0x09, 0x00],
    'a_off': [0x19, 0x10, 0x0E, 0x08, 0x00],
    'b_on': [0x19, 0x10, 0x0D, 0x0A, 0x00],
    'b_off': [0x19, 0x10, 0x0C, 0x0B, 0x00],
    'c_on': [0x19, 0x10, 0x0B, 0x0E, 0x00],
    'c_off': [0x19, 0x10, 0x0A, 0x0F, 0x00],
    'd_on': [0x19, 0x10, 0x07, 0x01, 0x00],
    'd_off': [0x19, 0x10, 0x06, 0x00, 0x00],
    'all_on': [0x19, 0x10, 0x04, 0x03, 0x00],
    'all_off': [0x19, 0x10, 0x08, 0x0D, 0x00]
    }

def main(code):
    """ main function """
    pi = gpio.pi(host=HOST)
    if not pi.connected:
        exit()

    # prepare GPIO-Pins
    pi.set_mode(RESET, gpio.OUTPUT)
    pi.set_mode(DATA, gpio.OUTPUT)
    pi.set_pull_up_down(DATA, gpio.PUD_OFF)
    pi.write(DATA, 0)

    # reset transmitter before use
    pi.write(RESET, 1)
    pi.write(RESET, 0)
    sleep(.005)

    with Rfm69(host=HOST, channel=0, baudrate=32000, debug_level=0) as rf:
        # just to make sure SPI is working
        rx_data = rf.read_single(0x5A)
        if rx_data != 0x55:
            print("SPI Error")

        rf.write_single(0x01, 0b00000100)     # OpMode: STDBY

        rf.write_burst(0x07, [0x6C, 0x80, 0x12]) # Frf: Carrier Frequency 433.93MHz

        # Use PA_BOOST
        rf.write_single(0x13, 0x0F)
        rf.write_single(0x5A, 0x5D)
        rf.write_single(0x5C, 0x7C)
        rf.write_single(0x11, 0b01111111)     # Use PA_BOOST

        rf.write_single(0x18, 0b00000110)     # Lna: 50 Ohm, highest gain
        rf.write_single(0x19, 0b01000000)     # RxBw: 4% DCC, BW=250kHz

        # Transmit Mode
        rf.write_single(0x02, 0b01101000)     # DataModul: continuous w/o bit sync, OOK, no shaping
        rf.write_single(0x01, 0b00001100)     # OpMode: SequencerOn, TX

        # wait for ready
        while (rf.read_single(0x27) & 0x80) == 0:
            pass
            #print "waiting..."

        # delete existing waveforms
        pi.wave_clear()

        # calculate frame-data from command-line arguments
        data = np.empty(0, dtype=np.uint8)
        for item in code:
            data = np.append(data, np.array(int(item), dtype=np.uint8))
        # how many consecutive frame repetitions
        repetitions = 8

        # create "0" pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 333), gpio.pulse(0, 1<<DATA, 667)])
        zero = pi.wave_create()

        # create "1" pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 667), gpio.pulse(0, 1<<DATA, 333)])
        one = pi.wave_create()

        # create preamble pulse waveform
        pi.wave_add_generic([gpio.pulse(0, 1<<DATA, 10000)])
        pause = pi.wave_create()

        # create bitstream from data
        bits = np.where(np.unpackbits(data) == 1, one, zero)

        # use only 34 bit
        bits = bits[:34]

        # assemble whole frame sequence including repetitions
        frames = np.concatenate(([255, 0], bits, [pause], [255, 1, repetitions, 0]))

        # send frames
        pi.wave_chain(frames.tolist())

        # wait until finished
        while pi.wave_tx_busy():
            sleep(0.1)

        # clean up
        pi.wave_delete(zero)
        pi.wave_delete(one)
        pi.wave_delete(pause)

    # reset transmitter
    pi.write(RESET, 1)
    pi.write(RESET, 0)
    sleep(.005)
    pi.stop()

if __name__ == "__main__":
    try:
        if sys.argv[1] in COMMANDS:
            main(COMMANDS[sys.argv[1]])
        else:
            print("Unknown command:", sys.argv[1])
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        # just make sure we don't transmit forever
        pi = gpio.pi(host=HOST)
        pi.write(DATA, 0)
        pi.stop()
    finally:
        #print "done"
        pass
