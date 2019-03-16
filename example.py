# === example.py ===
# simple usage example for BB84.py

import BB84

# we set up the connection between Alice and Bob
server = BB84.Server()
Alice = BB84.Client('Alice')
Bob = BB84.Client('Bob')

Alice.connect(server)
Bob.connect(server)
Alice.handshake(Bob)

# now that they are connected, we can chat
print(Bob.decrypt(Alice.encrypt('Hello!')))
print(Alice.decrypt(Bob.encrypt('Hi yourself!')))

# this is what the raw encrypted text looks like
print(Alice.encrypt('Oh...'))
print(Alice.encrypt('Bye!'))

# note that we must encrypt/decrypt in sync, or it will fail
print(Bob.decrypt(Alice.encrypt('this should fail!')))

