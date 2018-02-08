#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Transmit mumbi power outlet codes"""

import sys
from struct import pack
from time import sleep
import pigpio as gpio
from lib.rfm69 import Rfm69
import numpy as np
import json

# define pigpio GPIO-pins where RESET- and DATA-Pin of RFM69-Transceiver are connected
RESET = 24
DATA = 25

# define pigpio-host 
HOST = "rfpi"

COMMANDS={
    'null': 0x00,
    'up': 0x02,
    'down': 0x04,
    'stop': 0x01,
    'prog': 0x08,
    }

config=None

clock = 640    

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

    # load current config
    with open("config.json") as f:
        try:
            config = json.load(f)
        except:
            config = {"rolling_code": 0, "key": 10, "address": 1}

    # update config
    config["rolling_code"] += 1

    # write new config
    with open("config.json", "w") as f:
        json.dump(config, f)

    with Rfm69(host=HOST, channel=0, baudrate=32000, debug_level=0) as rf:
        # just to make sure SPI is working
        rx_data = rf.read_single(0x5A)
        if rx_data != 0x55:
            print "SPI Error"

        rf.write_single(0x01, 0b00000100)     # OpMode: STDBY

        rf.write_burst(0x07, [0x6C, 0x9A, 0x00]) # Frf: Carrier Frequency 434.42MHz

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
        data = pack(">BBH", config["key"] | (config["rolling_code"] & 0x0f), code << 4, config["rolling_code"]) 
        data += pack("<I",config["address"])[:-1]
        frame = np.fromstring(data, dtype=np.uint8)

        # checksum calculation
        cksum = frame[0] ^ (frame[0] >> 4)
        for i in range(1,7):
            cksum = cksum ^ frame[i] ^ (frame[i] >> 4)
        frame[1] = frame[1] | (cksum & 0x0f)
        print "Data: "+''.join('0x{:02X} '.format(x) for x in frame)

        # data whitening/obfuscation
        for i in range(1, frame.size):
            frame[i] = frame[i] ^ frame[i-1]

        print "Frame: "+''.join('0x{:02X} '.format(x) for x in frame)

        # how many consecutive frame repetitions
        repetitions = 3

        # create wakeup pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 10000), gpio.pulse(0, 1<<DATA, 95000)])
        wakeup = pi.wave_create()

        # create hw_sync pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 2500), gpio.pulse(0, 1<<DATA, 2500)])
        hw_sync = pi.wave_create()

        # create sw_sync pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, 4850), gpio.pulse(0, 1<<DATA, clock)])
        sw_sync = pi.wave_create()

        # create "0" pulse waveform
        pi.wave_add_generic([gpio.pulse(1<<DATA, 0, clock), gpio.pulse(0, 1<<DATA, clock)])
        zero = pi.wave_create()

        # create "1" pulse waveform
        pi.wave_add_generic([gpio.pulse(0, 1<<DATA, clock), gpio.pulse(1<<DATA, 0, clock)])
        one = pi.wave_create()

        # create "eof" pulse waveform
        pi.wave_add_generic([gpio.pulse(0, 1<<DATA, clock)])
        eof = pi.wave_create()

        # create "inter-frame gap" pulse waveform
        pi.wave_add_generic([gpio.pulse(0, 1<<DATA, 32000)])
        gap = pi.wave_create()

        # create bitstream from frame
        bits = np.where(np.unpackbits(frame) == 1, one, zero)

        # assemble whole frame sequence
        frames = np.concatenate((
                [wakeup], 
                [hw_sync, hw_sync], 
                [sw_sync], 
                bits,                   # send at least once
                [eof],                  # start 
                [gap],   # inter-frame gap
                [255, 0],               # start loop
                    [255, 0], 
                        [hw_sync], 
                    [255, 1, 7, 0],
                    [sw_sync], 
                    bits, 
                    [eof], 
                    [gap],   # inter-frame gap
                [255, 1, repetitions, 0]    # repeat 
                ))

        # send frames
        pi.wave_chain(frames.tolist())

        # wait until finished
        while pi.wave_tx_busy():
            sleep(0.1)

        # clean up
        pi.wave_delete(zero)
        pi.wave_delete(one)
        pi.wave_delete(wakeup)
        pi.wave_delete(hw_sync)
        pi.wave_delete(sw_sync)
        pi.wave_delete(eof)
        pi.wave_delete(gap)

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
            print "Unknown command:", sys.argv[1]
    except KeyboardInterrupt:
        print "KeyboardInterrupt"
        # just make sure we don't transmit forever
        pi = gpio.pi(host=HOST)
        pi.write(DATA, 0)
        pi.stop()
    finally:
        #print "done"
        pass
