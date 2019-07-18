from bb84.client import Client

alice_address = ('localhost', 65423)
bob_address = ('localhost', 56432)

alice = Client(alice_address, bob_address)
alice.send_k(250, out='tmp_key.txt', mode='a')

