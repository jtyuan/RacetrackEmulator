#!/usr/bin/env python3

__author__ = 'bilibili'

import argparse

from configs import Configs
from l2cache import L2Cache


def add_arguments(parser):
    parser.add_argument('--trace-file', action='store', type=str)
    parser.add_argument('--cpu-clock', action='store', type=str, default='2GHz')
    parser.add_argument('--clock-cycle', action='store', type=int, default=1000)
    parser.add_argument('--byte-size', action='store', type=int, default=8)
    parser.add_argument('--address-bits', action='store', type=int, default=32)
    parser.add_argument('--tape-domain', action='store', type=int, default=64)
    parser.add_argument('--tape-length', action='store', type=int, default=80)
    parser.add_argument('--group-tape', action='store', type=int, default=512)
    parser.add_argument('--l2-size', action='store', type=str, default='4MB')
    parser.add_argument('--l2-assoc', action='store', type=int, default=8)
    parser.add_argument('--l2-r-latency', action='store', type=int, default=1)
    parser.add_argument('--l2-w-latency', action='store', type=int, default=1)
    parser.add_argument('--l2-access-latency', action='store', type=int, default=6)
    parser.add_argument('--l2-shift-latency', action='store', type=int, default=1)
    parser.add_argument('--l2-miss-latency', action='store', type=int, default=100)
    parser.add_argument('--port-mode', action='store', type=str, default='rw')
    parser.add_argument('-v', '--verbose', action='store_true')


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
    Configs.BLOCK_SIZE = args.byte_size
    Configs.ADDRESS_BITS = args.address_bits
    Configs.TAPE_DOMAIN = args.tape_domain
    Configs.TAPE_LENGTH = args.tape_length
    Configs.GROUP_TAPE = args.group_tape
    Configs.L2_SIZE = args.l2_size
    Configs.L2_ASSOC = args.l2_assoc
    Configs.L2_R_LATENCY = args.l2_r_latency
    Configs.L2_W_LATENCY = args.l2_r_latency
    Configs.L2_ACCESS_LATENCY = args.l2_access_latency
    Configs.L2_SHIFT_LATENCY = args.l2_shift_latency
    Configs.L2_MISS_PENALTY = args.l2_miss_latency
    Configs.PORT_MODE = args.port_mode

    if args.verbose is True:
        Configs.VERBOSE = True

    if not args.trace_file:
        print('Trace file path needed: --trace-file="/path/to/file"')
    else:
        l2cache = L2Cache(args.trace_file)
        while True:
            if not l2cache.next_cycle():
                break