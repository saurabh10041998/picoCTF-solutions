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

### Allocating from the free'd chunks
- Heap manage keeps track of such freed chuncks in series of different link list called as `bins`
- Allocation request --> search for bins for a chunk big enough to serve request
- If found,remove the chunk from bin and mark it allocated
- For performance reason, there are several types of bins
```
    1. fast bins
    2. the unsorted bins
    3. small bins
    4. large bins
    5. per thread t-cache
```
### Allocation from the top of heap
- If no chunk found to serve the request, the heap manager must constructor from the scratch
- first lookup at end of the heap (sometimes called as "top chunk" or "remainder chunk") to see enough space is there
- If there is, manufacture the chunk and allocate to process.


### Asking the kernel for more memory at the top of the heap
- Once free space from the top is used up, heap manager will have to ask kernel to add more memory at end of the heap
- On initial heap, heap manager calls `sbrk` to allocate more memory
- Internally uses `brk` system call. Quite confusing name. Original meaning `change the program break location`
- syscall will allocate more memory at the end of the initial heap created by process

- sbrk will fail when heap will eventually grow so large that expanding it further would collide with the other things in the process' address space.
- Process address space include
```
    1. Memory mappings
    2. shared library
    3. thread's stack region
```
- At this point, heap manager will resort to attaching **non-contigious memory** to the initial program using calls to `mmap`
- if mmap fails, then malloc will return NULL

### Off-heap allocations via mmap
- Very large allocations requests gets special treatment from heap manager.
- Large chunks allocated off heap using direct call to `mmap`. This fact is marked using flag in chunk metadata.
- free(large allocations) --> heap manager releases entire mmaped region back to system via `munmap`.

