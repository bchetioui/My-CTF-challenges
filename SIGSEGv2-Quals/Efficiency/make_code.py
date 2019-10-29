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
POWMOD = 0xCDEF0123
JNZ    = 0xDEF01234
SUB    = 0xEF012345

def generateProgram():
    # FLAG SHOULD BE 
    flag = 'sigsegv{VM3d_stuff!}'
    parts = []

    e = 0x10001

    for i in range(0, len(flag) / 4):
        n = 2**32
        # Make sure to avoid overflows in program
        while not n < 2**31:
            p = getPrime(15)
            q = getPrime(15)

            if p == 0x10001 or q == 0x10001:
                continue
            
            n = p * q
        
        parts.append((pow(bytes_to_long(flag[i * 4:i * 4 + 4]), e, n), p, q, n))

    for part in parts:
        enc, p, q, n = part
        print 'enc = ' + str(enc)
        print 'p = ' + str(p)
        print 'q = ' + str(q)
        print 'n = ' + str(n)

    # Aim is for program to print 1
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

    # To export packed data:
    """
    with open('instructions', 'w') as f:
        f.write(''.join(map(packer, program)))
    """

    # To write source:
    packed_program = ''.join(map(packer, program))
    packed_codes = [packed_program[i:i + 4] for i in range(0, len(packed_program), 4)]
    insertable_program = ', '.join(map(lambda c: '0x' + c[::-1].encode('hex'), packed_codes))
    
    with open('template.c') as template:
        source = template.read().replace('/* INSERT OPCODES HERE */', insertable_program)
        with open('production.c', 'w') as target:
            target.write(source)

generateProgram()
