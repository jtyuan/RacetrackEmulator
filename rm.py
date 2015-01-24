__author__ = 'bilibili'

from trace import Trace
from configs import *

'''
Some thoughts:
    when SRAM miss, the latency is SRAM accessing time
    when SRAM hits, the latency would only be DWM accessing time, SRAM is not in the critical path
'''


class RM:
    trace = Trace()
    target_line_num = -1
    target_group = 0

    count_down = 0

    r_port = []  # TODO need to modify to 2-dimensional array, 1st dimension for group, second for port in group
    w_port = []

    offset = []

    def next_trace(self, trace, target_line_num):
        # TODO check whether self.trace is a reference of trace, manually
        self.trace = trace
        self.target_line_num = target_line_num
        self.trace.state = 'accessing'
        self.count_down = 6000

    def shift(self):  # TODO
        return self.temp

    def next_cycle(self, tick):  # TODO
        self.count_down -= 1000
        if self.count_down == 0:  # ready to use L2
            if self.trace.instr == 'r':
                d = TAPE_LENGTH
                for i in self.r_port:



