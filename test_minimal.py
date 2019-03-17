# === test_minimal.py ===
# a short script to set up a (minimal) interactive testing environment
# you can just run with python3 -i

import BB84

server = BB84.Server()
Alice = BB84.Client('Alice')
Bob = BB84.Client('Bob')

Alice.connect(server)
Bob.connect(server)

