__author__ = 'bilibili'

from trace import Trace
from configs import Configs

'''
Some thoughts:
    when SRAM miss, the latency is SRAM accessing time
    when SRAM hits, the latency would only be DWM accessing time, SRAM is not in the critical path

    when miss:
        update/replace
    when hit:
        read(update timestamp in SRAM)
        write(update timestamp in SRAM, set dirty bit) -- write back
'''

RW_PORT_SIZE = 12  # the size of a W/R port
W_PORT_SIZE = 8  # the size of a W port
R_PORT_SIZE = 4  # the size of a R port

RW_PORT_NUM = 4
R_PORT_NUM = 0
W_PORT_NUM = 0


class RM:
    def __init__(self, sram):
        """
        __init__(sram) - constructor
        :param sram: the SRAM that maintains tag array
        """

        # initialization
        self.offset = Configs.GROUP_NUM * [0]

        self.current_trace = Trace()
        self.waiting_trace = Trace()

        self.miss_count = 0
        self.access_count = 0
        self.total_cycles = 0
        self.total_shifts = 0
        self.total_shift_dis = 0
        self.count_down = 0

        self.sram = sram

        if Configs.PORT_MODE == 'rw':
            self.r_port = []
            self.w_port = []
            self.rw_port = [0, 13, 26, 39, 52]
        elif Configs.PORT_MODE == 'rw+r':
            self.rw_port = [0, 32]
            self.w_port = []
            self.r_port = [12, 16, 20, 24, 28, 44, 48, 52, 56, 60]
        elif Configs.PORT_MODE == 'w+r':
            self.rw_port = []
            self.w_port = [0, 32]
            self.r_port = [8, 12, 16, 20, 24, 28, 40, 44, 48, 52, 56, 60]
        elif Configs.PORT_MODE == 'rw+w+r':
            self.rw_port = [0, 32]
            self.w_port = [12, 44]
            self.r_port = [20, 24, 28, 52, 56, 60]
        elif Configs.PORT_MODE == 'w+r+r':
            self.rw_port = []
            self.w_port = [0, 16, 32, 48]
            self.r_port = [8, 12, 24, 28, 40, 44, 56, 60]
        else:  # baseline
            self.r_port = []
            self.w_port = []
            self.rw_port = [0, 16, 32, 48]

        global RW_PORT_NUM, R_PORT_NUM, W_PORT_NUM
        RW_PORT_NUM = len(self.rw_port)
        R_PORT_NUM = len(self.r_port)
        W_PORT_NUM = len(self.w_port)

    def next_trace(self, current_trace, waiting_trace):
        """
        next_trace(current_trace, waiting_trace) - setup for next trace
        :param current_trace: the trace to be processed immediately
        :param waiting_trace: the trace to be processed after current trace finishes
        """
        self.current_trace = current_trace
        self.waiting_trace = waiting_trace

        self.current_trace.state = 'accessing'
        self.count_down = Configs.CLOCK_CYCLE * Configs.L2_ACCESS_LATENCY

        if Configs.VERBOSE:
            print('Start accessing L2 Cache for the next {0} ticks'.format(self.count_down))

        self.waiting_trace.state = 'waiting'

        self.access_count += 1

    def shift(self, port_type, target_port, target_group, target_group_line, dis):
        """
        shift(port_type, target_port, target_group ,target_group_line, dis) - shift a group of tapes to target line
        :param port_type: the type of port to be used ('r', 'w', 'rw')
        :param target_port: the index for the target port
        :param target_group: the group that the target belongs to
        :param target_group_line: the line in the group in which the target is
        :param dis: the distance to shift
        :return: the distance to shift
        """
        g = target_group
        p = target_port

        shift_dis = dis

        if shift_dis == 0:
            if Configs.VERBOSE:
                print('No need to shift')
            return 0

        if Configs.PORT_UPDATE_POLICY == 'lazy':
            if port_type == 'r':
                self.offset[g] = target_group_line - self.r_port[p]
            elif port_type == 'w':
                self.offset[g] = target_group_line - self.w_port[p]
            elif port_type == 'rw':
                self.offset[g] = target_group_line - self.rw_port[p]
            else:
                print('error: unknown port type:', port_type)
                exit()
        elif Configs.PORT_UPDATE_POLICY == 'eager':
            if port_type == 'r':
                if Configs.VERBOSE:
                    print('Applying EAGER policy, the tape will move to default position after read complete')
            elif port_type == 'w':
                if Configs.VERBOSE:
                    print('Applying EAGER policy, the tape will move to default position after write complete')
                self.offset[g] = target_group_line - self.w_port[p]
            elif port_type == 'rw':
                if Configs.VERBOSE:
                    print('Applying EAGER policy, the tape will move to default position after read/write complete')
                self.offset[g] = target_group_line - self.rw_port[p]
            else:
                print('error: unknown port type:', port_type)
                exit()

        self.total_shifts += 1
        self.total_shift_dis += shift_dis

        self.current_trace.state = 'shifting'
        self.count_down = shift_dis * Configs.L2_SHIFT_LATENCY * Configs.CLOCK_CYCLE

        if Configs.VERBOSE:
            print('Start shifting on Group{0} for the next {1} ticks'.format(g, self.count_down))

        return shift_dis

    def next_cycle(self, tick):
        """
        next_cycle(tick) - move 1 cycle forward, do all the works that should be done in this cycle
        :param tick: current tick
        """
        self.total_cycles += 1
        self.count_down -= Configs.CLOCK_CYCLE

        if Configs.VERBOSE:
            print('Trace state: current({0}) next({1})'.format(self.current_trace.state, self.waiting_trace.state))
            if self.count_down >= 0:
                print('Count down:', self.count_down)
            else:
                print('Waiting for next instr')

        if self.waiting_trace.instr != 'EOF' and tick > self.waiting_trace.start_tick:
            self.waiting_trace.state = 'ready'

        if self.count_down == 0:
            if self.current_trace.state == 'accessing':
                if Configs.VERBOSE:
                    print('L2 Cache accessed')

                self.current_trace.target_line_num = self.sram.compare_tag(self.current_trace.tag,
                                                                           self.current_trace.index, tick)
                target_line_num = self.current_trace.target_line_num
                target_group_line = target_line_num % Configs.TAPE_DOMAIN  # target line # in a group
                target_group = target_line_num // Configs.TAPE_DOMAIN  # the group target is in

                if target_line_num >= 0:  # hit
                    if Configs.VERBOSE:
                        print('L2 Cache Hit')
                    self.current_trace.hit = True
                    target_port = -1
                    port_type = 'undefined'
                    d = Configs.TAPE_LENGTH
                    if self.current_trace.instr == 'r':
                        # if current instr is read, to find closest read port or rw port
                        if R_PORT_NUM > 0:
                            if Configs.PORT_SELECTION == 'dynamic':
                                for pos_k, k in zip(self.r_port, range(R_PORT_NUM)):
                                    # looking for the closest read port
                                    d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                    if d_k < d:
                                        d = d_k
                                        target_port = k
                                        port_type = 'r'
                            elif Configs.PORT_SELECTION == 'static':
                                for pos_k, k in zip(self.r_port, range(R_PORT_NUM)):
                                    if pos_k <= target_group_line <= R_PORT_SIZE + pos_k:
                                        d = abs(pos_k + self.offset[target_group] - target_group_line)
                                        target_port = k
                                        port_type = 'r'
                                        break
                            else:
                                print('error: undefined port selection policy')
                                exit()
                        if RW_PORT_NUM > 0:  # if there is rw port
                            if Configs.PORT_SELECTION == 'dynamic':
                                for pos_k, k in zip(self.rw_port, range(RW_PORT_NUM)):
                                    # looking for the closest rw port
                                    d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                    if d_k < d:
                                        d = d_k
                                        target_port = k
                                        port_type = 'rw'
                            elif Configs.PORT_SELECTION == 'static':
                                for pos_k, k in zip(self.rw_port, range(RW_PORT_NUM)):
                                    if pos_k <= target_group_line <= RW_PORT_SIZE + pos_k:
                                        d = abs(pos_k + self.offset[target_group] - target_group_line)
                                        target_port = k
                                        port_type = 'rw'
                                        break
                            else:
                                print('error: undefined port selection policy')
                                exit()
                        if Configs.PORT_MODE == 'w+r' and Configs.PORT_SELECTION == 'static' \
                                and port_type == 'undefined':
                            # haven't found a port in corresponding area
                            # only when use 'w+r' port mode can this situation occur
                            if target_line_num < Configs.TAPE_DOMAIN // 2 and R_PORT_NUM > 0:
                                # target is in the 1st half of the group
                                d = abs(self.r_port[0] + self.offset[target_group] - target_group_line)
                                target_port = 0
                                port_type = 'r'
                            else:
                                target_port = int((R_PORT_NUM + 0.5) // 2)
                                d = abs(self.r_port[target_port] + self.offset[target_group] - target_group_line)
                                port_type = 'r'
                        self.shift(port_type, target_port, target_group, target_group_line, d)
                    elif self.current_trace.instr == 'w':
                        # if current instr is write, to find closest write port or rw port
                        if W_PORT_NUM > 0:
                            if Configs.PORT_SELECTION == 'dynamic':
                                for pos_k, k in zip(self.w_port, range(W_PORT_NUM)):
                                    # looking for the closest write port
                                    d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                    if d_k < d:
                                        d = d_k
                                        target_port = k
                                        port_type = 'w'
                            elif Configs.PORT_SELECTION == 'static':
                                for pos_k, k in zip(self.w_port, range(W_PORT_NUM)):
                                    if pos_k <= target_group_line <= W_PORT_SIZE + pos_k:
                                        d = abs(pos_k + self.offset[target_group] - target_group_line)
                                        target_port = k
                                        port_type = 'w'
                                        break
                            else:
                                print('error: undefined port selection policy')
                                exit()
                        if RW_PORT_NUM > 0:  # if there is rw port
                            if Configs.PORT_SELECTION == 'dynamic':
                                for pos_k, k in zip(self.rw_port, range(RW_PORT_NUM)):
                                    # looking for the closest rw port
                                    d_k = abs(pos_k + self.offset[target_group] - target_group_line)
                                    if d_k < d:
                                        d = d_k
                                        target_port = k
                                        port_type = 'rw'
                            elif Configs.PORT_SELECTION == 'static':
                                for pos_k, k in zip(self.rw_port, range(RW_PORT_NUM)):
                                    if pos_k <= target_group_line <= RW_PORT_SIZE + pos_k:
                                        d = abs(pos_k + self.offset[target_group] - target_group_line)
                                        target_port = k
                                        port_type = 'rw'
                                        break
                            else:
                                print('error: undefined port selection policy')
                                exit()
                        if Configs.PORT_MODE != 'rw' and Configs.PORT_SELECTION == 'static' \
                                and port_type == 'undefined':
                            # haven't found a port in corresponding area
                            if W_PORT_NUM > 0:
                                if target_line_num < Configs.TAPE_DOMAIN // 2:
                                    # target is in the 1st half of the group
                                    d = abs(self.w_port[0] + self.offset[target_group] - target_group_line)
                                    target_port = 0
                                    port_type = 'w'
                                else:
                                    target_port = int((W_PORT_NUM + 0.5) // 2)
                                    d = abs(self.w_port[target_port] + self.offset[target_group] - target_group_line)
                                    port_type = 'w'
                            elif RW_PORT_NUM > 0:
                                if target_line_num < Configs.TAPE_DOMAIN // 2:
                                    # target is in the 1st half of the group
                                    d = abs(self.rw_port[0] + self.offset[target_group] - target_group_line)
                                    target_port = 0
                                    port_type = 'rw'
                                else:
                                    target_port = int((RW_PORT_NUM + 0.5) // 2)
                                    d = abs(self.rw_port[target_port] + self.offset[target_group] - target_group_line)
                                    port_type = 'rw'

                        self.shift(port_type, target_port, target_group, target_group_line, d)
                    else:
                        print('error: Unknown Instruction type:', self.current_trace.instr)
                        exit()
                    if d == 0:  # don't need shift
                        if self.current_trace.instr == 'r':
                            self.current_trace.state = 'reading'
                            self.count_down = Configs.CLOCK_CYCLE * Configs.L2_R_LATENCY
                            if Configs.VERBOSE:
                                print('Current trace start reading from L2, it would take {0} ticks'.format(
                                    self.count_down))
                        elif self.current_trace.instr == 'w':
                            self.current_trace.state = 'writing'
                            self.count_down = Configs.CLOCK_CYCLE * Configs.L2_W_LATENCY
                            if Configs.VERBOSE:
                                print('Current trace start writing in L2, it would take {0} ticks'.format(
                                    self.count_down))
                        else:
                            print('error: Unknown Instruction type:', self.current_trace.instr)
                            exit()
                # end of if target_line_num >= 0
                else:  # failed to find a matched tag in SRAM, miss
                    self.current_trace.hit = False
                    self.current_trace.state = 'memory'
                    self.count_down = Configs.CLOCK_CYCLE * Configs.L2_MISS_PENALTY
                    self.miss_count += 1
                    if Configs.VERBOSE:
                        print('L2 Cache Miss, this would take {0} ticks'.format(self.count_down))
            # end of if state == 'accessing'
            elif self.current_trace.state == 'shifting':
                # after shifting, start reading/writing
                if Configs.VERBOSE:
                    print('Shift complete')
                if self.current_trace.instr == 'r':
                    self.current_trace.state = 'reading'
                    self.count_down = Configs.CLOCK_CYCLE * Configs.L2_R_LATENCY
                    if Configs.VERBOSE:
                        print('Current trace start reading from L2, it would take {0} ticks'.format(self.count_down))
                elif self.current_trace.instr == 'w':
                    self.current_trace.state = 'writing'
                    self.count_down = Configs.CLOCK_CYCLE * Configs.L2_W_LATENCY
                    if Configs.VERBOSE:
                        print('Current trace start writing in L2, it would take {0} ticks'.format(self.count_down))
                else:
                    print('error: Unknown Instruction type:', self.current_trace.instr)
                    exit()
            elif self.current_trace.state == 'reading':
                if Configs.VERBOSE:
                    print('L2 reading complete')
                self.sram.read(self.current_trace.target_line_num, tick)
                self.current_trace.state = 'finished'
                if Configs.VERBOSE:
                    print('Current trace finished\n')
            elif self.current_trace.state == 'writing':
                if Configs.VERBOSE:
                    print('L2 writing complete')
                self.sram.write(self.current_trace.target_line_num, tick)
                self.current_trace.state = 'finished'
                if Configs.VERBOSE:
                    print('Current trace finished\n')
            elif self.current_trace.state == 'memory':
                if Configs.VERBOSE:
                    print('Main memory access complete')
                self.sram.update(self.current_trace.tag, self.current_trace.index, tick)
                # for t, k in zip(self.sram.tags, range(len(self.sram.tags))):
                # if t is not None:
                # print(t, k)
                self.current_trace.state = 'finished'
                if Configs.VERBOSE:
                    print('Current trace finished\n')
                    # end of if count_down == 0
