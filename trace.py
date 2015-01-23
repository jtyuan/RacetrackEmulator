__author__ = 'bilibili'


class Trace:
    """
    Trace
    states:
        waiting
        ready
        (when hit:)
        accessing
        shifting
        reading/writing
        finished
    """
    def __init__(self, instr='u', parsed_addr=(-1, -1, -1), tick=0):
        self.instr = instr
        self.tag = parsed_addr[0]
        self.index = parsed_addr[1]
        self.offset = parsed_addr[2]
        self.tick = tick
        self.state = 'waiting'