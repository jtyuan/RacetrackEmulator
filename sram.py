__author__ = 'bilibili'

from l2cache import L2Cache


class SRAM:
    tags = []
    valid = []

    def __init__(self, line_num):
        self.tags = line_num * [None]
        self.valid = line_num * [False]
        self.line_num = line_num

    def compare_tag(self, tag, index):
        """
        compare_tag(tag, index) - compare tag in the set given by index
        :param tag: the tag to compare
        :param index: set index
        :return line_number: return -1 if no valid & matched line
        """
        for i in L2Cache.set_line_numbers(index):
            if self.valid[i] is True and tag == self.tags[i]:
                return i
        return -1

    def update(self, tag, line):
        """
        update(tag, line_num) - update SRAM
        :param tag: new tag
        :param line: update line# in SRAM
        :return: True if success
        """
        if line < 0 or line >= self.line_num:
            return False
        self.tags[line] = tag
        self.valid[line] = True
        return True