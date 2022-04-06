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

## Arenas (I found this imp hence large..)
- On multithreaded environment, heap manager have to defend its internal heap DS from race conditions.
- Prior to ptmalloc2, this is accomplished using a global mutex before heap operation.
- ptmalloc2 introduce concept of `arenas`.
- **Arenas** --> an entirely different heap that manages its own chunk allocation and free bins completely seperately.
- Each arenas still serializes access to its own internal data structure with a mutex, but threads can safely perform heap operations without stalling each other so long as they are interacting with different arenas.
- "Initial" Arena is the only main heap that we have seen. This is primary arena for single threaded application.
- As new threads join process, the heap manager allocates and attaches **secondary arena** to each new thread.
- With each new thread joins the process, the heap manager tries to find the arena that no other thread is using and attaches the arenas to it.
- Maximum number of arena creation = 2 * cpu core 32 bit processor / 8 * cpu core 64 bit processor.
- Secondary arena do not work same as primary arena(i.e allocted when process is loaded into memory and expanded using brk syscall)
- *Secondary arena emulate the behaviour of the main heap using one or more "subheaps" created using* `mmap` and `mprotect`

## Subheaps
- Sub heaps same working as main heaps but only difference is they are positioned into memory using `mmap` , and the heap manager emulates growing the subheap using mprotect
- When heap manager wants to create subheap
```
1. Asks kernel to reserve a region of memory that subheap can grow into by calling mmap.
2. Reserving region does not allocate memory directly into the subheap.
3. It asks the kernel to refrain from allocating things like thread stacks, mmap* regions and other allocations inside this region.
4. mmap asks for pages that are marked PROT_NONE, which acts as hint to the kernel that it only needs to reserve the address range for the region; it doesn't yet need the kernel attach memory to it.
```
*By Default, the maximum size of a subheap -and therefore the region of memory reserved for the subheap to grow into is 1MB on 3 bit processes and 64MB on 64 bit processes*

- Intial heap grow using sbrk --> the heap manager emulates growing of subheap into reseved address range by mannually calling `mprotect` to change pages in the region from **PROT_NONE** to **PROT_READ | PROT_WRITE** 
- This causes kernel to to **attach** memory to address space --> subheap growing. The subheap grows until whole mmap region is full.
- When entire subheap is exhausted then arena allocates another subheap.
- This allows secondary arenas to grow indefinitely until process run out of memory.  
