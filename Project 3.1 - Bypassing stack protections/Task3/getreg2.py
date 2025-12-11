from pwn import *

elf = ELF('./binary')
rop = ROP(elf)

pop_eax = rop.find_gadget(['pop eax', 'ret'])[0]
pop_ebx = rop.find_gadget(['pop ebx', 'ret'])[0]
pop_ecx = rop.find_gadget(['pop ecx', 'ret'])[0]
pop_edx = rop.find_gadget(['pop edx', 'ret'])[0]
int_80 = rop.find_gadget(['int 0x80'])[0]

print(f"pop eax; ret @ {hex(pop_eax)}")
print(f"pop ebx; ret @ {hex(pop_ebx)}")
print(f"pop ecx; ret @ {hex(pop_ecx)}")
print(f"pop edx; ret @ {hex(pop_edx)}")
print(f"int 0x80 @ {hex(int_80)}")