### bb84/client.py ###
#
# This file implements a basic client. I will document this more fully when I
# am done with it.

from bb84.qubit import QubitStream
import socket

class Connection(object):
    # represents a connection with another party
    def __init__(self, target_addr, qubit_stream, sock):
        self.target_addr = target_addr
        self.qubit_stream = qubit_stream
        self.socket = sock

class Client(object):
    # represents a user on the network
    def __init__(self, name, id_no):
        self.name = name
        self.id_no = id_no

        # TODO: we need to construct self.server TCP server to receive
        #       messages from other users
        self.connections = {}

    def connect(self, qubit_stream, target_id, target_addr):
        # create a socket for the qubit_stream connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(qubit_stream.socket.getsockname())

        # attach this address to the qubit stream
        qubit_stream.attach_user_address(self.id_no, sock.getsockname())
        conn = Connection(target_addr, qubit_stream, sock)
        self.connections[str(target_id)] = conn

    def send_qubits(self, basis_str, target_id):
        # sends qubits prepared in the specified basis to the target
        # returns number of qubits sent, or -1 on error
        sock = self.connections[str(target_id)].socket
        sock.sendall(bytes('SEND %d %s' % (len(basis_str), basis_str),
                           'utf-8'))
        reply = sock.recv(1024).strip().decode('utf-8')
        if reply[:7] == 'SEND OK':
            # TODO: store the results of the measurements somewhere,
            #       probably in the connection object
            return len(basis_str)
        return -1

