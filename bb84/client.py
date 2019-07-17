### bb84/client.py ###
#
# This file implements a basic client. I will document this more fully when I
# am done with it.

from bb84.qubit import Qubit, Bases, Gates
import socket
import numpy as np

class Client(object):
    def __init__(self, own_addr, other_addr):
        self.own_host, self.own_port = own_addr
        self.other_host, self.other_port = other_addr

    # prepares 'n' qubits for sending
    # returns utf-8 representations of (bases, qubits)
    def prepare(self, n):
        # randomly decide 'n' bases, each either X or Z
        bases = [np.random.choice(['X', 'Z']) for _ in range(n)]

        # prepare a 'n' qubits in those bases
        qubits = []
        for b in bases:
            q = Qubit()
            if b == 'Z':  # prepare in computational basis
                qubits += [np.random.choice([q, q.gate(Gates.X)])]
            else:  # prepare in superposition basis
                q = q.gate(Gates.H)
                qubits += [np.random.choice([q, q.gate(Gates.Z)])]

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
        print('Sending %s...' % name, end=' ')
        sock.sendall(message)
        response = sock.recv(4096).decode('utf-8')
        if message.decode('utf-8') == response:
            print('ok')
            sock.sendall(bytes('ok', 'utf-8'))
        else:
            print('Error: response integrity')
            print('Message was: %s' % message.decode('utf-8'))
            print('Response was: %s' % response)

    # receive a message and relay back the original bytes as confirmation
    def check_recv(self, conn, size=4096):
        data = conn.recv(size)
        conn.sendall(data)
        if conn.recv(size).decode('utf-8') != 'ok':
            print('Error: client reported message integrity error')
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
    def filter_key(self, key, b1, b2):
        # filter out the useless bits
        b1 = b1.decode('utf-8')
        b2 = b2.decode('utf-8')
        key = filter(lambda x: x[1] == x[2], zip(key, b1, b2))
        key = ''.join([k for k, _, _ in key])

        # convert the string to bits into hex
        # we'll discard any leftover bits at the end
        hex_key = ''
        for i in range(int(len(key) / 8)):
            hex_key += '%x' % int(key[i:i+8], 2)
        return hex_key

    ###########
    # SENDING #
    ###########

    # ultimate send routine
    def send(self, n):
        # prepare and measure the qubits
        # in this simulation, we essentially clone and measure upfront
        # in reality, we can still measure here, since mearuing in the
        # correct basis will not change the qubit state
        bstr, qstr = self.prepare(n)
        qubits = self.reconstruct(qstr.decode('utf-8'))

        # open the connection to the target
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print('Connecting to %s:%d' % (self.other_host, self.other_port))
            s.connect((self.other_host, self.other_port))

            # send the qubits
            self.check_send(s, qstr, 'qubits')

            # receive the target's basis string
            target_bstr = self.check_recv(s)

            # send our own basis string
            self.check_send(s, bstr, 'bases')

            # measure qubits and combine to form final key
            measure = self.measure(qubits, bstr.decode('utf-8'))
            key = self.filter_key(measure, bstr, target_bstr)
            print(key)

    #############
    # RECEIVING #
    #############

    # ultimate receive routine
    def receive(self):
        # wait for connection from sender
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.own_host, self.own_port))
            print('Listening for connections on %s:%d' % (self.own_host,
                                                          self.own_port))
            s.listen()
            conn, addr = s.accept()
            print('Connection from %s:%d' % addr)

            # receive and decode qubits from sender
            qstr = self.check_recv(conn)
            qubits = self.reconstruct(qstr.decode('utf-8'))

            # generate our own basis string and return it to sender
            bstr, _ = self.prepare(len(qubits))
            self.check_send(conn, bstr, 'bases')

            # receive the original party's basis string
            target_bstr = self.check_recv(conn)

            # measure qubits and discard appropriate bits for final key
            measure = self.measure(qubits, bstr.decode('utf-8'))
            key = self.filter_key(measure, bstr, target_bstr)
            print(key)

            conn.close()
