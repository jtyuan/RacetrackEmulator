__author__ = 'bilibili'

import math

CPU_CLOCK = 2 * 2 ** 30  # 2GHz
CLOCK_CYCLE = 1000       # 1000ticks per cycle

L2_SIZE = 4 * 2 ** 20    # 4MB as default
L2_ASSOC = 8             # Associativity
L2_R_LATENCY = 1         # cycles
L2_W_LATENCY = 1         # cycles
L2_ACCESS_LATENCY = 6    # cycles
L2_SHIFT_LATENCY = 1     # cycles
L2_MISS_PENALTY = 10    # cycles, equals to total access cycles for next level of cache/memory,
                         # also including cycles to update SRAM

BYTE_SIZE = 8            # bits of 1 byte

ADDRESS_BITS = 32        # address space bits

TAPE_DOMAIN = 64         # # of domains on a tape
TAPE_LENGTH = 80         # TODO
GROUP_TAPE = 512         # # of tapes in a group
GROUP_NUM = L2_SIZE // (GROUP_TAPE * TAPE_DOMAIN)  # # of groups
LINE_NUM = GROUP_NUM * TAPE_DOMAIN  # # of lines
SET_LINE_NUM = L2_ASSOC  # # of lines in one set
SET_NUM = LINE_NUM // SET_LINE_NUM  # # of sets

BLOCK_SIZE = GROUP_TAPE  # size (in bit) of a block

OFFSET_BITS = int(math.log2(BLOCK_SIZE // BYTE_SIZE))  # # of bits that byte offset takes in an address
SET_BITS = int(math.log2(SET_NUM))  # # of bits that set index takes in an address
TAG_BITS = int(math.log2(ADDRESS_BITS) - SET_BITS - OFFSET_BITS)  # # of bits that tag takes in an address

RW_PORT_SIZE = 12        # the size of a W/R port
W_PORT_SIZE = 8          # the size of a W port
R_PORT_SIZE = 4          # the size of a R port

RW_PORT_NUM = 4
R_PORT_NUM = 0
W_PORT_NUM = 0