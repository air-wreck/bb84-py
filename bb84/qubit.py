### qubit.py ###
#
# This file implements a simulated qubit with enough functionality for
# our protocol. Actually, the qubit functionality is probably overkill.

import numpy as np

class Bases(object):
    # contains some common bases for convenience
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])

class Gates(object):
    # contains some common gates for convenience
    X = Bases.X
    Z = Bases.Z
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    S = np.array([[1, 0], [0, 1j]])

class Qubit(object):
    # a single simulated qubit
    def __init__(self, zero=1, one=0, tolerance=1e-9):
        # zero, one = wavefunction in computational basis
        self.state = np.array([zero, one])

        # check that probabilities are normalized
        if not np.isclose(np.linalg.norm(self.state), 1, atol=tolerance):
            raise ValueError('Qubit probabilities must be normalized')

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

