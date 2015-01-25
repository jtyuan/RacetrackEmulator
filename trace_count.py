import os

TRACE_DIR = '/Users/lx/Courses/Computer Architecture/RaceTrackEmulator/trace/'

for trace in os.listdir(TRACE_DIR):
    tracePath = os.path.join(TRACE_DIR, trace)
    u = r = t = 0
    for line in open(tracePath):
        if 'u' in line:
            u = u + 1
        if 'r' in line:
            r = r + 1
        t = t + 1
    print
    trace, '|', t, '|', round(float(r) / float(t) * 100, 2), '%|', round(float(u) / float(t) * 100, 2), '%'