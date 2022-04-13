#!/usr/bin/env python3

from pwn import *

exe = ELF("./heapedit_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.27.so")

context.binary = exe

"""
    To run locally: ./solve.py LOCAL
    To run and attach gdb: ./solve.py DEBUG
    To run remotely: ./solve.py

"""

def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("addr", 1337)

    return r


def main():
    r = conn()

    # good luck pwning :)

    r.interactive()


if __name__ == "__main__":
    main()
