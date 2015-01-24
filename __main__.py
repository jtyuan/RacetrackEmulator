__author__ = 'bilibili'

import argparse
import configs

from l2cache import L2Cache


def add_arguments(parser):
    # system options
    parser.add_argument('--cpu-clock', action='store', type=str, default='2GHz')
    parser.add_argument('--clock-cycle', action='store', type=int, default=1000)
    parser.add_argument('--byte-size', action='store', type=int, default=8)
    parser.add_argument('--address-bits', action='store', type=int, default=32)
    parser.add_argument('--tape-domain', action='store', type=int, default=64)
    parser.add_argument('--tape-length', action='store', type=int, default=80)
    parser.add_argument('--group-tape', action='store', type=int, default=512)
    parser.add_argument('--l2_size', action='store', type=str, default='4MB')
    parser.add_argument('--l2_assoc', action='store', type=int, default=8)
    parser.add_argument('--l2_r_latency', action='store', type=int, default=1)
    parser.add_argument('--l2_w_latency', action='store', type=int, default=1)
    parser.add_argument('--l2_access_latency', action='store', type=int, default=6)
    parser.add_argument('--l2_shift_latency', action='store', type=int, default=1)
    parser.add_argument('--l2_miss_latency', action='store', type=int, default=100)
    parser.add_argument('-v', '--verbose', action='store_true')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="racetrack")
    add_arguments(parser)
    args = parser.parse_args()

    configs.CLOCK_CYCLE = args.clock_cycle
    configs.BLOCK_SIZE = args.byte_size
    configs.ADDRESS_BITS = args.address_bits
    configs.TAPE_DOMAIN = args.tape_domain
    configs.TAPE_LENGTH = args.tape_length
    configs.GROUP_TAPE = args.group_tape
    configs.L2_SIZE = args.l2_size
    configs.L2_ASSOC = args.l2_assoc
    configs.L2_R_LATENCY = args.l2_r_latency
    configs.L2_W_LATENCY = args.l2_r_latency
    configs.L2_ACCESS_LATENCY = args.l2_access_latency
    configs.L2_SHIFT_LATENCY = args.l2_shift_latency
    configs.L2_MISS_PENALTY = args.l2_miss_latency

    if args.verbose:
        configs.VERBOSE = True

    l2cache = L2Cache('trace/482.sphinx3.trace')
    while True:
        if not l2cache.next_cycle():
            break