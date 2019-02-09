#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Decoder for Hideki TS33C Wireless Temperature/Humidity Sensor
    for Raspberry Pi with RXB8 Receiver
"""
import matplotlib
# Force matplotlib to not use any Xwindows backend.
#matplotlib.use('Agg')

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
    ax.step(data[0], data[1], linewidth=1, where='post')
#    ax.plot(data[0], data[1], linewidth=1)
    ax.grid(True)
    plt.tight_layout()
#    plt.show()
    fig.savefig(filename)
    #plt.close(fig)    # close the figure          

def main():
    """ main function """
    edge_positions = np.array([   229,    419,  19990,  20189,  23975,  24229,  30154,  30374,
        34669,  34834,  54310,  55490,  56295,  57345,  58250,  59285,
        59700,  60280,  60695,  61250,  62160,  62700,  63135,  64220,
        64605,  65120,  65575,  66135,  66555,  67110,  67530,  68100,
        69005,  69525,  69975,  70500,  70955,  71465,  71925,  72435,
        72905,  73905,  74875,  75845,  76325,  76825,  77305,  77805,
        78275,  78795,  79255,  79740,  80720,  81225,  81705,  82695,
        83645,  84645,  85605,  86080,  86585,  87560,  88050,  88530,
        89520,  90485,  90980,  91460,  91965,  92435,  93420,  94395,
        94890,  95375,  95875,  96330,  96840,  97315,  98310,  98780,
        99275, 100240, 100740, 101220, 101720, 102190, 102695, 103185,
       103680, 104140, 105145, 106095, 107095, 108065, 108560, 109040,
       109545, 110000, 110515, 110985, 111980, 112935, 113440, 113905,
       114420, 114885, 115885, 116835, 117835, 118295, 118820, 119765,
       120770, 121720, 122730, 123665, 124680, 125125, 125655, 126105,
       126645, 127080, 127620, 128070, 128585, 129055, 129560, 130495,
       131520, 131965, 132490, 132945, 133465, 134405, 134935, 135385,
       135905, 136370, 136890, 137335, 138350, 139285, 139815, 140260,
       141280, 141720, 162020])
    edges = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
       1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
       1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1,
       0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
       1, 0, 1, 0, 1, 0, 1, 0, 4])
    symbols = np.array([  190, 19571,   199,  3786,   254,  5925,   220,  4295,   165,
       19476,  1180,   805,  1050,   905,  1035,   415,   580,   415,
         555,   910,   540,   435,  1085,   385,   515,   455,   560,
         420,   555,   420,   570,   905,   520,   450,   525,   455,
         510,   460,   510,   470,  1000,   970,   970,   480,   500,
         480,   500,   470,   520,   460,   485,   980,   505,   480,
         990,   950,  1000,   960,   475,   505,   975,   490,   480,
         990,   965,   495,   480,   505,   470,   985,   975,   495,
         485,   500,   455,   510,   475,   995,   470,   495,   965,
         500,   480,   500,   470,   505,   490,   495,   460,  1005,
         950,  1000,   970,   495,   480,   505,   455,   515,   470,
         995,   955,   505,   465,   515,   465,  1000,   950,  1000,
         460,   525,   945,  1005,   950,  1010,   935,  1015,   445,
         530,   450,   540,   435,   540,   450,   515,   470,   505,
         935,  1025,   445,   525,   455,   520,   940,   530,   450,
         520,   465,   520,   445,  1015,   935,   530,   445,  1020,
         440, 20300])         
    """
array([  190, 19571,   199,  3786,   254,  5925,   220,  4295,   165,
       19476,  1180,   805,  1050,   905,  1035,   415,   580,   415,
         555,   910,   540,   435,  1085,   385,   515,   455,   560,
         420,   555,   420,   570,   905,   520,   450,   525,   455,
         510,   460,   510,   470,  1000,   970,   970,   480,   500,
         480,   500,   470,   520,   460,   485,   980,   505,   480,
         990,   950,  1000,   960,   475,   505,   975,   490,   480,
         990,   965,   495,   480,   505,   470,   985,   975,   495,
         485,   500,   455,   510,   475,   995,   470,   495,   965,
         500,   480,   500,   470,   505,   490,   495,   460,  1005,
         950,  1000,   970,   495,   480,   505,   455,   515,   470,
         995,   955,   505,   465,   515,   465,  1000,   950,  1000,
         460,   525,   945,  1005,   950,  1010,   935,  1015,   445,
         530,   450,   540,   435,   540,   450,   515,   470,   505,
         935,  1025,   445,   525,   455,   520,   940,   530,   450,
         520,   465,   520,   445,  1015,   935,   530,   445,  1020,
         440, 20300])
    """
    pulse_short = 460
    pulse_long = 989
    gap_short = 492
    gap_long = 998
    """
    pattern = np.array([ 500,   500,   500,   500,  500,   500,   500,   500,   500])
    pattern2 = np.array([ 500,   500,   500,   500,  500,   500,   500,   500,   500, 500,   500,   500,   500,  500,   500,   500,   500,   500, 500,   500,   500,   500,  500,   500,   500,   500,   500])
    pattern = np.array([ 1028,   936,  1074,   862,  1122,   366,   510,   464,   522])

    symbols = np.array([1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0,])
    zeros = np.array([0, 0, 0, 0, 0, 0])
    ones = np.array([1, 1, 1, 1, 1])
    pattern = np.array([0, 0, 0, 1, 0, 0])
    """

    #random = np.random.uniform(0,6000,size=100)
    #symbols = np.concatenate( (random, symbols, 6000-random) )

    #pattern = symbols[40:60]
    pattern = np.array([ pulse_long,  gap_long,   pulse_long,   gap_long,   pulse_long, gap_short, pulse_short, gap_short, pulse_short, gap_long, pulse_short])
    write_png("pattern.png", [np.cumsum(pattern), [1,0,1,0,1,0,1,0,1,0,1]])

    interp = np.interp(np.linspace(0, np.sum(pattern), 250), np.cumsum(pattern), [1,0,1,0,1,0,1,0,1,0,1])
    write_png("interp.png", [range(0,interp.size), interp])

    symbols_normalised = symbols - np.mean(symbols)
    pattern_normalised = pattern - np.mean(symbols)
    res = np.correlate(symbols_normalised, pattern_normalised)
    index = np.argmax(res)
    print("max=", index)

    write_png("correlate.png", [range(0,res.size), res], title=None)
    write_png("symbols.png", [range(0,symbols.size), symbols], title=None)

if __name__ == "__main__":
    main()