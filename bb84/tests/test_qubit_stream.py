### tests/test_qubit_stream.py ###
#
# This file implements unit tests for the simulated qubit stream.

import unittest
import socket
import threading
import numpy as np
from bb84.qubit import make_qubit_stream

class TestQubitStream(unittest.TestCase):
    def test_basic_socket(self):
        # make sure basic server structure is working
        # this test will probably be replaced with a stronger one later
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            stream = make_qubit_stream(0, 1)  # dummy id numbers
            sock.connect(('localhost', stream.socket.getsockname()[1]))
            stream.attach_user_address(0, sock.getsockname())
            sock.sendall(bytes('SEND 3 ZZZ', 'utf-8'))
            reply = sock.recv(1024).strip().decode('utf-8').split(' ')

            self.assertTrue(reply[0] == 'SEND' and reply[1] == 'OK:')
            self.assertTrue(all([x in ['0', '1'] for x in reply[2]]))
            stream.shutdown()

if __name__ == '__main__':
    unittest.main()

