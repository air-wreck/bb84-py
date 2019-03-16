# I'm going to keep the module as a single BB84.py file for now
# I'll organize it after I'm done prototyping
# TODO: split file
# TODO: add GPL boilerplate

from random import uniform
from math import floor

class Qubit(object):
    def set_random_basis(self):
        if uniform(0, 1) < 0.5:
            self.basis = '0'
        else:
            self.basis = '1'
        return self.basis

    def set_random_state(self):
        if uniform(0, 1) < 0.5:
            self.state = 0
        else:
            self.state = 1
        return self.state

    def measure(self, basis):
        # if we measure in the same basis, return qubit value
        if basis is self.basis:
            return self.state

        # otherwise, when wavefunction collapses, probability is 0.5/0.5
        self.basis = basis
        return self.set_random_state()

class Message(object):
    def __init__(self, sender, recipient, text, msg_type='Text'):
        self.sender = sender
        self.recipient = recipient
        self.text = text
        self.msg_type = msg_type

        if msg_type not in ['Basis', 'Key']:
            self.msg_type = 'Text'

class Server(object):
    def __init__(self, name='Forum'):
        self.name = name
        self.stack = []

    def post_text(self, sender, recipient, text):
        self.stack += [Message(sender, recipient, text, 'Text')]

    def post_basis(self, sender, recipient, basis):
        basis = ''.join(basis)
        self.stack += [Message(sender, recipient, basis, 'Basis')]

    def post_sifted_key(self, sender, recipient, sifted_key):
        key = ''.join(sifted_key)
        self.stack += [Message(sender, recipient, key, 'Key')]

    def filter_msgs(self, sender=None, recipient=None, msg_type=None):
        ret = self.stack
        if sender is not None:
            ret = filter(lambda m: m.sender is sender, ret)
        if recipient is not None:
            ret = filter(lambda m: m.recipient is recipient, list(ret))
        if msg_type is not None:
            ret = filter(lambda m: m.msg_type is msg_type, list(ret))
        return list(ret)

class Client(object):
    def __init__(self, name):
        self.name = name

    ### low-level protocol methods
    def generate_qubits(self, n):
        qubits = [Qubit() for _ in range(n)]
        bases = [q.set_random_basis() for q in qubits]
        for q in qubits:
            q.set_random_state()
        return qubits, bases

    def receive_qubits(self, qubits, sender, callback):
        # upon receive, randomly choose a basis for each qubit
        # measure them and then publicly announce the chosen basis
        bases = ['0' if uniform(0, 1) < 0.5 else '1' for _ in qubits]
        bits = [q.measure(b) for q, b in zip(qubits, bases)]
        self.server.post_basis(self.name, sender, bases)

        # we notify the sender that we have posted our bases
        # after they post their bases, we use it to generate our keys
        callback(self.name)
        self.keygen(bits, self.get_sender_bases(sender), bases, True)

    def get_sender_bases(self, sender):
        basis_2 = self.server.filter_msgs(sender=sender, recipient=self.name,
                                          msg_type='Basis')
        return list(basis_2[-1].text)

    def post_sender_bases(self, bases):
        def callback(recipient):
            self.server.post_basis(self.name, recipient, bases)

        return callback

    def keygen(self, bits, basis_1, basis_2, order=False):
        # we keep the bits for which we measured in the same basis
        key = zip(bits, basis_1, basis_2)
        key = [bit if b1 is b2 else None for bit, b1, b2 in key]
        key = list(filter(lambda bit: bit is not None, key))

        # we round key down to even number and split for encrypt/decrypt
        # important: b1 and b2 must be SWAPPED for the two parties
        # this is accomplished by setting order to True for one party
        key_len = floor(len(key) / 2.)
        if order:
            self.encrypting_key = key[:key_len]
            self.decrypting_key = key[key_len:2*key_len]
        else:
            self.encrypting_key = key[key_len:2*key_len]
            self.decrypting_key = key[:key_len]

    def ascii_bitwise_xor(self, key, string):
        bits = list(map(int, list(string)))
        return ''.join([str(a ^ b) for a, b in zip(bits, key)])

    ### high-level chat methods
    def connect(self, server):
        self.server = server

    def handshake(self, target, n=500, sift_len=50):
        qubits, bases = self.generate_qubits(n)
        target.receive_qubits(qubits, self.name, self.post_sender_bases(bases))

        # measure in matching basis and construct key
        bits = [q.measure(b) for q, b in zip(qubits, bases)]
        self.keygen(bits, bases, self.get_sender_bases(target.name))

        # test if sifted keys match
        # to prevent attacks, post random test indices
        # TODO: implement this check

    def encrypt(self, text):
        # simple one-time-pad
        # we decrypt and then discard the used bits
        # I'll implement error checking for insufficient bits later
        text = ''.join([format(ord(c), '08b') for c in text])
        ciphertext = self.ascii_bitwise_xor(self.encrypting_key, text)
        self.encrypting_key = self.encrypting_key[len(ciphertext):]
        return ciphertext

    def decrypt(self, text):
        # like self.ecrypt(), except that we translate back to ASCII
        plaintext = self.ascii_bitwise_xor(self.decrypting_key, text)
        self.decrypting_key = self.decrypting_key[len(plaintext):]
        return ''.join([chr(int(''.join(plaintext[i:i+8]), 2))
                        for i in range(0, len(plaintext), 8)])

