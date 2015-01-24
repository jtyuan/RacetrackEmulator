__author__ = 'bilibili'

from configs import *


class SRAM:
    tags = []
    valid = []
    stamp = []

    def __init__(self, line_num):
        self.tags = line_num * [None]
        self.valid = line_num * [False]
        self.stamp = line_num * [0]
        self.line_num = line_num

    def compare_tag(self, tag, index, tick):
        """
        compare_tag(tag, index) - compare tag in the set given by index
        :param tag: the tag to compare
        :param index: set index
        :return line_number: return -1 if no valid & matched line
        """
        for i in SRAM.set_line_numbers(index):
            if self.valid[i] is True and tag == self.tags[i]:
                self.stamp[i] = tick
                return i
        return -1

    def update(self, tag, index, tick):
        """
        update(tag, index) - update SRAM
        :param tag: new tag
        :param index: index of update target
        :param tick: the time when this data is updated
        :return: True if success
        """
        line = self.update_line_number(index)
        print('SRAM updating with tag:{0} on line {1}'.format(tag, line))
        if line < 0 or line >= self.line_num:
            return False
        self.tags[line] = tag
        self.valid[line] = True
        self.stamp[line] = tick
        print('SRAM tag array updated')
        return True

    def update_line_number(self, index):
        """
        update_line_number(index) - decide which line to replace/take
        :param index:
        :return:
        """
        min_stamp = -1
        best = index * L2_ASSOC
        for l in SRAM.set_line_numbers(index):
            if self.valid[l] is False:
                # if there is an empty line
                best = l
                break

            # LRU
            if min_stamp == -1:
                min_stamp = self.stamp[l]
                best = l
            elif min_stamp > self.stamp[l]:
                min_stamp = self.stamp[l]
                best = l

        return best

    @staticmethod
    def set_line_numbers(index):
        """
        set_lines(index) - get line numbers of one set, given set index
        :param index: set index
        :return: line numbers belong to this set
        """
        for i in range(L2_ASSOC):
            yield index * L2_ASSOC + i