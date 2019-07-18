# bb84-py
> a (simulated) Python implementation of the BB84 protocol

This will (hopefully) be a rudimentary Python implementation of BB84, a quantum key distribution protocol, using simulated qubits. There's a >50% chance that I'm using sockets wrong.

You see, I started writing this thinking that I'd brush up on my quantum while learning network programming! Now, two re-writes in, I can safely say that I've forgotten all of quantum mechanics and still don't know how network programming works.

## quickstart usage
**Scenario:** Alice wants to generate a 250-byte shared secret (a "key") with Bob.

1. Alice runs her code.
``` python
# alice.py
from bb84.client import Client

alice_address = ('localhost', 65423)
bob_address = ('localhost', 56432)

alice = Client(alice_address, bob_address)
key = alice.send_k(250)
```
2. Bob runs his code to receive Alice's connection.
``` python
# bob.py
from bb84.client import Client

alice_address = ('localhost', 65423)
bob_address = ('localhost', 56432)

bob = Client(bob_address, alice_address)
key = bob.receive_k(250)
```

These scripts are included as `alice.py` and `bob.py` for your convenience.

## overview
I'll get around to writing an overview of BB84 later.

## major todos
* write key comparison / statistics routines
* look into packet size / more robust networking
* run randomness tests on generated keys
* attempt MITM attack
* write neat command line interface

