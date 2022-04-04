## Heap Based exploitation

### heap basics

1. google chrome --> PartionAlloc  heap allocatior
2. freeBSD --> jemalloc heap allocatior
3. glibc --> ptmalloc --> dlmalloc

## Tutorial link:
```
https://azeria-labs.com/heap-exploitation-part-1-understanding-the-glibc-heap-implementation/
```

### Why do people use heap ??
- Mannually allocate the new region during program execution. This is done via `malloc`.
- Then programmer can then interact with "allocations".
- After use it done, programmer can return the allocation back to heap manager using `free`. 


### Memory chunks and chunk allocation strategies

```
 Whatever amount request by programmer to heap manager, 
 1. Find the requested amount on heap
 2. store its metadata
 3. Ensure allocation is 8 byte aligned on 32 bit system, 16 byte aligned on 64 bit system

```

Request x byte --> metadata + x bytes + alignment byte 

return value from malloc = start address of x byte

### Chunk allocation : basic strategy.

**For smaller chunks**
- If there is previously freed chunk of memory, and that chunk is big enough to service the request, the heap manager will use that freed chunk for the new allocation..
- Otherwise, if there is available space at top of the heap, the heap manager will allocate a new chunk out of that available space and use that.
- Otherwise, the heap manager will ask the kernel to add new memory to the end of the heap, and then allocates a new chunk from the newly allocated space.
- Otherwise, allocation can't be serviced ,return NULL


