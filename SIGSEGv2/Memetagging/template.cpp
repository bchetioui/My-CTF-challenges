#include <fstream>
#include <iostream>
#include <random>
#include <string>
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
#define PFLAG  0xCDEF0123
#define JNZ    0xDEF01234
#define SUB    0xEF012345

std::mt19937 mt_rand(time(0));

char  zflag = 0;
int32_t global_retval = 0;

// 6 first addresses are reserved.
// 0, 1, 2, 3, 4 = eax, ebx, ecx, edx, label
// 5 = modval
int32_t stack[1024] = { 0 };

uint32_t program[] = { /* INSERT OPCODES HERE */ };
uint32_t tags[ /* INSERT LENGTH HERE */] = { 0 };

uint32_t database[256] = { 0 };
uint32_t database_tags[256] = { 0 };

void read32(int32_t *dest, int32_t *src) {
    *dest = *src;
}

void copy32(int32_t *dest, int32_t val) {
    *dest = val;
}

void setrv32(int32_t *ptr) {
    global_retval = *ptr;
}

/*void xor(int32_t *dest, int32_t *src) {
    *dest ^= *src;
}*/

void add(int32_t *dest, int32_t *src) {
    *dest += *src;
}

void sub(int32_t *dest, int32_t *src) {
    *dest -= *src;
}

void jz(int32_t dest) { // TODO: add ptr to EIP
    //if (zflag == 0) eip = dest;
}

void jnz(int32_t dest) { // TODO: add ptr to EIP
    //if (zflag != 0) eip = dest;
}

void jmp(int32_t dest) { // TODO: add ptr to EIP
    //eip = dest;
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

void print_flag() {
    std::ifstream is ("flag.txt", std::ifstream::binary);
    if (is) {
        // get length of file:
        is.seekg (0, is.end);
        int length = is.tellg();
        is.seekg (0, is.beg);

        char *flag = new char [length];

        is.read(flag, length);
        std::cout << "Flag is " << flag << std::endl;
        is.close();
    }
    else {
        std::cout << "Error opening flag.txt" << std::endl;
    }
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

void run_checker(uint64_t eip) {

    int32_t val1, val2;
    
    while ( 1 ) {
        if (tags[(eip & 0xff) / 3] != eip >> 32) {
            std::cout << "Corrupted eip!" << std::endl;
            exit(1);
        }

        eip = eip & 0xff;

        val1 = program[eip + 1];
        val2 = program[eip + 2];
        
        switch (program[eip]) {
            case READ:
                read32(stack + val1, stack + val2);
                break;
            case COPY:
                copy32(stack + val1, val2);
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
            case PFLAG:
                print_flag();
                break;
            case RET:
                return;
            default:
                break;
        }

        eip += 3;
        eip = (((int64_t)tags[(eip & 0xff) / 3]) << 32) | (eip & 0xff);
    }
}

void bite(uint64_t *x) {
    return;
}

void insert_into_database() {
    uint32_t value = 0;
    uint32_t index = 0;

    std::cout << "Please provide a positive value to insert in the database:" << std::endl;
    std::cin >> value;

    if (value < 0) {
        std::cout << "Nope!" << std::endl;
        return;
    }

    std::cout << "What index would you like to store your value at? (0 <= index < 256)" << std::endl;
    std::cin >> index;

    if (index < 0 || index > 255) {
        std::cout << "Nope!" << std::endl;
        return;
    }

    database[index] = value;
    database_tags[index] = mt_rand();

    std::cout << "Value has been inserted!" << std::endl;
    std::cout << "Here's your tag: " << database_tags[index] << std::endl;
}

void access_database() {
    int64_t tagged_index = 0;

    std::cout << "Please provide a tagged index to access the database" << std::endl;
    std::cin >> tagged_index;

    if (database_tags[tagged_index & 0xff] != tagged_index >> 32) {
        std::cout << "Corrupted index!" << std::endl;
        return;
    }

    std::cout << "Your value is " << database[tagged_index & 0xff] << std::endl;
}

void run() {
    uint64_t eip;
    char name[24] = "lol memetagging";

    for (int i = 0; i < 1000; ++i) {
        eip = ((uint64_t)tags[0]) << 32;
        int32_t option;
        std::string printable_name(name);

        std::cout << "Your name is: " << printable_name << std::endl;
        std::cout << "What do you want to do this round?" << std::endl;
        std::cout << "1. Change your username" << std::endl;
        std::cout << "2. Store an element in your database" << std::endl;
        std::cout << "3. Access an element in your database" << std::endl;
        std::cout << "4. Quit" << std::endl;
        std::cout << "> ";

        std::cin >> option;

        int char_read = 0;

        switch (option) {
            case 1:
                char_read = read(STDIN_FILENO, name, 40);
                if (char_read < 0) {
                    std::cout << "Error, skipping";
                    break;
                }
                if (char_read > 23) {
                    name[23] = '\0';
                }
                else {
                    name[char_read] = '\0';
                }
                break;
            case 2:
                insert_into_database(); 
                break;
            case 3:
                access_database();
                break;
            default:
                std::cout << "Bye~!" << std::endl;
                exit(1);
        }

        run_checker(eip);
    }

}

int main() {
    int nb_tags = sizeof(tags) / (sizeof(tags[0]));

    for (int i = 0; i < nb_tags; i++) {
        tags[i] = mt_rand();
    }
    
    std::cout << "****************************************" << std::endl;
    std::cout << "*** Welcome to my own memtagging poc ***" << std::endl;
    std::cout << "****************************************" << std::endl;
    std::cout << std::endl;

    std::cout << "Memtagging is coming soon. Show me you're ready to pwn it." << std::endl;
    std::cout << std::endl;

    run();
}
