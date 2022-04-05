#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>      // for brk syscall and sbrk

int main() {
    int *area;
    area = (int *) malloc(4 * sizeof(int));
    puts("\x1B[32m[*] Printing the dynamically allocated array content\x1B[0m");
    area[0] = 0x32;
    area[1] = 0x33;
    area[2] = 0x34;
    area[3] = 0x35;
  //area[4] = 0x69;     // this will be violation as accessing outside
    int i;
    for(i = 0; i < 4; ++i)
        printf("area[%d] = %x\n", i, area[i]);
    
    // finding the location of heap boundary..(they call it break location)
    void *addr = sbrk(0);
    printf("\x1B[1;32m[*] Heap expanded upto -> %p\n", addr);
    return 0;
}
