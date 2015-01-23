__author__ = 'bilibili'

import os

from configs import *
from traceparser import parse
from trace import Trace
from sram import SRAM
from rm import RM


class L2Cache:
    current_trace = Trace()
    waiting_trace = Trace()
    current_tick = 0

    def __init__(self, trace_file):
        self.trace_file = open(os.path.abspath(trace_file), 'r')
        self.sram = SRAM(LINE_NUM)
        self.rm = RM()

        self.next_trace()  # get 1st trace
        # set current_tick to one cycle before the first trace
        self.current_tick = self.waiting_trace.tick // 1000 * 1000
        if self.current_tick == self.waiting_trace.tick:
            self.current_tick -= 1000

    def next_trace(self):
        self.current_trace = self.waiting_trace
        self.waiting_trace = parse(self.trace_file.readline())

    def next_cycle(self):
        self.current_tick += 1000

        # # the current trace finished, and next one is ready
        # if self.current_tick >= self.current_trace.finish_tick:
        #     self.current_trace.state = 'finished'
        #
        # if self.current_tick >= self.waiting_trace.tick:
        #     self.current_trace.state = 'ready'

        self.rm.next_cycle()

        if self.current_trace.state == 'finished' and self.waiting_trace.state == 'ready':
            self.next_trace()
            self.current_trace.state = 'accessing'
            self.rm.set_trace(self.current_trace,
                              self.sram.compare_tag(self.current_trace.tag, self.current_trace.index))

    @staticmethod
    def set_line_numbers(index):
        """
        set_lines(index) - get line numbers of one set, given set index
        :param index: set index
        :return: line numbers belong to this set
        """
        for i in range(L2_ASSOC):
            yield index + i