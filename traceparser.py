__author__ = 'bilibili'

from configs import Configs
from trace import Trace


def parse(trace):
    """
    parse(trace) - parse the given trace
    :param trace: one line of trace in the trace file
    :return: Trace object
    """
    args = trace.split()
    if args[0] == 'u':
        args[0] = 'w'
    return Trace(args[0], __addr_parse(int(args[1])), int(args[4]))


def __addr_parse(addr):
    """
    __addr_parse(addr) - extract tag/index/byte offset for the given address 'addr'
    :param addr: the address to parse
    :return: tag, index, byte offset of corresponding address
    """
    trace_bits = bin(addr)
    byte_offset = int(trace_bits[max(-Configs.OFFSET_BITS, 2 - len(trace_bits)):], 2)
    index = int(trace_bits[max(-(Configs.OFFSET_BITS + Configs.SET_BITS), 2 - len(trace_bits)):-Configs.OFFSET_BITS], 2)
    tag = trace_bits[2:-(Configs.OFFSET_BITS + Configs.SET_BITS)]
    if len(tag) > 0:
        tag = int(tag, 2)
    else:
        tag = 0
    if Configs.VERBOSE:
        if Configs.OUTPUT:
            Configs.OUT_FILE.write(
                'Instr tag: {0} index {1} offset{2}\n'.format(bin(tag)[2:], bin(index)[2:], bin(byte_offset)[2:]))
        print('Instr tag:', bin(tag)[2:], 'index:', bin(index)[2:], 'offset:', bin(byte_offset)[2:])
    return tag, index, byte_offset
