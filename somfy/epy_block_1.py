"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import scipy as sci
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, bit_length=1e-6):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Embedded Python Block',   # will show up in GRC
            in_sig=[np.byte],
            out_sig=[np.byte]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.bit_length = bit_length
        self.state = 0
        self.preamble = 0
        self.position = 0
        print("length of one sample", bit_length)
        

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        self.position = self.position + len(input_items[0])
        if self.state == 0:
            if sum(input_items[0]) > 0:
                self.preamble = sum(input_items[0])
                print("position of preamble",self.position-self.preamble)
                #print(len(input_items[0]), sum(input_items[0]))
                #print(input_items[0])
                self.state = 1 
                zeros = np.zeros(len(input_items[0]))
                zeros[np.nonzero(input_items[0])[0][0]]=1.
                output_items[0][:] = zeros
                #output_items[0][:] = np.gradient(input_items[0],0.5)
            else:
                output_items[0][:] = [0]
        elif self.state == 1:
            print(len(input_items[0]), sum(input_items[0]))
            if sum(input_items[0]) < len(input_items[0]):
                self.preamble = self.preamble + sum(input_items[0])
                self.state = 2
                print("length of preamble",self.preamble)
                output_items[0][:] = np.gradient(input_items[0],0.5)
            else:
                self.preamble = self.preamble + sum(input_items[0])
                output_items[0][:] = [1]
        else:
            output_items[0][:] = [1]
            
#            output_items[0][:] = input_items[0] * self.example_param
 #       else: 
#		output_items[0][:] = input_items[0] * self.example_param
        #output_items[0][:] = [2]
        return len(output_items[0])
