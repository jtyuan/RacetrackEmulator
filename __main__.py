#!/usr/bin/env python3

__author__ = 'bilibili'

import argparse
import os

from configs import Configs
from l2cache import L2Cache


def add_arguments(parser):
    parser.add_argument('-t', '--tracefile', action='store', type=str,
                        help='The trace file to emulate with, this argument will be ignored is --directory is added')
    parser.add_argument('-d', '--directory', metavar='dir', action='store', type=str,
                        help='Emulate all trace files in the given directory, enable \
                        this will ignore trace-file argument')
    parser.add_argument('-o', '--output', metavar='outfile', action='store', type=str,
                        help="The file path to write emulation information to. \
                        Add -v to save the whole emulation detail.")
    parser.add_argument('--cpu-clock', action='store', type=str, default='2GHz',
                        help='Clock for blocks running at CPU speed(default="2GHz")')
    parser.add_argument('--clock-cycle', action='store', type=int, default=1000,
                        help='Ticks to run in one cycle(default=1000)')
    # parser.add_argument('--byte-size', action='store', type=int, default=8,
    # help='Size of byte in emulated system')
    # parser.add_argument('--address-bits', action='store', type=int, default=32)
    parser.add_argument('--tape-domain', action='store', type=int, default=64,
                        help='The domain# in one tape(default=64)')
    parser.add_argument('--tape-length', action='store', type=int, default=80,
                        help='The spacial length of each tape(default=80)')
    parser.add_argument('--group-tape', action='store', type=int, default=512,
                        help='The tape# in one group(default=512)')
    parser.add_argument('--l2-size', action='store', type=str, default='4MB',
                        help='The size of L2 Cache(default=4MB)')
    parser.add_argument('--l2-assoc', action='store', type=int, default=8,
                        help='The associativity of L2 Cache(default=8)')
    parser.add_argument('--l2-r-latency', action='store', type=int, default=1,
                        help='The read latency (cycle) of L2 Cache(default=1)')
    parser.add_argument('--l2-w-latency', action='store', type=int, default=1,
                        help='The write latency (cycle) of L2 Cache(default=1)')
    parser.add_argument('--l2-access-latency', action='store', type=int, default=6,
                        help='The assess latency (cycle) of L2 Cache(default=6)')
    parser.add_argument('--l2-shift-latency', action='store', type=int, default=1,
                        help='The shift latency (cycle) of L2 Cache RacetrackMemory(default=1)')
    parser.add_argument('--l2-miss-penalty', action='store', type=int, default=100,
                        help='The penalty (cycle) when a L2 Cache miss occurs(default=100)')
    parser.add_argument('-pm', '--port-mode', action='store', type=str, default='baseline',
                        choices=('baseline', 'rw', 'w+r', 'rw+r', 'rw+w+r', 'w+r+r'),
                        help='Determine how the r/w ports are placed on a tape')
    parser.add_argument('-ps', '--port-selection', action='store', type=str, default='dynamic',
                        choices=('dynamic', 'static'),
                        help='Port selection policy for every r/w instr')
    parser.add_argument('-pp', '--port-update-policy', action='store', type=str, default='lazy',
                        choices=('lazy', 'eager'),
                        help='The tape will remain where it is or move to default place after r/w operation')
    parser.add_argument('-sp', '--set_partition', action='store', type=str, default='con',
                        choices=('con', 'way'),
                        help='Set partitioning policy, "con" for continues, use "way" to '
                             'divide sets into different ways')
    parser.add_argument('-pre', '--preshift', action='store_true', help='Enable preshift for next i/o instr')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode, show debug info')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="racetrack")
    add_arguments(parser)
    args = parser.parse_args()

    if args.cpu_clock[-3:] == 'GHz':
        args.cpu_clock = int(args.cpu_clock[0:-3]) * 1000 ** 3
    elif args.cpu_clock[-3:] == 'MHz':
        args.cpu_clock = int(args.cpu_clock[0:-3]) * 1000 ** 2
    else:
        print('Wrong format of CPU Clock, check input')
        exit()

    if args.l2_size[-2:] == 'MB':
        args.l2_size = int(args.l2_size[0:-2]) * 2 ** 20
    elif args.l2_size[-2:] == 'kB':
        args.l2_size = int(args.l2_size[0:-2]) * 2 ** 10
    else:
        print('Wrong format of CPU Clock, check input')
        exit()

    Configs.CPU_CLOCK = args.cpu_clock
    Configs.CLOCK_CYCLE = args.clock_cycle
    # Configs.BLOCK_SIZE = args.byte_size
    # Configs.ADDRESS_BITS = args.address_bits
    Configs.TAPE_DOMAIN = args.tape_domain
    Configs.TAPE_LENGTH = args.tape_length
    Configs.GROUP_TAPE = args.group_tape
    Configs.L2_SIZE = args.l2_size
    Configs.L2_ASSOC = args.l2_assoc
    Configs.L2_R_LATENCY = args.l2_r_latency
    Configs.L2_W_LATENCY = args.l2_r_latency
    Configs.L2_ACCESS_LATENCY = args.l2_access_latency
    Configs.L2_SHIFT_LATENCY = args.l2_shift_latency
    Configs.L2_MISS_PENALTY = args.l2_miss_penalty

    Configs.reload_attr()

    Configs.PORT_MODE = args.port_mode
    Configs.PORT_SELECTION = args.port_selection
    Configs.PORT_UPDATE_POLICY = args.port_update_policy
    Configs.SET_PARTITION = args.set_partition

    if args.preshift:
        Configs.PRESHIFT = True

    if args.output:
        Configs.OUTPUT = True
        Configs.OUT_FILE = open(os.path.abspath(args.output), 'w')

    if args.verbose is True:
        Configs.VERBOSE = True

    if not args.directory:
        if not args.tracefile:
            print('error: the following arguments are required: trace-file')
        else:
            if Configs.OUTPUT:
                Configs.OUT_FILE.write('Trace file: {0}\n'.format(args.tracefile))
            print('Trace file:', args.tracefile)
            l2cache = L2Cache(args.tracefile)
            while True:
                if not l2cache.next_cycle():
                    break
    else:
        Configs.TRACE_DIR = args.directory
        if Configs.OUTPUT:
            Configs.OUT_FILE.write('Trace dir: {0}\n'.format(Configs.TRACE_DIR))
        print('Trace dir:', Configs.TRACE_DIR)
        for trace in os.listdir(Configs.TRACE_DIR):
            if trace[-6:] == '.trace':
                if Configs.OUTPUT:
                    Configs.OUT_FILE.write('Trace File: {0}\n'.format(trace))
                print('Trace File:', trace)
                l2cache = L2Cache(os.path.join(Configs.TRACE_DIR, trace))
                while True:
                    if not l2cache.next_cycle():
                        break

