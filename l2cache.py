__author__ = 'bilibili'

import os

from configs import *
from traceparser import parse
from trace import Trace
from sram import SRAM
from rm import RM


class L2Cache:
    EOF = False
    trace_count = 0

    def __init__(self, trace_file):
        """
        __init__(trace_file) - constructor
        :param trace_file: the path of the trace file to emulate
        """
        self.trace_file = open(os.path.abspath(trace_file), 'r')
        self.sram = SRAM(LINE_NUM)
        self.rm = RM(self.sram)

        print('Starting up')
        if VERBOSE:
            print('\nCurrent tick: 0')
            print('Trace state: current(unfetched) next(unfetched)\n')

        self.current_trace = Trace()
        if VERBOSE:
            print('Fetching the first trace')
        self.waiting_trace = parse(self.trace_file.readline())
        self.next_trace()  # get 1st trace
        # set current_tick to one cycle before the first trace
        self.current_tick = self.current_trace.start_tick // CLOCK_CYCLE * CLOCK_CYCLE
        if self.current_tick == self.current_trace.start_tick:
            self.current_tick -= CLOCK_CYCLE

    def next_trace(self):
        """
        next_trace() - start process next trace & pre fetch the 2nd next trace
        """

        self.trace_count += 1
        if VERBOSE:
            print('Start process waiting trace')
            print('Executing the {0}th trace'.format(self.trace_count))

        if self.trace_count % 1000 == 0:
            print('**Executing the {0}th trace**'.format(self.trace_count))

        self.current_trace = self.waiting_trace

        next_line = self.trace_file.readline()

        if not next_line:
            self.EOF = True
            print('No more traces left')
            self.waiting_trace = Trace(instr='EOF')
        else:
            if VERBOSE:
                print('Pre-fetching next trace')
            self.waiting_trace = parse(next_line)
        self.rm.next_trace(self.current_trace, self.waiting_trace)

    def next_cycle(self):
        """
        next_cycle() - move the clock to next cycle, do what ever should be done in this cycle
        :return:
        """
        self.current_tick += CLOCK_CYCLE

        if VERBOSE:
            print('\nCurrent tick:', self.current_tick)

        self.rm.next_cycle(self.current_tick)

        if self.current_trace.state == 'finished' and self.EOF:
            print('\nEmulation Complete')
            print('total cycles:', self.current_tick // CLOCK_CYCLE)
            print('total shifts:', self.rm.total_shifts)
            print('total shift distance:', self.rm.total_shift_dis)
            print('total access:', self.rm.access_count)
            print('total misses:', self.rm.miss_count)
            return False

        if self.current_trace.state == 'finished' and self.waiting_trace.state == 'ready':
            # for t, k in zip(self.sram.tags, range(len(self.sram.tags))):
            # if t is not None:
            #         print(t, k)
            self.next_trace()

        if self.waiting_trace.state != 'ready':
            # TODO pre-fetch logic
            dummy = 1
        return True

    def boost_cycle(self, num=1000):
        """
        boost_cycle(num) - move the cycle forward by 'num', DEBUG use
        :param num: cycles to move forward
        :return: None
        """
        self.current_tick += CLOCK_CYCLE * num