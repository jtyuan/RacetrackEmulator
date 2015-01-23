# RacetrackEmulator

## Basic Design
1. functional module
1.1 trace parser
1.2 SRAM (Tag & valid)
1.2.1 Tag locator
1.2.2 Tag comparator 
1.3 Racetrack Memory (Data)
1.3.1 Datablock locator
1.3.2 Datablock getter
1.4 results analysis (Statistical)

2. architecture module
2.1 SRAM (store as an Array)
2.2 Racetrace Memory 

Procedure of emulator:
1. fetch instr (MemControl)
2. decode (TraceParser)
3. find corresponding tag&valid in SRAM
4. if no (matched tag & valid) **return** miss
5. else, find data in Racetrack Memory
6. calculate shift latency, and **return** hit, data & latency

## Class Design:

```
class Configs {
	l2_size
	l2_assoc
	l2_io_latency = 1
	l2_access_latency = 6
	cpu_clock = 2GHz
	clock_cycle = 1000tick(or 3000)
}
```

```
class MemControl {
Methods:
	MemControl(trace_path);

	trace fetchNext();
	TraceParser decode(trace);
	(hit_or_miss, target_line_num) checkInSRAM(tag, index);
	(data, shift_num) fetchFromRM(target_line_num);
	void resultProcess(hit_or_miss, data, shift_num);
}

```


```
class TraceParser {
Methods:
	TraceParser(trace);
	getTag();
	getIndex();
	getByteOffset();
Members:
	int64_t tag;
}
```

```
class SRAM {
Methods:
	SRAM(l2_size);

	(boolean, int64_t) compareTag(tag, index); // return the target_line_number which is valid and where tag is matched
Members:
	int64_t tags[line_num];
	boolean valid[line_num];
}
```

```
typedef Set int64_t[set_line_num][group_tape/64];
```
```c
class RacetrackMemory {
Methods:
	RacetrackMemory(l2_size, tape_domain, group_tape, pos[]...);
	Set getSet(index); // could be useful
	int64_t getData(index, target_line_number) ;
	// matched_pos is fetched from SRAM, 
	// returns boolean(hit/miss), int64_t(result data)
	
	int64_t shift(target_line_num); // return shift distance
Members:
	int16_t[group_num] offset; // offset for each group
	int64_t[line_num][group_tape/64] data;

Attributes:
	mem_size = l2_size;
	tape_domain = 64; // # of domains on a tape
	group_tape = 512; // # of tapes in a group
	group_num = mem_size / (group_tape * tape_domain);
	line_num = group_num * tape_domain;
	set_line_num = l2_assoc;
	wr_port_size = 12;
	w_port_size = 8;
	r_port_size = 4;

	int16_t port_pos[num_of_port];
}
```
> Written with [StackEdit](https://stackedit.io/).