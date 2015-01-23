__author__ = 'bilibili'

from configs import OFFSET_BITS, SET_BITS
from trace import Trace


def parse(trace):
    args = trace.split()
    if args[0] == 'u':
        args[0] = 'w'
    return Trace(args[0], __addr_parse(args[1]), args[4])


def __addr_parse(addr):
    trace_bits = bin(addr)
    byte_offset = int(trace_bits[-OFFSET_BITS:], 2)
    index = int(trace_bits[-(OFFSET_BITS + SET_BITS):OFFSET_BITS], 2)
    tag = int(trace_bits[2:-(OFFSET_BITS + SET_BITS)], 2)
    return tag, index, byte_offset
