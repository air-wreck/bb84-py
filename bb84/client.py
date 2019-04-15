### bb84/client.py ###
#
# This file implements a basic client. I will document this more fully when I
# am done with it.

import http.server

class Client(object):
    encrypting_keys = {}
    decrypting_keys = {}
