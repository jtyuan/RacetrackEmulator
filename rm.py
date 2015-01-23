__author__ = 'bilibili'

from trace import Trace

'''
Some thoughts:
    when SRAM miss, the latency is SRAM accessing time
    when SRAM hits, the latency would only be DWM accessing time, SRAM is not in the critical path
'''

class RM:
    temp = 0

    trace = Trace()
    target_line_num = -1

    def __init__(self):
        self.temp = 1

    def set_trace(self, trace, target_line_num):
        # check whether self.trace is a reference of trace
        self.trace = trace
        self.target_line_num = target_line_num

    def shift(self):  # TODO
        return self.temp

    def next_cycle(self):  # TODO
        self.trace.state = 'xx'
