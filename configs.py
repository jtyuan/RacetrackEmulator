__author__ = 'bilibili'

import math


class Configs:
    CPU_CLOCK = 2 * 1000 ** 3  # 2GHz
    CLOCK_CYCLE = 1000       # 1000ticks per cycle

    L2_SIZE = 4 * 2 ** 20    # 4MB as default
    L2_ASSOC = 8             # Associativity
    L2_R_LATENCY = 1         # cycles
    L2_W_LATENCY = 1         # cycles
    L2_ACCESS_LATENCY = 6    # cycles
    L2_SHIFT_LATENCY = 1     # cycles
    L2_MISS_PENALTY = 100    # cycles, equals to total access cycles for next level of cache/memory,
                             # also including cycles to update SRAM

    BYTE_SIZE = 8            # bits of 1 byte

    ADDRESS_BITS = 32        # address space bits

    TAPE_DOMAIN = 64         # # of domains on a tape
    TAPE_LENGTH = 80         # unimportant in simulation
    GROUP_TAPE = 512         # # of tapes in a group

    GROUP_NUM = L2_SIZE // (GROUP_TAPE * TAPE_DOMAIN)  # # of groups
    LINE_NUM = GROUP_NUM * TAPE_DOMAIN  # # of lines
    SET_LINE_NUM = L2_ASSOC  # # of lines in one set
    SET_NUM = LINE_NUM // SET_LINE_NUM  # # of sets

    BLOCK_SIZE = GROUP_TAPE  # size (in bit) of a block

    OFFSET_BITS = int(math.log2(BLOCK_SIZE // BYTE_SIZE))  # # of bits that byte offset takes in an address
    SET_BITS = int(math.log2(SET_NUM))  # # of bits that set index takes in an address
    TAG_BITS = int(math.log2(ADDRESS_BITS) - SET_BITS - OFFSET_BITS)  # # of bits that tag takes in an address

    PORT_MODE = 'baseline'  # rw - only rw ports; rw+r - rw ports and r ports; w+r - w ports and r ports
    PORT_SELECTION = 'dynamic'   # static - move to given port; dynamic - move to nearest port
    # PORT_UPDATE_POLICY = 'lazy'  # eager - move back to fixed position after r/w; lazy - stay where the last r/w happens
    SET_PARTITION = 'con'  # con - continuous, way - separate by ways

    REPLACE_POLICY = 'LRU'

    TRACE_DIR = 'trace'

    VERBOSE = False

    @staticmethod
    def print_info():
        print('-----------------------------\n  Emulation System Summary:')
        cpu_clock = '2GHz'
        if Configs.CPU_CLOCK >= 1000 ** 3:
            cpu_clock = str(Configs.CPU_CLOCK // (1000 ** 3)) + 'GHz'
        elif Configs.CPU_CLOCK >= 1000 ** 2:
            cpu_clock = str(Configs.CPU_CLOCK // (1000 ** 2)) + 'MHz'
        else:
            cpu_clock = str(Configs.CPU_CLOCK) + 'Hz'
        print('  CPU Clock:', cpu_clock)
        print('  Clock Cycle:', Configs.CLOCK_CYCLE)
        l2_size = '4MB'
        if Configs.L2_SIZE >= 2 ** 20:
            l2_size = str(Configs.L2_SIZE // (2 ** 20)) + 'MB'
        elif Configs.L2_SIZE >= 2 ** 10:
            l2_size = str(Configs.L2_SIZE // (2 ** 10)) + 'kB'
        else:
            l2_size = str(Configs.L2_SIZE) + 'Bytes'
        print('  L2 Size:', l2_size)
        print('  L2 Associativity:', Configs.L2_ASSOC)
        print('  L2 Read/Write Latency: {0}/{1}'.format(Configs.L2_R_LATENCY, Configs.L2_W_LATENCY))
        print('  L2 Access Latency:', Configs.L2_ACCESS_LATENCY)
        print('  L2 Shift Latency:', Configs.L2_SHIFT_LATENCY)
        print('  L2 Miss Penalty:', Configs.L2_MISS_PENALTY)
        print('  Port Placement Mode:', Configs.PORT_MODE)
        print('  Port Selection:', Configs.PORT_SELECTION)
        print('  Set Partition:', Configs.SET_PARTITION)
        print('  Replace Policy:', Configs.REPLACE_POLICY)
        print('  Verbose mode:', Configs.VERBOSE)
        print('-----------------------------\n')

