#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void secret() {
    printf(">> you have found the secret function\n");
}

void process_request()
{
    char buffer[8];
    gets(buffer);
    printf("> %s\n", buffer);
}   

int main()
{
    process_request();
    return 0;
}