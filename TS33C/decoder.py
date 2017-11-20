"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, sample_rate=1.0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Decoder Block',   # will show up in GRC
            in_sig=[np.byte],
            out_sig=[np.byte]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.sample_rate = sample_rate
        self.state = 0
        self.absolute_position = 0
        self.decoded_bits = np.array([0])

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        
        edges = np.insert(np.diff(input_items[0]),0,[0])
        edge_positions = np.nonzero(edges)

        if np.count_nonzero(edges) > 0:
            edge_positions += np.array(self.absolute_position)
            print(edge_positions)

        #output_items[0][:] = input_items[0] * self.example_param
        output_items[0][:] = edges

        self.absolute_position = self.absolute_position + len(input_items[0])
        return len(output_items[0])
