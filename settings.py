f = open("template.html")
TEMPLATE = f.read()
f.close()

MAX_WORKERS = 4
PORT = 8000
NETWORK_TEST_SERVER_PORT = 7000
LOAD_TEST_TIME = 10
