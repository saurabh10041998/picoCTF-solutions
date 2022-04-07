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


