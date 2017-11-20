#!/usr/bin/env python

import numpy as np

FILENAME = "TS33C_samples.dat"
SAMPLERATE = 20000

if __name__ == "__main__":
  rawData = [np.fromfile(FILENAME, dtype=np.byte)]
  if rawData[0].size > 0:
    # to-do
    # - handle high-levels at beginning

    # calculate edges from raw data; insert one at beginning for sync
    edges = np.insert(np.diff(rawData[0]),0,[0])

    # position (offset) of edges
    edge_positions = np.nonzero(edges)
    symbols = np.diff(edge_positions)[0]
    pulses = symbols[0::2]
    gaps = symbols[1::2]
    #print(edge_positions)
    print(pulses.size,pulses)
    print(gaps.size, gaps)
    #print(np.histogram(pulses, bins=[0,11,21,80,10000]))
