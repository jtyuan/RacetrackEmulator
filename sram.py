__author__ = 'bilibili'

from configs import *


class SRAM:
    tags = []
    valid = []
    dirty = []
    stamp = []

    def __init__(self, line_num):
        """
        __init__(line_num) - constructor
        :param line_num: the line # in L2 cache, each line has 64 blocks (512 bits)
        """
        self.tags = line_num * [None]
        self.valid = line_num * [False]
        self.dirty = line_num * [False]
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
        if Configs.VERBOSE:
            print('SRAM updating with tag:{0} on line {1}'.format(tag, line))
        if line < 0 or line >= self.line_num:
            return False
        self.tags[line] = tag
        self.valid[line] = True
        self.stamp[line] = tick
        self.dirty[line] = False
        if Configs.VERBOSE:
            print('SRAM tag array updated')
        return True

    def update_line_number(self, index):
        """
        update_line_number(index) - decide which line to replace/take
        :param index:
        :return: the best line# to take/replace
        """
        min_stamp = -1
        best = index * Configs.L2_ASSOC
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

        if self.valid[best] is True:
            # a replacement occurred
            if Configs.VERBOSE:
                print('Line {0} in L2 Cache is replaced'.format(best))
                if self.dirty[best] is True:
                    print('This block is dirty, write back to next memory level')

        return best

    def write(self, target_line_num, tick):
        """
        write(target_line_number, tick) - write on the l2 cache, set dirty bit
        :param target_line_num: the line number in the l2 cache to write
        :param tick: the time when write happens
        """
        if Configs.VERBOSE:
            print('Write on line {0} in L2 Cache, marked as dirty'.format(target_line_num))
        self.dirty[target_line_num] = True
        self.stamp[target_line_num] = tick

    def read(self, target_line_num, tick):
        """
        read(tick) - write on the l2 cache, set dirty bit
        :param target_line_num: the line number in the l2 cache to read
        :param tick: the time when read happens
        """
        self.stamp[target_line_num] = tick

    @staticmethod
    def set_line_numbers(index):
        """
        set_lines(index) - get line numbers of one set, given set index
        :param index: set index
        :return: line numbers belong to this set
        """
        if Configs.SET_PARTITION == 'con':
            for i in range(Configs.L2_ASSOC):
                yield index * Configs.L2_ASSOC + i
        elif Configs.SET_PARTITION == 'way':
            for i in range(Configs.L2_ASSOC):
                yield Configs.SET_NUM * i + index
        else:
            print('error: undefined set partitioning policy')
            exit()