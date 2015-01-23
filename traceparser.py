__author__ = 'bilibili'

import configs


def parse(trace):
    trace_bits = bin(trace)
    byte_offset = int(trace_bits[-configs.OFFSET_BITS:], 2)
    index = int(trace_bits[-(configs.OFFSET_BITS + configs.SET_BITS):configs.OFFSET_BITS], 2)
    tag = int(trace_bits[2:-(configs.OFFSET_BITS + configs.SET_BITS)], 2)
    return tag, index, byte_offset
