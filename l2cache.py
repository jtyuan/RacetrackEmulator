#!/usr/bin/env python3
__author__ = 'bilibili'

import os

from configs import *
from traceparser import parse
from trace import Trace
from sram import SRAM
from rm import RM


class L2Cache:
    def __init__(self, trace_file):
        """
        __init__(trace_file) - constructor
        :param trace_file: the path of the trace file to emulate
        """

        # initialization
        self.EOF = False
        self.trace_count = 0

        self.trace_file = open(os.path.abspath(trace_file), 'r')

        if not self.trace_file:
            print('Trace file not exist, please check path:', os.path.abspath(trace_file))
            self.EOF = True

        self.sram = SRAM(Configs.LINE_NUM)
        self.rm = RM(self.sram)

        Configs.print_info()

        if Configs.OUTPUT:
            Configs.OUT_FILE.write('**Emulation Start**\n');
        print('**Emulation Start**')
        if Configs.VERBOSE:
            if Configs.OUTPUT:
                Configs.OUT_FILE.write('\nCurrent tick: 0\n')
                Configs.OUT_FILE.write('Trace state: current(unfetched) next(unfetched)\n\n')
            print('\nCurrent tick: 0')
            print('Trace state: current(unfetched) next(unfetched)\n')

        self.current_trace = Trace()
        if Configs.VERBOSE:
            if Configs.OUTPUT:
                Configs.OUT_FILE.write('Fetching the first trace\n')
            print('Fetching the first trace')
        self.waiting_trace = parse(self.trace_file.readline())
        self.next_trace()  # get 1st trace
        # set current_tick to one cycle before the first trace
        self.current_tick = self.current_trace.start_tick // Configs.CLOCK_CYCLE * Configs.CLOCK_CYCLE
        if self.current_tick == self.current_trace.start_tick:
            self.current_tick -= Configs.CLOCK_CYCLE

    def next_trace(self):
        """
        next_trace() - start process next trace & pre fetch the 2nd next trace
        """

        self.trace_count += 1
        if Configs.VERBOSE:
            if Configs.OUTPUT:
                Configs.OUT_FILE.write('Start process waiting trace\n')
                Configs.OUT_FILE.write('Executing the {0}th trace\n'.format(self.trace_count))
            print('Start process waiting trace')
            print('Executing the {0}th trace'.format(self.trace_count))

        if self.trace_count % 100000 == 0:
            print('**Executing the {0}th trace**'.format(self.trace_count))

        self.current_trace = self.waiting_trace

        next_line = self.trace_file.readline()

        if not next_line:
            self.EOF = True
            print('No more traces left')
            self.waiting_trace = Trace(instr='EOF')
        else:
            if Configs.VERBOSE:
                if Configs.OUTPUT:
                    Configs.OUT_FILE.write('Pre-fetching next trace\n')
                print('Pre-fetching next trace')
            self.waiting_trace = parse(next_line)
        self.rm.next_trace(self.current_trace, self.waiting_trace)

    def next_cycle(self):
        """
        next_cycle() - move the clock to next cycle, do what ever should be done in this cycle
        :return:
        """
        self.current_tick += Configs.CLOCK_CYCLE

        if Configs.VERBOSE:
            if Configs.OUTPUT:
                Configs.OUT_FILE.write('\nCurrent tick: {0}\n'.format(self.current_tick))
            print('\nCurrent tick:', self.current_tick)

        self.rm.next_cycle(self.current_tick)

        if self.current_trace.state == 'finished' and self.EOF:
            if Configs.OUTPUT:
                Configs.OUT_FILE.write('\n**Emulation Complete**\n')
                Configs.OUT_FILE.write('secs emulated: {0}\n'.format(self.current_tick / Configs.CPU_CLOCK))
                Configs.OUT_FILE.write('total cycles: {0}\n'.format(self.current_tick // Configs.CLOCK_CYCLE))
                Configs.OUT_FILE.write('total shifts: {0}\n'.format(self.rm.total_shifts))
                Configs.OUT_FILE.write('total shift overhead: {0}\n'.format(self.rm.total_shift_dis))
                Configs.OUT_FILE.write('total access: {0}\n'.format(self.rm.access_count))
                Configs.OUT_FILE.write('total misses: {0}\n'.format(self.rm.miss_count))
                Configs.OUT_FILE.write('**********************\n')
            print('\n**Emulation Complete**')
            print('secs emulated:', self.current_tick / Configs.CPU_CLOCK)
            print('total cycles:', self.current_tick // Configs.CLOCK_CYCLE)
            print('total shifts:', self.rm.total_shifts)
            print('total shift overhead:', self.rm.total_shift_dis)
            print('total access:', self.rm.access_count)
            print('total misses:', self.rm.miss_count)
            print('**********************')
            return False

        if self.current_trace.state == 'finished' and self.waiting_trace.state == 'ready':
            self.next_trace()

        return True

    def boost_cycle(self, num=1000):
        """
        boost_cycle(num) - move the cycle forward by 'num', for DEBUG use
        :param num: cycles to move forward
        :return: None
        """
        self.current_tick += Configs.CLOCK_CYCLE * num
        print('Current tick:', self.current_tick)