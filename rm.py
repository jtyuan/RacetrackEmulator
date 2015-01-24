__author__ = 'bilibili'

from trace import Trace
from configs import *

'''
Some thoughts:
    when SRAM miss, the latency is SRAM accessing time
    when SRAM hits, the latency would only be DWM accessing time, SRAM is not in the critical path
'''


class RM:
    current_trace = Trace()
    waiting_trace = Trace()

    count_down = 0

    r_port = []
    w_port = []
    rw_port = [0, 16, 32, 48]

    offset = GROUP_NUM * [0]

    miss_count = 0
    access_count = 0
    total_cycles = 0
    total_shifts = 0
    total_shift_dis = 0

    def __init__(self, sram):
        self.sram = sram

    def next_trace(self, current_trace, waiting_trace):
        self.current_trace = current_trace
        self.waiting_trace = waiting_trace

        self.current_trace.state = 'accessing'
        self.count_down = CLOCK_CYCLE * L2_ACCESS_LATENCY

        print('Start accessing L2 Cache for the next {0} ticks'.format(self.count_down))

        self.waiting_trace.state = 'waiting'

        self.access_count += 1

    def shift(self, port_type, target_port, target_group, target_group_line, dis):
        g = target_group
        p = target_port

        shift_dis = dis

        if shift_dis == 0:
            print('No need to shift')
            return 0

        if port_type == 'r':
            self.offset[g] = target_group_line - self.r_port[p]
        elif port_type == 'w':
            self.offset[g] = target_group_line - self.w_port[p]
        elif port_type == 'rw':
            self.offset[g] = target_group_line - self.rw_port[p]
        else:
            print('Error: Unknown Port Type:', port_type)

        self.total_shifts += 1
        self.total_shift_dis += shift_dis

        self.current_trace.state = 'shifting'
        self.count_down = shift_dis * L2_SHIFT_LATENCY * CLOCK_CYCLE

        print('Start shifting on Group{0} for the next {1} ticks'.format(g, self.count_down))

        return shift_dis

    def next_cycle(self, tick):
        self.total_cycles += 1
        self.count_down -= CLOCK_CYCLE

        print('Trace state: current({0}) next({1})'.format(self.current_trace.state, self.waiting_trace.state))

        if self.count_down >= 0:
            print('Count down:', self.count_down)
        else:
            print('Waiting for next instr')

        if self.waiting_trace.instr != 'EOF' and tick > self.waiting_trace.start_tick:
            self.waiting_trace.state = 'ready'

        if self.count_down == 0:
            if self.current_trace.state == 'accessing':
                print('L2 Cache accessed')

                self.current_trace.target_line_num = self.sram.compare_tag(self.current_trace.tag,
                                                                           self.current_trace.index, tick)
                target_line_num = self.current_trace.target_line_num
                target_group_line = target_line_num % TAPE_DOMAIN  # target line # in a group
                target_group = target_line_num // TAPE_DOMAIN  # the group target is in

                if target_line_num >= 0:  # hit
                    print('L2 Cache Hit')
                    self.current_trace.hit = True
                    target_port = -1
                    port_type = 'undefined'
                    d = TAPE_LENGTH
                    if self.current_trace.instr == 'r':
                        # if current instr is read, to find closest read port or rw port
                        if R_PORT_NUM > 0:
                            for pos_k, k in zip(self.r_port, range(R_PORT_NUM)):
                                # looking for the closest read port
                                d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                if d_k < d:
                                    d = d_k
                                    target_port = k
                                    port_type = 'r'
                                k += 1
                        if RW_PORT_NUM > 0:  # if there is rw port
                            for pos_k, k in zip(self.rw_port, range(RW_PORT_NUM)):
                                # looking for the closest rw port
                                d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                print(pos_k, k, self.offset[target_group], target_group_line)
                                if d_k < d:
                                    d = d_k
                                    target_port = k
                                    port_type = 'rw'
                                k += 1
                        self.shift(port_type, target_port, target_group, target_group_line, d)
                    elif self.current_trace.instr == 'w':
                        # if current instr is write, to find closest write port or rw port
                        if W_PORT_NUM > 0:
                            for pos_k, k in zip(self.w_port, range(W_PORT_NUM)):
                                # looking for the closest write port
                                d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                if d_k < d:
                                    d = d_k
                                    target_port = k
                                    port_type = 'w'
                                k += 1
                        if RW_PORT_NUM > 0:  # if there is rw port
                            for pos_k, k in zip(self.rw_port, range(RW_PORT_NUM)):
                                # looking for the closest rw port
                                d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                if d_k < d:
                                    d = d_k
                                    target_port = k
                                    port_type = 'rw'
                                k += 1
                        self.shift(port_type, target_port, target_group, target_group_line, d)
                    else:
                        print('Error: Unknown Instruction type:', self.current_trace.instr)
                    if d == 0:  # don't need shift
                        if self.current_trace.instr == 'r':
                            self.current_trace.state = 'reading'
                            self.count_down = CLOCK_CYCLE * L2_R_LATENCY
                            print(
                                'Current trace start reading from L2, it would take {0} ticks'.format(self.count_down))
                        elif self.current_trace.instr == 'w':
                            self.current_trace.state = 'writing'
                            self.count_down = CLOCK_CYCLE * L2_W_LATENCY
                            print('Current trace start writing in L2, it would take {0} ticks'.format(self.count_down))
                        else:
                            print('Error: Unknown Instruction type:', self.current_trace.instr)
                # end of if target_line_num >= 0
                else:  # failed to find a matched tag in SRAM, miss
                    self.current_trace.hit = False
                    self.current_trace.state = 'memory'
                    self.count_down = CLOCK_CYCLE * L2_MISS_PENALTY
                    self.miss_count += 1
                    print('L2 Cache Miss, this would take {0} ticks'.format(self.count_down))
            # end of if state == 'accessing'
            elif self.current_trace.state == 'shifting':
                # after shifting, start reading/writing
                print('Shift complete')
                if self.current_trace.instr == 'r':
                    self.current_trace.state = 'reading'
                    self.count_down = CLOCK_CYCLE * L2_R_LATENCY
                    print('Current trace start reading from L2, it would take {0} ticks'.format(self.count_down))
                elif self.current_trace.instr == 'w':
                    self.current_trace.state = 'writing'
                    self.count_down = CLOCK_CYCLE * L2_W_LATENCY
                    print('Current trace start writing in L2, it would take {0} ticks'.format(self.count_down))
                else:
                    print('Error: Unknown Instruction type:', self.current_trace.instr)
            elif self.current_trace.state == 'reading':
                print('L2 reading complete')
                self.current_trace.state = 'finished'
                print('Current trace finished\n')
            elif self.current_trace.state == 'writing':
                print('L2 writing complete')
                self.current_trace.state = 'finished'
                print('Current trace finished\n')
            elif self.current_trace.state == 'memory':
                print('Main memory access complete')
                self.sram.update(self.current_trace.tag, self.current_trace.index, tick)
                # for t, k in zip(self.sram.tags, range(len(self.sram.tags))):
                # if t is not None:
                #         print(t, k)
                self.current_trace.state = 'finished'
                print('Current trace finished\n')
                # end of if count_down == 0
