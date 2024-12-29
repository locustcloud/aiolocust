Right now this is just a PoC.

Things left to do include:

* Worker communication (connect over zmq, receive spawn/despawn messages, send heartbeats etc)
* An equivalent of Locust's main.py (arg parsing, reading locustfile etc)
* An HTTP User (probably using aiohttp)
* More User-stuff (like wait times)
