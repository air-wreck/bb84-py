### tests/test_qubit_stream.py ###
#
# This file implements unit tests for the simulated qubit stream.

import unittest
import socket
import threading
import numpy as np
from bb84.qubit import QubitStream

class TestQubitStream(unittest.TestCase):
    def start_test_server(self, client_A, client_B, return_list, init_flag):
        # starts a test server for the given client addresses
        # to find a free port, we let the OS choose one and return
        # it in return_list, C-style
        server = ('localhost', 0)
        stream = QubitStream(server, client_A, client_B)
        return_list[0] = stream.socket.getsockname()[1]
        return_list[1] = stream

        init_flag.set()
        stream.serve_forever()

    def test_basic_socket(self):
        # make sure basic server structure is working
        # this test will probably be replaced with a stronger one later
        dummy = ('localhost', 9999)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            server_info = [0, None]
            server_init_flag = threading.Event()
            threading.Thread(target=self.start_test_server,
                             args=(dummy, dummy, server_info,
                                   server_init_flag)).start()

            server_init_flag.wait()
            sock.connect(('localhost', server_info[0]))
            server_info[1].client_A_addr = sock.getsockname()
            sock.sendall(bytes('SEND 3 ZZZ', 'utf-8'))
            reply = str(sock.recv(1024).strip(), 'utf-8')
            print(reply)
            server_info[1].shutdown()

if __name__ == '__main__':
    unittest.main()



