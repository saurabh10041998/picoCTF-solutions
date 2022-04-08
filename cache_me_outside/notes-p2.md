# Heap exploitation notes part 2

## Tutorial link
```
https://azeria-labs.com/heap-exploitation-part-2-glibc-heap-free-bins/
```

## How does the free work ??
- Programmer releases memory by call to `free`. When call to free made, job of heap manager to resolve the pointer back to it's corresponding chunk.
- This is done by subtracting size of chunk metadata from the pointer passed to free.
- `free` first does a couple of basic checks to see if freed pointer is not invalid. If all these checks fail, it leads to program aborts.
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
- free bins operate like linked list. This require chunk to store pointer to other chunks.
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
- Automatically ordered and hence insertion and removal of the entries is incredibly fast.

## Large bins
- For chunk over 512/1024 bytes, the heap manager uses large bins
- 63 large bins, operates the same as the small bins but instead of storing the fixed size,  **they instead store chunks within size range**.
- Each large bin's range is designed not to overlap with either the chunks sizes of small bins or the ranges of the other bins. **In other words, given the chunk size, there is exactly one small bin or large bin that this size corresponds to**.
- Insertion has to be mannually sorted and allocation from this list requires list traversal. Thus these are inherently slower than the small bins. However
large bins are used less frequently in the program.
- **Hypothesis** :- *programs tend to allocate(and thus release) small allocations at a far higher rate than large allocations on an average*
- Henc large bin ranges are clustered towards smaller chunk sizes
```
Smallest large bins -> 64 bytes(512 byte to 576 bytes).
Second largest -> 256Kb
largest of large bin(1) -> freed chunks over  1Mb.
``` 
