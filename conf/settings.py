import os

ssl_options = {
    "certfile": os.path.join(os.getcwd(), 'conf', 'ssl', 'server.crt'),
    "keyfile": os.path.join(os.getcwd(), 'conf', 'ssl', 'server.key'),
}

users = {
    "host": "184.169.147.21",
    "port": 80
}

eventnetwork = {
    "host": "localhost",
    "port": 80
}
