from gmpy2 import invert
from Crypto.Util.number import getPrime, long_to_bytes, bytes_to_long
import struct

def pack(val):
    return struct.pack('I', val)

def pack1(opcode, val1):
    return pack(opcode) + pack(val1) + pack(0)

def pack2(opcode, val1, val2):
    return pack(opcode) + pack(val1) + pack(val2)

def packer(cmd):
    if len(cmd) == 2:
        return pack1(cmd[0], cmd[1])
    elif len(cmd) == 3:
        return pack2(cmd[0], cmd[1], cmd[2])
    else:
        print 'ERROR: ' + str(cmd)
        exit(1)

READ   = 0x12345678
COPY   = 0x23456789
XOR    = 0x3456789A
ADD    = 0x456789AB
JZ     = 0x56789ABC
JMP    = 0x6789ABCD
CMP    = 0x789ABCDE
SHIFTL = 0x89ABCDEF
SHIFTR = 0x9ABCDEF0
RET    = 0xABCDEF01
SETRV  = 0xBCDEF012
PFLAG  = 0xCDEF0123
JNZ    = 0xDEF01234
SUB    = 0xEF012345

def generateProgram():
    # Aim is for program to print 1
    """
    program = [ [ COPY, 0x4, 3 ],
                [ JMP, 4 ],
                [ SETRV, 0x3ff ],
                [ RET, 0 ],
                [ COPY, 0x5, 0x10001 ] ]

    for i in range(len(parts)):
        enc, _, _, n = parts[i]
        program.append([ COPY, 0x100 + i, enc ])
        program.append([ COPY, 0x200 + i, n   ])

    # Input flag will be arbitrarily put at 0x10

    for i in range(len(parts)):
        program.append([ POWMOD, 0x10 + i, 0x200 + i ])
        program.append([ CMP, 0x10 + i, 0x100 + i ])
        program.append([ JNZ, 2 ])

    program.append([ COPY, 0x3ff, 1 ])
    program.append([ JMP, 2 ])

    """

    # Simplistic program will have to do.
    program = [ [ RET, 0 ],
                [ PFLAG, 0, 0 ],
                [ RET, 0 ] ]

    # To write source:
    packed_program = ''.join(map(packer, program))
    packed_codes = [packed_program[i:i + 4] for i in range(0, len(packed_program), 4)]
    insertable_program = ', '.join(map(lambda c: '0x' + c[::-1].encode('hex'), packed_codes))
    
    with open('template.cpp') as template:
        source = template.read().replace('/* INSERT OPCODES HERE */', insertable_program)
        source = source.replace('/* INSERT LENGTH HERE */', str(len(program)))

        with open('production.cpp', 'w') as target:
            target.write(source)

generateProgram()
