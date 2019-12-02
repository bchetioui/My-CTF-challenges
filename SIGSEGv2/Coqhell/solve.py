from pwn import *

i = 0

p = ''

while True:
    p = process('./chall.py')
    text = p.recvuntil('Solve problem')
    if 'n = n + 0' in text:
        break
    else:
        i += 1
        p.close()

print('[+] Found easy problem!')

p.sendline('1')
p.sendline('3032206e0a30330a30360a30352049486e0a3033')

for i in range(1, 100):
    print('[+] Passing round {}'.format(i + 1))
    p.send('2\n' * i)
    p.sendline('1')
    p.sendline('3032206e0a30330a30360a30352049486e0a3033')

text = p.recvuntil('Coq master!')
p.interactive()
