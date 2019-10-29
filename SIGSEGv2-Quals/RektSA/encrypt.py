#!/usr/bin/python2.7

import sys
from secret import FLAG
from Crypto.Util.number import getPrime, bytes_to_long
from gmpy2 import invert

p = getPrime(1024)
q = getPrime(1024)
r = getPrime(1028)

e = 0x10001

N = p * q * r
phi = (p - 1) * (q - 1) * (r - 1)

print 'N:', N
print 'phi:', phi % 2**2050
print 'r:', r

print 'Give me d: '

sys.stdout.flush()

try:
    d = int(raw_input())
except:
    print 'Invalid input!'
    exit(1)

if d == invert(e, phi):
    print 'Congratulations: %s' % FLAG
else:
    print 'Nope!'
    exit(1)
