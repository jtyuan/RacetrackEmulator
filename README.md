# RacetrackEmulator
```
usage: python3 racetrack.zip [-h] [-t TRACEFILE] [-d dir] [-o outfile]
                 			       [--cpu-clock CPU_CLOCK] [--clock-cycle CLOCK_CYCLE]
                   			     [--tape-domain TAPE_DOMAIN] [--tape-length TAPE_LENGTH]
                 			       [--group-tape GROUP_TAPE] [--l2-size L2_SIZE]
                 			       [--l2-assoc L2_ASSOC] [--l2-r-latency L2_R_LATENCY]
                 			       [--l2-w-latency L2_W_LATENCY]
                 			       [--l2-access-latency L2_ACCESS_LATENCY]
                 			       [--l2-shift-latency L2_SHIFT_LATENCY]
                 			       [--l2-miss-penalty L2_MISS_PENALTY]
                 			       [-pm {baseline,rw,w+r,rw+r,rw+w+r,w+r+r}]
                 			       [-ps {dynamic,static}] [-pp {lazy,eager}] [-sp {con,way}]
                 			       [-pre] [-I MAXINSTS] [-V]

optional arguments:
  -h, --help            show help message and exit
  -t TRACEFILE, --tracefile TRACEFILE
                        The trace file to emulate with, this argument will be
                        ignored is --directory is added
  -d dir, --directory dir
                        Emulate all trace files in the given directory, enable
                        this will ignore trace-file argument
  -o outfile, --output outfile
                        The file path to write emulation information to. Add
                        -v to save the whole emulation detail.
  --cpu-clock CPU_CLOCK
                        Clock for blocks running at CPU speed(default="2GHz")
  --clock-cycle CLOCK_CYCLE
                        Ticks to run in one cycle(default=1000)
  --tape-domain TAPE_DOMAIN
                        The domain# in one tape(default=64)
  --tape-length TAPE_LENGTH
                        The spacial length of each tape(default=80)
  --group-tape GROUP_TAPE
                        The tape# in one group(default=512)
  --l2-size L2_SIZE     The size of L2 Cache(default=4MB)
  --l2-assoc L2_ASSOC   The associativity of L2 Cache(default=8)
  --l2-r-latency L2_R_LATENCY
                        The read latency (cycle) of L2 Cache(default=1)
  --l2-w-latency L2_W_LATENCY
                        The write latency (cycle) of L2 Cache(default=1)
  --l2-access-latency L2_ACCESS_LATENCY
                        The assess latency (cycle) of L2 Cache(default=6)
  --l2-shift-latency L2_SHIFT_LATENCY
                        The shift latency (cycle) of L2 Cache
                        RacetrackMemory(default=1)
  --l2-miss-penalty L2_MISS_PENALTY
                        The penalty (cycle) when a L2 Cache miss
                        occurs(default=100)
  -pm {baseline,rw,w+r,rw+r,rw+w+r,w+r+r}, --port-mode {baseline,rw,w+r,rw+r,rw+w+r,w+r+r}
                        Determine how the r/w ports are placed on a tape
  -ps {dynamic,static}, --port-selection {dynamic,static}
                        Port selection policy for every r/w instr
  -pp {lazy,eager}, --port-update-policy {lazy,eager}
                        The tape will remain where it is or move to default
                        place after r/w operation
  -sp {con,way}, --set_partition {con,way}
                        Set partitioning policy, "con" for continuous, use
                        "way" to divide sets into different ways
  -pre, --preshift      Enable preshift for next i/o instr
  -I MAXINSTS, --maxinsts MAXINSTS
                        Total number of traces to emulate (default: run
                        forever)
  -V, --verbose         Verbose mode, show debug info

其中与报告中的几种策略相关的有

  -pm {baseline,rw,w+r,rw+r,rw+w+r,w+r+r}, --port-mode {baseline,rw,w+r,rw+r,rw+w+r,w+r+r}
                        对应报告中的端口摆放策略，rw对应5RW, w+r对应2W+12R, rw+r对应2RW+10R,
                        rw+w+r对应2RW+2W+6R, w+r+r对应4W+8R
  -ps {dynamic,static}, --port-selection {dynamic,static}
                        对应报告中的端口选择策略
  -pp {lazy,eager}, --port-update-policy {lazy,eager}
                        对应报告中的端口移动策略
  -sp {con,way}, --set_partition {con,way}
                        对应报告中的Set划分策略, "con"代表continuous,
                        "way"代表corss-way
  -pre, --preshift      对应报告中的Preshift策略

使用例子：
  python3 ./racetrack.zip -pm 'w+r+r' -ps 'dynamic' -pp 'lazy' -sp 'way' -pre -t trace/462.libquantum.trace
  
  或者解压出来之后，
  ./__main__.py -pm 'w+r+r' -ps 'dynamic' -pp 'lazy' -sp 'way' -pre -t trace/462.libquantum.trace
```