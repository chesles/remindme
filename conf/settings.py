import os

ssl_options = {
    "certfile": os.path.join(os.getcwd(), 'conf', 'ssl', 'server.crt'),
    "keyfile": os.path.join(os.getcwd(), 'conf', 'ssl', 'server.key'),
}

