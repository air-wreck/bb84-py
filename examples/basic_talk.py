### examples/basic_talk.py ###
#
# This file contains a basic usage example for the BB84 protocol.

import bb84

Alice = bb84.client.Client('Alice', 0)
Bob = bb84.client.Client('Bpb', 1)

# create a simulated quantum channel between Alice and Bob
dummy_addr = ('localhost', 0)
qubit_stream = bb84.qubit.QubitStream(dummy_addr, Alice.id_no, Bob.id_no)
Alice.join_stream(qubit_stream, Bob.id_no, Bob.server.socket.getsockname())
Bob.join_stream(qubit_stream, Alice.id_no, Alice.server.socket.getsockname())

# Alice chooses some qubits to send
# I realized that I need to fix the basis method so that it randomly chooses
# in the specified basis, not just the zero eigenstate in that basis
Alice.send_qubits('ZZZ', Bob.id_no)

