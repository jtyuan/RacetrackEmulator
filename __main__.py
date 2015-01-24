__author__ = 'bilibili'

from l2cache import L2Cache

if __name__ == "__main__":
    l2cache = L2Cache('trace/test.trace')
    while True:
        if not l2cache.next_cycle():
            break