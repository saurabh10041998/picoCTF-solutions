## Allocation algorithm
1. If the size corresponds with a tcache bin and tcache chunk available, return that immediately.
2. If the request is enormus allocate a chunk off-heap via mmap
3. Otherwise we obtain arena heap lock and then perform following strategies, in order:  
    **1. Try the fastbins/smallbin recycling strategy**
        - If a correspoding fast bin exists, find a chunk from there.(and also oppotunistically prefill the tcache with entries from fast bin).
        - Otherwise, if corresponding small bin exists, allocate from there(opportunistically prefilling the tcache as we can go).
    
    **2. Resolve all deferred frees**
        - Otherwise "truly free" the entries in the fast bins and move their consolidated chunks to unsorted bin.
        - Go through each entry in the unsorted bins, if it is suitable, stop. Otherwise, put the unsorted entry into its corresponding small/large bin as we go (possibly promoting small entries to tcache as we go).
    
    **3. Default back to basic recycling stratagy** 
        - If the chunks size corresponds with a large bin, search the corresponding large bin now.

    **4. Create a new chunk from scratch**
        - Otherwise, there are no chunks available, so try and get a chunk from top of the heap.
        - If the top of the heap is not big enough, extend it using sbrk.
        - IF the top of the heap can't be extended beacause we ran into something else in the address space, create a discontinuos extenstion using mmap and allocate 
          from there.

    **5. If all else fails,return NULL**
