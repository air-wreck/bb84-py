### tests/test_qubit.py ###
#
# This file contains unit tests for the simulated qubit.

import unittest
import numpy as np
from bb84.qubit import Qubit, Bases, Gates

class TestQubit(unittest.TestCase):
    def cmp_states(self, a, b, tolerance=1e-9):
        # compare two state vectors component-wise
        self.assertTrue(np.isclose(a[0], b[0], atol=tolerance))
        self.assertTrue(np.isclose(a[1], b[1], atol=tolerance))

    def test_norm(self):
        # initialization fails with non-normalized amplitudes
        with self.assertRaises(ValueError):
            Qubit(zero=1+1j, one=1+1j)

    def test_randomization(self):
        # applying a Hadamard puts the qubit into a superposition state
        q = Qubit().gate(Gates.H)
        self.cmp_states(q.state, np.array([1, 1]) * np.sqrt(0.5))

    def test_measure_Z(self):
        # measuring in the computational basis yields 1 each time
        q = Qubit()
        for _ in range(100):
            val, vect = q.measure(Bases.Z)
            self.assertTrue(np.isclose(val, 1))
            self.cmp_states(vect.state, Qubit().state)

    def test_measure_H(self):
        # measuring after Hadamard yields +1/-1 with 0.5 probability
        ones = 0
        for _ in range(100):
            val, vect = Qubit().gate(Gates.H).measure(Bases.Z)
            try:
                self.assertTrue(np.isclose(val, 1))
                self.cmp_states(vect.state, Qubit().state)
                ones += 1
            except AssertionError:
                self.assertTrue(np.isclose(val, -1))
                self.cmp_states(vect.state, Qubit(zero=0, one=1).state)
        self.assertTrue(40 <= ones <= 60)

    def test_measure_X(self):
        # measuring in X basis yields +1/-1 with 0.5 probability
        ones = 0
        for _ in range(100):
            val, vect = Qubit().measure(Bases.X)
            try:
                self.assertTrue(np.isclose(val, 1))
                self.cmp_states(vect.state, np.array([1, 1]) / np.sqrt(2))
                ones += 1
            except AssertionError:
                self.assertTrue(np.isclose(val, -1))
                # not sure how to foce numpy to choose the [1, -1] eigenvector
                self.cmp_states(vect.state, np.array([-1, 1]) / np.sqrt(2))
        self.assertTrue(40 <= ones <= 60)

    def test_measure_H_X(self):
        # applying H then measuring in X yields +1 each time
        for _ in range(100):
            val, _ = Qubit().gate(Gates.H).measure(Bases.X)
            self.assertTrue(np.isclose(val, 1))

    def test_apply_H_H(self):
        # two Hadamard gates cancel
        q = Qubit().gate(Gates.H).gate(Gates.H)
        self.cmp_states(q.state, Qubit().state)

    def test_invalid_gate(self):
        # a non-unitary gate should fail
        G = np.array([[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            Qubit().gate(G)

    def test_invalid_measure(self):
        # a non-Hermitian measurement should fail
        M = np.array([[1j, 3], [-3, 1+4j]])
        with self.assertRaises(ValueError):
            Qubit().measure(M)

if __name__ == '__main__':
    unittest.main()
