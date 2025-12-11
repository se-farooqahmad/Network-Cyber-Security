from pwn import *

elf = ELF('./binary')
rop = ROP(elf)

print(rop.find_gadget(['pop ebx', 'ret']))
print(rop.find_gadget(['pop esi', 'ret']))
print(rop.find_gadget(['pop edi', 'ret']))
