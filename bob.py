from bb84.client import Client

alice_address = ('localhost', 65423)
bob_address = ('localhost', 56432)

bob = Client(bob_address, alice_address)
bob.receive()

