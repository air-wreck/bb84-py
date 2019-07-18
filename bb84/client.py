### bb84/client.py ###
#
# This file implements a basic client. I will document this more fully when I
# am done with it.

from bb84.qubit import Qubit, Bases, Gates
import socket
import numpy as np
import secrets
import sys

class Client(object):
    # constructor arguments:
    #   own_addr: ('hostname', port) tuple for this client
    #   other_addr: ('hostname', port) tuple for intended recipient
    #   n_cmp: number of bytes to use in key comparison step
    #          more bytes is more secure, but also less efficient
    #   send_q_n: default number of qubits to send at once
    #   block: default block size for TCP requests
    #   verbosity: number [0..1], with 0 totally quiet and 1 very verbose
    #   file: place to print output (by default stdout)
    def __init__(self, own_addr, other_addr, n_cmp=4,
                 send_q_n=350, block=4096, verbosity=0.2, file=sys.stdout):
        self.own_host, self.own_port = own_addr
        self.other_host, self.other_port = other_addr
        self.n_cmp = n_cmp
        self.send_q_n = send_q_n
        self.block = block
        self.verbosity = verbosity
        self.file = file

    # print a message
    # consider switching to standard logging module?
    def print(self, message, v=0.1, **kwargs):
        if v <= self.verbosity:
            print(message, file=self.file, **kwargs)

    # prepare 'n' qubits for sending
    # returns utf-8 representations of (bases, qubits)
    def prepare(self, n):
        # randomly decide 'n' bases, each either X or Z
        bases = [secrets.choice(['X', 'Z']) for _ in range(n)]

        # prepare 'n' qubits in those bases
        qubits = []
        for b in bases:
            q = Qubit()
            if b == 'Z':  # prepare in computational basis
                qubits += [secrets.choice([q, q.gate(Gates.X)])]
            else:  # prepare in superposition basis
                q = q.gate(Gates.H)
                qubits += [secrets.choice([q, q.gate(Gates.Z)])]

        # utf-8 representation of bases
        bstr = bytes(''.join(bases), 'utf-8')

        # utf-8 representation of qubits
        # since this is a simulation, we only transmit the first decimal point
        # the receiver will decode this into a high-precision version
        # to keep a semblance of realism, we won't optimize the protocol more
        padded = ['%.1f,%.1f' % tuple(q.state) for q in qubits]
        qstr = bytes(':'.join(padded), 'utf-8')

        return bstr, qstr

    # send utf-8 through a socket and check integrity
    # this assumes the target is relaying the original message
    def check_send(self, sock, message, name='message'):
        self.print('Sending %s...' % name, v=0.2, end=' ')
        sock.sendall(message)
        response = sock.recv(self.block).decode('utf-8')
        if message.decode('utf-8') == response:
            self.print('ok', v=0.2)
            sock.sendall(bytes('ok', 'utf-8'))
        else:
            self.print('Error: response integrity', v=0.1)
            self.print('Message was: %s' % message.decode('utf-8'), v=0.5)
            self.print('Response was: %s' % response, v=0.5)

    # receive a message and relay back the original bytes as confirmation
    def check_recv(self, conn):
        data = conn.recv(self.block)
        conn.sendall(data)
        if conn.recv(self.block).decode('utf-8') != 'ok':
            self.print('Error: client reported message integrity error', v=0.1)
        return data

    # reconstruct qubit objects from the simulated stream
    # due to the difference in realism between the simulated qubits
    # and the simulated qubit stream, this is rather hack-y
    def reconstruct(self, stream):
        qubits = []
        for pair in stream.split(':'):
            a, b = map(lambda x: np.sign(x) * np.sqrt(0.5)
                                 if np.isclose(abs(x), 0.7)
                                 else x, map(float, pair.split(',')))
            qubits += [Qubit(zero=float(a), one=float(b))]
        return qubits

    # get measurements from qubit list and basis string
    def measure(self, qubits, bases):
        measures = []
        for q, b in zip(qubits, bases):
            m, _ = q.measure(Bases.Z if b == 'Z' else Bases.X)
            measures += ['0' if m > 0 else '1']
        return measures

    # filter a key based on two basis strings
    # returns (key, subkey) as hex strings, where subkey is used for comparison
    def filter_key(self, key, b1, b2):
        # filter out the useless bits
        b1 = b1.decode('utf-8')
        b2 = b2.decode('utf-8')
        key = filter(lambda x: x[1] == x[2], zip(key, b1, b2))
        key = ''.join([k for k, _, _ in key])

        # convert the string from bits into hex
        # we'll discard any leftover bits at the end
        hex_key = ''
        for i in range(int(len(key) / 8)):
            hex_key += '%x' % int(key[i:i+8], 2)

        # split the key into subkeys
        if len(hex_key) <= self.n_cmp * 2:
            raise Exception("Generated key too short")
        subkey = hex_key[:self.n_cmp * 2]
        final_key = hex_key[self.n_cmp * 2:]
        return final_key, subkey

    # compare two keys, both represented as hex strings
    # TODO: add more refined statistics to this
    def key_cmp(self, key1, key2):
        if key1 == key2:
            self.print('Confirmed subkey match. Connection is secure.', v=0.2)
            return True
        else:
            self.print('WARNING: subkeys do not match.', v=0.1)
            self.print('WARNING: connection may be compromised.', v=0.1)
            return False

    def write_key_to_file(self, key, filename, mode):
        file = open(filename, mode)
        file.write(key)
        file.close()

    ###########
    # SENDING #
    ###########

    def accept_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.own_host, self.own_port))
        self.print('Listening for connections on %s:%d' %
                   (self.own_host, self.own_port), v=0.5)
        sock.listen()
        conn, addr = sock.accept()
        self.print('Connection from %s:%d' % addr, v=0.5)
        return sock, conn, addr

    # qubit-based send routine
    #   n: the number of qubits to send
    #   sock: the TCP socket to the target
    def send_q(self, n, sock):
        # prepare and measure the qubits
        # in this simulation, we essentially clone and measure upfront
        # in reality, we can still measure here, since measuring in the
        # correct basis will not change the qubit state
        bstr, qstr = self.prepare(n)
        qubits = self.reconstruct(qstr.decode('utf-8'))

        # send the qubits
        self.check_send(sock, qstr, 'qubits')

        # receive the target's basis string
        target_bstr = self.check_recv(sock)

        # send our own basis string
        self.check_send(sock, bstr, 'bases')

        # receive the target's generated key
        target_subkey = self.check_recv(sock).decode('utf-8')

        # measure qubits and combine to form our own final key
        # send the appropriate subkey to the target
        measure = self.measure(qubits, bstr.decode('utf-8'))
        key, subkey = self.filter_key(measure, bstr, target_bstr)
        self.print('Generated key: %s' % key, v=0.3)
        self.check_send(sock, bytes(subkey, 'utf-8'), 'subkey')
        self.key_cmp(subkey, target_subkey)

        return key

    # key-based send routine
    #   n: the total length of the key, in bytes
    #   out: if not None, file name to write output (TODO)
    #   mode: 'w' or 'a' (write or append to file)
    def send_k(self, n, out=None, mode='w'):
        # since the protocol is non-deterministic, there is no way to
        # pre-compute the correct number of qubit blocks to send
        # we will have to keep on sending until our final key is long enough
        key = ''
        n *= 2  # we're using two characters per byte

        # establish connection with target party
        # build up key until full
        # TODO: more robust networking in case connection drops
        sock, conn, addr = self.accept_connection()
        while len(key) < n:
            key += self.send_q(self.send_q_n, conn)
            key += self.receive_q(conn)
        conn.close()
        sock.close()
        key = key[:n]
        self.print('Generated final key: %s' % key, v=0.1)
        self.print('Final key has length %d bytes' % (len(key) / 2), v=0.3)

        # write key to file if requested and return key
        if not out is None:
            self.write_key_to_file(key, out, mode)
        return key

    #############
    # RECEIVING #
    #############

    def request_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.print('Connecting to %s:%d' %
                   (self.other_host, self.other_port), v=0.5)
        sock.connect((self.other_host, self.other_port))
        return sock

    # qubit-based receive routine
    def receive_q(self, conn):
        # receive and decode qubits from sender
        qstr = self.check_recv(conn)
        qubits = self.reconstruct(qstr.decode('utf-8'))

        # generate our own basis string and return it to sender
        bstr, _ = self.prepare(len(qubits))
        self.check_send(conn, bstr, 'bases')

        # receive the original party's basis string
        target_bstr = self.check_recv(conn)

        # measure qubits and discard appropriate bits for final key
        # send the first n_cmp bytes to original sender
        measure = self.measure(qubits, bstr.decode('utf-8'))
        key, subkey = self.filter_key(measure, bstr, target_bstr)
        self.print('Generated key: %s' % key, v=0.3)
        self.check_send(conn, bytes(subkey, 'utf-8'), 'subkey')

        # confirm the generated key from the original sender
        target_subkey = self.check_recv(conn).decode('utf-8')
        self.key_cmp(subkey, target_subkey)

        return key

    # key-based receive routine
    #   n: total length of key
    #   out: None or name of file to write output (TODO)
    #   mode: 'w' or 'a' (write or append to file)
    def receive_k(self, n, out=None, mode='w'):
        key = ''
        n *= 2  # two characters to represent each bit

        # connect to client and do the key exchange
        sock = self.request_connection()
        while len(key) < n:
            key += self.receive_q(sock)
            key += self.send_q(self.send_q_n, sock)
        sock.close()  # unnecessary if client does it?
        key = key[:n]
        self.print('Generated final key: %s' % key, v=0.1)
        self.print('Final key has length %d bytes' % (len(key) / 2), v=0.3)

        # write key to file if requested and return key
        if not out is None:
            self.write_key_to_file(key, out, mode)
        return key

