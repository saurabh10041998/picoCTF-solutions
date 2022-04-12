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

## Free strategy
1. If the pointer is NULL, the C standard defines the behaviour as "do nothing".
2. Otherwise, convert the pointer back to chunk by subtracting the size of chunk metadata.
3. Perform a few sanity checks on the chunk, and abort if the sanity checks fail.
4. If the chunks fit into tcache bin, store it there.
5. If the chunks has  M bit set, give it back to OS system via munmap.
6. Otherwise we obtain the heap lock and then:  
    1. If the chunks fit into a fastbin, put it on the corresponding fast bin and we're done.
    2. If chunk is > 64MB, consolidate the fast bins immediately and put the resulting merged chunks on the unsorted bin.
    3. Merge the chunks backwards and forwards with the neighbouring freed chunks in the small,large and unsorted bins.
    4. If resulting chunk lies at top of the heap, merge it into the top of the heap rather that storing it in a bin.
    5. Otherwise, store it in unsorted bin.(Malloc will later do the work to put entries from the unsorted bin into the small or large bins)
