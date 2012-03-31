import os

ssl_options = {
    "certfile": os.path.join(os.getcwd(), 'conf', 'ssl', 'server.crt'),
    "keyfile": os.path.join(os.getcwd(), 'conf', 'ssl', 'server.key'),
}

users = {
    "host": "localhost",
    "port": 8082
}

eventnetwork = {
    "host": "localhost",
    "port": 8080
}
