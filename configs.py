__author__ = 'bilibili'

import math

CPU_CLOCK = 2 * 2 ** 30  # 2GHz
CLOCK_CYCLE = 1000       # 1000ticks per cycle

L2_SIZE = 4 * 2 ** 20    # 4MB as default
L2_ASSOC = 8             # Associativity
L2_RW_LATENCY = 1        # cycles
L2_ACCESS_LATENCY = 6    # cycles
L2_SHIFT_LATENCY = 1     # cycles

BYTE_SIZE = 8

ADDRESS_BITS = 32

TAPE_DOMAIN = 64  # # of domains on a tape
GROUP_TAPE = 512  # # of tapes in a group
GROUP_NUM = L2_SIZE / (GROUP_TAPE * TAPE_DOMAIN)
LINE_NUM = GROUP_NUM * TAPE_DOMAIN
SET_LINE_NUM = L2_ASSOC
SET_NUM = LINE_NUM / SET_LINE_NUM

BLOCK_SIZE = GROUP_TAPE

OFFSET_BITS = math.log2(BLOCK_SIZE / BYTE_SIZE)
SET_BITS = math.log2(SET_NUM)
TAG_BITS = math.log2(ADDRESS_BITS) - SET_BITS - OFFSET_BITS

WR_PORT_SIZE = 12
W_PORT_SIZE = 8
R_PORT_SIZE = 4

