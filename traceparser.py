__author__ = 'bilibili'

from configs import OFFSET_BITS, SET_BITS, VERBOSE
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
    byte_offset = int(trace_bits[max(-OFFSET_BITS, 2-len(trace_bits)):], 2)
    index = int(trace_bits[max(-(OFFSET_BITS + SET_BITS), 2-len(trace_bits)):-OFFSET_BITS], 2)
    tag = trace_bits[2:-(OFFSET_BITS + SET_BITS)]
    if len(tag) > 0:
        tag = int(tag, 2)
    else:
        tag = 0
    if VERBOSE:
        print('Instr tag:', bin(tag)[2:], 'index:', bin(index)[2:], 'offset:', bin(byte_offset)[2:])
    return tag, index, byte_offset
