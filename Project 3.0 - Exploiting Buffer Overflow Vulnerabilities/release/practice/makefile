SOURCES=vuln.c
TARGETS=$(SOURCES:.c=)

CC=gcc
CFLAGS=-g -m32 -static -Wno-deprecated-declarations -fno-stack-protector -z execstack

all: $(TARGETS)

$(TARGETS): $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $@.c

clean:
	rm -f $(TARGETS)