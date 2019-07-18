# bb84-py
> a (simulated) Python implementation of the BB84 protocol

This will (hopefully) be a rudimentary Python implementation of BB84, a quantum key distribution protocol, using simulated qubits. There's a >50% chance that I'm using sockets wrong.

You see, I started writing this thinking that I'd brush up on my quantum while learning network programming! Now, two re-writes in, I can safely say that I've forgotten all of quantum mechanics and still don't know how network programming works.

## usage
**Scenario:** Alice wants to generate a shared key with Bob by sending him 350 qubits.

1. Bob prepares to receive qubits from Alice.
``` python
# bob.py
from bb84.client import Client

alice_address = ('localhost', 65423)
bob_address = ('localhost', 56432)

bob = Client(bob_address, alice_adress)
bob.receive()
```
2. Alice sends the qubits to Bob.
``` python
# alice.py
from bb84.client import Client

alice_address = ('localhost', 65423)
bob_address = ('localhost', 56432)

alice = Client(alice_address, bob_address)
alice.send(350)
```

**Important!** Bob must run his side of the code before Alice (i.e. he needs to be ready to receive before Alice sends). This isn't a fundamental limitation; it's just how I wrote the code.

These scripts are included as `alice.py` and `bob.py` for your convenience. When I ran them, the two clients agreed upon the secret key `3a64c993265cb962c59b367ce9c3870e0c1825`. However, since the protocol is non-deterministic, your results will likely vary.

## Overview
I'll get around to writing an overview of BB84 later.

## major todos
* write key comparison / statistics routines
* warn user if not enough bits
* look into packet size
* run randomness tests on generated keys
* attempt MITM attack
* write neat command line interface

