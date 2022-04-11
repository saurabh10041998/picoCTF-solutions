# Heap exploitation notes part 2

## Tutorial link
```
https://azeria-labs.com/heap-exploitation-part-2-glibc-heap-free-bins/
```

## How does the free work ??
- Programmer releases memory by call to `free`. When call to free made, job of heap manager is to resolve the pointer back to it's corresponding chunk.
- This is done by subtracting size of chunk metadata from the pointer passed to free.
- `free` first does a couple of basic checks to see if freed pointer is not invalid. If any of these checks fail, it leads to program aborts.
```
1. Allocation is aligned 8/16 bytes boundary. Since malloc ensures the same.
2. chunk's size isn't impossible - too small, too large, overlap the end of process' address space.
3. chunk lies within the boundaries of arena.
4. Chunk is not marked as free(checking the "P" bit from  metadata of next chunk).
```
Even with these checks, attackers can still exploit heap.

## Free chunk metadata

- We know about metadata(chunk size, "A" bit, "M" bit, "P" bit).
- Free chunks stores above info too. (Except "M" bit beacause of nature of `munmap`)
- Free chunks also store information after user data region using a technique called as **boundary tags**. 
- Boundary tags carry size information  before and after the chunk. This allows bidirectional traversing.
- Free bins operate like linked list. This require chunk to store pointer to other chunks.
- Since there is no "user data" in user region, heap manager repurposes this "user data" region in freed chunks as the place where this additional metadata lives.

## Recycling memory with bins
- Heap manager needs to keep track of freed chunks so that malloc can reuse them during allocation request.
- *Naive implmentation* : Using linked list for this. This will work but will make malloc slow.
- Since malloc is **high utilization** component of most program, This would have a hugh impact on overall system performance.
- For performance improvement, heap manager maintains a series of list called "bins".
- 5 type of bins : **62 small bins, 63 large bins, 1 unsorted bin, 10 fast bin and 64 tcache bins per thread**.
- Large, small and unsorted bins --> basic recycling strategy of heap.
- Fast bins and  tcache bin are optimization that layer on top of these.

```
    bin[0] = N/A
    bin[1] = unsorted bin
    bin[2] - bin[63] = small bin
    bin[64] - bin[126] = large bin
```
## Chunk recycling : the basic strategy
- Basic algorithm for free as follows
```
1. If M = 1, allocation -> off heap and should be munmaped.
2. Chunk before this one is free, then chunk is merged backwards to create a bigger free chunk.
3. Chunk after this one is free, then chunk is merged forwards to create a bigger free chunk.
4. If this potentially larger chunk borders the "top" of the heap, the whole chunk is absorbed into the end of the heap, rather than stored in a "bin".
5. Otherwise, chunk is marked as free and placed in an appropriate bin.
```

## Small bins
- Small bins are easier to understand. Total - 62.
- **Each of them stores the chunks that are all same fixed size.**
- Every chunk < 512 bytes(32 bit system) and < 1024 bytes on 64 bit system has corresponding small bins.
- Automatically ordered and hence insertion and removal of the entries are incredibly fast.

## Large bins
- For chunk over 512/1024 bytes, the heap manager uses large bins
- 63 large bins, operates the same as the small bins but instead of storing the fixed size,  **they instead store chunks within size range**.
- Each large bin's range is designed not to overlap with either the chunks sizes of small bins or the ranges of the other large bins. **In other words, given the chunk size, there is exactly one small bin or large bin that this size corresponds to**.
- Insertion has to be mannually sorted and allocation from this list requires list traversal. Thus these are inherently slower than the small bins. However
large bins are used less frequently in the program.
- **Hypothesis** :- *programs tend to allocate(and thus release) small allocations at a far higher rate than large allocations on an average*
- Hence large bin ranges are clustered towards smaller chunk sizes
```
Smallest large bins -> 64 bytes(512 byte to 576 bytes).
Second largest -> 256Kb
largest of large bin(1) -> freed chunks over  1Mb.
``` 

## Unsorted bins
- Layer of optimization added by the heap manager.
- Optimization is based on following hypothesis
```
1. Often frees are clustered together.
2. free is immediatetly followed by reallocation of similar size of chunk.
```
- For example, program releasing the linked list or tree will release all the allocations for every entry at once..and In linked list, if list wants update entry, it will release the memory of old entry before allocating it for its replacement.
- Being able to fastly re-return recently freed location, will certainly improve the performance.
- So based on above observations, heap manaer uses "unsorted bin". 
- Instead of putting recently freed chunk in correct bins, heap manager coalesces it with neighbors and dumps it general unsorted link list.
- During malloc, each item in unsorted bins is checked if it "fits" the request. If it does malloc can use it immediately. If it does not then malloc puts it in corresponding small or large bins.

## Fast bins
- Further optimization layer on top these.
- Store recently freed small chunks in "fast turnaround queue"
- This will
```
  1. intentionally keep chunk live and unmerged with it's neighbours
  2. Hence it can be repurposed if malloc request of same chunk size come very soon after chunk is 
  freed
```
- Fixed chunk size bins ( same as small bins ) and 10 fast bins { 16, 24, 32, 40, 48, 56, 64, 72, 80 and 88 bytes+ }
- Remain **unmerged**. In practice, the way this works is the heap manager does not set P bit at start of next chunk metadata. It's like not "completely" freeing the chunks in fast  bins.
- Same as small bins, automatically ordered --> insertion and removal of chunks is incredibly fast. Moreover no merging, hence theycan be stored as **singly linked list** instead of doubly linked list and can be removed from the list when chunks are merged.
- Downside of fast bins, this lead to fragment and balloon over memory. To avoid this, heap manager periodically **consolidates** the heap.
- This flushes "every" entry in the fast bins. Merges the chunk neighbors and put resultant chunk in unsorted bins for malloc to use.
- "Consolidation" phase occurs when malloc request is made which is greater than what fastbins can service or `malloc_trim` or `mallocopt` is called.

## tcache ( per thread cache ) bins
- Also called as "tcache" allocator
### Problem analysis
Each running process in the computer system has one or more threads running. Multiple running threads allow process to execute multiple concurrent opertions. Great example would be web server handling large number of web requests. 
  Each thread in given process shares the same address space, which is to say, each thread can see the same code and data memory.
Each thread gets its own registers and stack to store the temporary variable but resources like global variables and heap are 
shared between all threads.Coordinating access to shared resources can be very difficult, and getting it wrong can lead to 
problems like "race conditions" which is kind of hard-debug problem also these faults can be exploitable by hackers.
```
For example, we maintain the database operation atomic during parallel web request thread access. 
```
Very Common way to solve these race conditions is to force simultaneous requests accessing the global resource into sequential queue using mechanism called as "lock".
Locks work by marking the one thread that it has "ownership" over global resources then doing the operation on that resources and then marking that resource is no longer  is use. If another thread comes along and wants to use the resource and some other thread is using it, the thread waits until other thread is done. This ensures thatthe global resource is used by one thread at a time. But it comes with cost: *The thread that is waiting on the resources is stalling and wasting time. This is called as "lock contention"*

For heap this cost is unacceptible as it will leads to program slowness
- This problem is solved by using per-thread arenas. + Additionally it maintains per thread t-cache. 
