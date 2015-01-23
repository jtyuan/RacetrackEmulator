__author__ = 'bilibili'

import configs
import l2cache


class SRAM:
    tags = []
    valid = []

    def __init__(self):
        self.tags = configs.LINE_NUM * [None]
        self.valid = configs.LINE_NUM * [False]

    def compare_tag(self, tag, index):
        """
        compare_tag(tag, index) - compare tag in the set given by index
        :param tag: the tag to compare
        :param index: set index
        :return line_number: return -1 if no valid & matched line
        """
        for i in l2cache.set_line_numbers(index):
            if self.valid[i] is True and tag == self.tags[i]:
                return i
        return -1

    def update(self, tag, line_num):
        """
        update(tag, line_num) - update SRAM
        :param tag: new tag
        :param line_num: update line# in SRAM
        :return: True if success
        """
        if line_num < 0 or line_num >= configs.LINE_NUM:
            return False
        self.tags[line_num] = tag
        self.valid[line_num] = True
        return True