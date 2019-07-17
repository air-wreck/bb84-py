# bb84-py
> a (simulated) Python implementation of the BB84 protocol

This will (hopefully) be a rudimentary Python implementation of BB84, a quantum key distribution protocol, using simulated qubits. There's a >50% chance that I'm using sockets wrong.

## usage
**Scenario:** Alice wants to generate a shared key with Bob by sending him 250 qubits.

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
alice.send(250)
```

**Important!** Bob must run his side of the code before Alice (i.e. he needs to be ready to receive before Alice sends). This isn't a fundamental limitation; it's just how I wrote the code.

These scripts are included as `alice.py` and `bob.py` for your convenience. When I ran them, the two clients agreed upon the secret key `e5cb972f5ebd7bf6ecd8b162c58b17`. However, since the protocol is non-deterministic, your results will likely vary.

## Overview
I'll get around to writing an overview of BB84 later.

## major todos
* write key comparison / statistics routines
* warn user if not enough bits
* look into packet size
* run randomness tests on generated keys
* attempt MITM attack
* write neat command line interface

