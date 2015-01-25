__author__ = 'bilibili'


class Trace:
    """
    Trace
    states:
        waiting
        ready
        accessing - 6 cycles
        (when hit:)
        shifting  - 1 cycle per domain
        reading/writing - 1 cycle
        finished
        (when miss:)
        memory    - 100 cycles
        finished
    """
    def __init__(self, instr='u', parsed_addr=(-1, -1, -1), tick=0):
        self.instr = instr
        self.tag = parsed_addr[0]
        self.index = parsed_addr[1]
        self.offset = parsed_addr[2]
        self.start_tick = tick

        self.state = 'waiting'
        self.hit = False
        self.target_line_num = -1
        self.target_group = 0
        self.preshift_state = 'idle'
        self.access_count_down = 0  # for preshift
        self.shift_count_down = 0   # for preshift
        self.memory_count_down = 0  # for preshift