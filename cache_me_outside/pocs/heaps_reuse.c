#include<stdio.h>
#include<stdlib.h>

int main() {
    int *arr;
    arr = (int *)malloc(4 * sizeof(int));
    arr[0] = 0x22;
    arr[1] = 0x33;
    arr[2] = 0x44;
    arr[3] = 0x55;

    puts("\x1B[32m[*]This worked!!!\x1B[0m"); 

    // free the heap
    free(arr);

    // make a smaller request
    int *arr2;
    arr2 = (int *)malloc(2 * sizeof(int));
    
    // Is same region allocated..
    puts("\x1B[33m[+] Checking the contents of reallocated region\x1B[0m");
    int i;
    for(int i = 0; i < 2; ++i)
        printf("arr2[%d] = %x\n", i, arr2[i]);

    puts("\x1B[33m[+] reusing the same pointer for reallocation \x1B[0m");

    arr = (int *)malloc(2 * sizeof(int));

    puts("\x1B[33m[+] Checking the contents of reallocated region\x1B[0m");
    for(i = 0; i < 2; ++i)
        printf("arr[%d] = %x\n", i, arr[i]);

    puts("\x1B[33m[+] Cleaning everything\x1B[0m");

    free(arr2);
    free(arr);

    puts("\x1B[32m[*] POC 1 completed\x1B[0m");
    return 0; 

}
