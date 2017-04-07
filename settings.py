import multiprocessing


f = open("template.html")
TEMPLATE = f.read()
f.close()

MAX_WORKERS = multiprocessing.cpu_count()
PORT = 8000
LOAD_TEST_TIME = 600  # seconds
