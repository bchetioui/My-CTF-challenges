#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define READ   0x12345678
#define COPY   0x23456789
#define XOR    0x3456789A
#define ADD    0x456789AB
#define JZ     0x56789ABC
#define JMP    0x6789ABCD
#define CMP    0x789ABCDE
#define SHIFTL 0x89ABCDEF
#define SHIFTR 0x9ABCDEF0
#define RET    0xABCDEF01
#define SETRV  0xBCDEF012
#define POWMOD 0xCDEF0123
#define JNZ    0xDEF01234
#define SUB    0xEF012345

int32_t eip = 0;
char  zflag = 0;
int32_t global_retval = 0;

int32_t stack[1024] = { 0, 0, 0, 0, 0, 0x10001, 0 };

void read32(int32_t *dest, int32_t *src) {
    *dest = *src;
}

void copy32(int32_t *dest, int32_t val) {
    *dest = val;
}

void setrv32(int32_t *ptr) {
    global_retval = *ptr;
}

void xor(int32_t *dest, int32_t *src) {
    *dest ^= *src;
}

void add(int32_t *dest, int32_t *src) {
    *dest += *src;
}

void sub(int32_t *dest, int32_t *src) {
    *dest -= *src;
}

void jz(int32_t dest) {
    if (zflag == 0) eip = dest;
}

void jnz(int32_t dest) {
    if (zflag != 0) eip = dest;
}

void jmp(int32_t dest) {
    eip = dest;
}

void cmp(int32_t *arg1, int32_t *arg2) {
    zflag = !(*arg1 == *arg2);
}

void shiftl(int32_t *value, size_t offset) {
    *value <<= offset;
}

void shiftr(int32_t *value, size_t offset) {
    *value >>= offset;
}

void powmod(int32_t *value, int32_t *mod) {
    unsigned long long result = 1;
    unsigned long long pow = *(stack + 5);

    unsigned long long cpow = *value;
    
    while (pow > 0) {
        if (pow & 1) result = (result * cpow) % *mod;
        pow >>= 1;
        cpow = (cpow * cpow) % *mod;
    }

    *value = result;
}

int32_t swap_int32( int32_t val ) {
    val = ((val << 8) & 0xFF00FF00) | ((val >> 8) & 0xFF00FF ); 
    return (val << 16) | ((val >> 16) & 0xFFFF);
}

void run(char *password) {

    // Putting password at the right spot
    for (int i = 0; i < 5; i++) {
        *(stack + 0x10 + i) = swap_int32(*((int32_t *)password + i));
    }

    int32_t program[] = { /* INSERT OPCODES HERE */ };

    int32_t val1, val2;
    
    while ( 1 ) {
        val1 = program[eip + 1];
        val2 = program[eip + 2];
        
        switch (program[eip]) {
            case READ:
                read32(stack + val1, stack + val2);
                break;
            case COPY:
                copy32(stack + val1, val2);
                break;
            case XOR:
                xor(stack + val1, stack + val2);
                break;
            case ADD:
                add(stack + val1, stack + val2);
                break;
            case SUB:
                sub(stack + val1, stack + val2);
                break;
            case JZ:
                jz(val1 * 3 - 3);
                break;
            case JNZ:
                jnz(val1 * 3 - 3);
                break;
            case JMP:
                jmp(val1 * 3 - 3);
                break;
            case CMP:
                cmp(stack + val1, stack + val2);
                break;
            case SHIFTL:
                shiftl(stack + val1, val2);
                break;
            case SHIFTR:
                shiftr(stack + val1, val2);
                break;
            case SETRV:
                setrv32(stack + val1);
                break;
            case POWMOD:
                powmod(stack + val1, stack + val2);
                break;
            case RET:
                exit(global_retval);
            default:
                break;
        }

        eip += 3;
    }
}

int main() {
    char buffer[21] = { 0 };
    printf("Please enter the password: \n");
    read(STDIN_FILENO, buffer, 20);

    run(buffer);
}
