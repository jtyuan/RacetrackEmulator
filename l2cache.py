__author__ = 'bilibili'

import configs


def set_line_numbers(index):
    """set_lines(index) - get line numbers of one set, given set index"""
    for i in range(configs.L2_ASSOC):
        yield index + i