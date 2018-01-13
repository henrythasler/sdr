#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Decoder for Hideki TS33C Wireless Temperature/Humidity Sensor
    for Raspberry Pi with RXB8 Receiver
"""
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import os
import numpy as np

from time import sleep, time
from datetime import datetime

# used for further processing of received data
import matplotlib.pyplot as plt

SILENT = 0
ERROR = 1
INFO = 2
TRACE = 3


def write_png(filename, data, title=None):
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    fig.set_size_inches(16, 3)
    ax.set_title(title, fontsize=10)
    fig.text(0.5, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        fontsize=8, color='black',
        ha='center', va='bottom', alpha=0.4)
#    ax.step(data[0], data[1], linewidth=1, where='post')
    ax.plot(data[0], data[1], linewidth=1)
    ax.grid(True)
    plt.tight_layout()
    fig.savefig(filename)
    plt.close(fig)    # close the figure          

def main():
    """ main function """

    symbols = np.array([ 1028,   936,  1074,   862,  1122,   366,   510,   464,   522,
         950,   528,   448,  1040,   430,   550,   422,   518,   444,
         546,   454,   492,   970,   524,   442,   520,   472,   490,
         474,   494,   488,   988,   958,  1000,   474,   538,   438,
         496,   488,   478,   486,   502,   966,   506,   476,   982,
         972,   958,   988,   500,   486,   970,   506,   460,   982,
         986,   478,   480,   994,   478,   500,   956,   512,   468,
         502,   482,   484,   482,   996,   468,   514,   944,   512,
         464,   536,   450,   516,   456,   526,   460,   990,   946,
        1012,   942,  1012,   463,   511,   460,   512,   462,   514,
         464,   520,   956,   508,   458,  1000,   940,  1014,   950,
        1014,   926,  1020,   938,  1022,   442,   528,   450,   522,
         942,   538,   443,  1013,   934,   544,   430,   540,   456,
         512,   444,  1036,   430,   564,   914,   526,   442,   528,
         444,   556,   416,   543,   431,  1040,   438,   526,   436, 20318])

    pattern = np.array([ 972,   958,   988,   500,  478,   500,   956,   512,   468])

    res = np.convolve(symbols, pattern, mode='valid')

    write_png("test.png", [range(0,res.size), res], title=None)

if __name__ == "__main__":
    main()