### qubit.py ###
#
# This file implements a simulated qubit with enough functionality for
# our protocol.

import numpy as np
import socketserver


### single-qubit operations ###

class Bases(object):
    # contains some common bases for convenience
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])

class Gates(object):
    # contains some common gates for convenience
    X = Bases.X
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

class Qubit(object):
    # a single simulated qubit
    def __init__(self, zero=1, one=0, tolerance=1e-9):
        # zero, one = wavefunction in computational basis
        self.state = np.array([zero, one])

        # check that probabilities are normalized
        if not np.isclose(np.linalg.norm(self.state), 1, atol=tolerance):
            raise ValueError('Qubit probabilities were not normalized')

    def gate(self, unitary):
        # check that the gate is unitary
        I = np.identity(unitary.shape[0])
        if not np.allclose(np.matmul(unitary, unitary.conj().T), I):
            raise ValueError('Gates must be unitary matrices')

        # apply a unitary gate to this qubit
        outstate = np.matmul(unitary, self.state)
        return Qubit(zero=outstate[0], one=outstate[1])

    def measure(self, observable):
        # check that the observable is Hermitian
        if not np.allclose(observable, observable.conj().T):
            raise ValueError('Observables must be Hermitian matrices')

        # perform a projective measurement with the given Hermitian
        e_val, e_vect = np.linalg.eig(observable)
        p = list(map(lambda v: abs(v) ** 2, np.matmul(e_vect.T, self.state)))
        i = np.random.choice(len(e_val), p=p)

        # place into state e_vect[i], normalized by the inner product p[i]
        outstate = e_vect.T[i] / np.linalg.norm(e_vect.T[i])
        out = Qubit(zero=outstate[0], one=outstate[1])
        return e_val[i], out


### qubit stream operations ###

class QubitRequestHandler(socketserver.BaseRequestHandler):
    # handles client requests to the qubit stream
    # this can be to either send or measure N qubits
    def handle(self):
        # receive and process data
        self.data = self.request.recv(1024).strip().upper()
        command = list(map(lambda x: x.decode('utf-8'), self.data.split()))

        # validate sender address
        sender = self.client_address
        if sender == self.server.client_A_addr:
            recipient = self.server.client_B_addr
            self.sending_party = 'A'
        elif sender == self.server.client_B_addr:
            recipient = self.server.client_A_addr
            self.sending_party = 'B'
        else:
            print(sender)
            print(self.server.client_A_addr)
            self.request.sendall(bytes('ERR: UNKOWN SENDER', 'utf-8'))
            return

        # command[0] is the instruction: either SEND or MEASURE
        if len(command) is not 3:
            self.request.sendall(bytes('ERR: MALFORMED REQUEST', 'utf-8'))
            return
        if command[0] not in ['SEND', 'MEASURE']:
            print(command[0])
            self.request.sendall(bytes('ERR: INVALID COMMAND', 'utf-8'))
            return

        # command[1] is the number 0 < N < 501 of qubits
        try:
            N = int(command[1])
            assert 0 < N < 501
        except:
            self.request.sendall('ERR: BAD N')
            return

        # command[2] is the string of basis, of length N
        # each must be either 'Z' (computational) or 'X' (superposition)
        basis = [c for c in command[2]]
        if len(command[2]) is not N:
            self.request.sendall(bytes('ERR: BASIS LENGTH DOES NOT MATCH',
                                       'utf-8'))
            return
        if not all(map(lambda c: c in ['X', 'Z'], basis)):
            self.request.sendall(bytes('ERR: INVALID BASIS', 'utf-8'))
            return

        # do a SEND: we prepare N qubits in the appropriate basis
        # in the target mailbox
        # TODO: this should then return the measurement of the qubits in the
        #       sending basis, possibly along with N for integrity check
        if command[0] ==  'SEND':
            if self.sending_party == 'A':
                target_mbox = self.server.mailbox_B
            else:
                target_mbox = self.server.mailbox_A
            target_mbox += [Qubit() if b is 'Z' else Qubit().gate(Gates.H)
                            for b in basis]
            self.request.sendall(bytes('SEND OK', 'utf-8'))
            return

        # do a MEASURE: we give the results of measuring N qubits
        # from the front of the sender's mailbox in the given basis
        # we then discard the used qubits
        if self.sending_party == 'A':
            target_mbox = self.server.mailbox_A
        else:
            target_mbox = self.server.mailbox_B
        if len(target_mbox) < N:
            self.request.sendall(bytes('ERR: INSUFFICIENT QUBITS IN QUEUE\n',
                                       'utf-8'))
            return
        qubits_to_measure = target_mbox[:N]
        target_mbox = target_mbox[N:]
        results = []
        for i, b in enumerate(basis):
            if b is 'Z':
                m, _ = qubits_to_measure[i].measure(Bases.Z)
            else:
                m, _ = qubits_to_measure[i].measure(Bases.X)
            results += ['0' if m is 1 else '1']
        self.request.sendall(bytes('MEASURE OK: %s\n' % ''.join(results), 'utf-8'))

class QubitStream(socketserver.TCPServer):
    # a simulated secure stream of qubits between parties A and B
    def __init__(self, self_addr, client_A_id, client_B_id):
        super(QubitStream, self).__init__(self_addr, QubitRequestHandler)
        self.client_A_id = client_A_id
        self.client_B_id = client_B_id
        self.client_A_addr = ('localhost', 0)
        self.client_B_addr = ('localhost', 0)

        self.mailbox_A = []
        self.mailbox_B = []

    def attach_user_address(self, client_id, client_addr):
        if client_id == self.client_A_id:
            self.client_A_addr = client_addr
        elif client_id == self.client_B_id:
            self.client_B_addr = client_addr
        else:
            raise ValueError('Unrecognized client ID [%d]' % client_id)

