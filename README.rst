Benchmarks of running a long-term process within an HTTP server
===============================================================

Below are performance benchmark results for several implementations of an HTTP server which runs a long-term task. All tests were made on a laptop with Intel Core i7-5500U 2.40GHz processor having 2 cores, and 16Gb RAM. To run a test, execute ``python 1_sync.py`` (or any other Python file which starts with a number), and in a separate console execute the benchmark script with an appropriate hostname and port (see examples).

Prerequisites:

* all packages installed from ``requirements.txt``
* ``siege`` utility, which can be installed on Ubuntu with ``sudo apt install siege``

Benchmark results:

1. Synchronous HTTP server (``1_sync.py``)::

    $ ./run_benchmark.sh 127.0.0.1:8000
    ** SIEGE 4.0.2
    ** Preparing 25 concurrent users for battle.
    The server is now under siege...[error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer
    [error] socket: read error Connection reset by peer sock.c:539: Connection reset by peer

    Lifting the server siege...
    Transactions:                 21 hits
    Availability:              80.77 %
    Elapsed time:              59.76 secs
    Data transferred:           0.00 MB
    Response time:             16.82 secs
    Transaction rate:           0.35 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:                5.91
    Successful transactions:      21
    Failed transactions:           5
    Longest transaction:       19.63
    Shortest transaction:       2.81

2. Asynchronous Tornado server, the background task runs in the same thread as the I/O loop (``2_async.py``)::

    $ ./run_benchmark.sh 127.0.0.1:8001
    ** SIEGE 4.0.2
    ** Preparing 25 concurrent users for battle.
    The server is now under siege...
    Lifting the server siege...
    Transactions:                209 hits
    Availability:             100.00 %
    Elapsed time:              59.15 secs
    Data transferred:           0.00 MB
    Response time:              5.13 secs
    Transaction rate:           3.53 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               18.11
    Successful transactions:     209
    Failed transactions:           0
    Longest transaction:        5.38
    Shortest transaction:       0.28

3. An approach using ``threading`` module, asynchronous Tornado server, the background task runs in a different thread taken from ``ThreadExecutor`` (``3_async_threadexecutor.py``)::

    $ ./run_benchmark.sh 127.0.0.1:8002
    ** SIEGE 4.0.2
    ** Preparing 25 concurrent users for battle.
    The server is now under siege...
    Lifting the server siege...
    Transactions:                840 hits
    Availability:             100.00 %
    Elapsed time:              59.10 secs
    Data transferred:           0.00 MB
    Response time:              1.73 secs
    Transaction rate:          14.21 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               24.62
    Successful transactions:     840
    Failed transactions:           0
    Longest transaction:        1.97
    Shortest transaction:       0.28

4. An approach using ``multiprocessing`` module, asynchronous Tornado server, the background task runs in a different process taken from ``ProcessExecutor`` (``4_async_processexecutor.py``)::

    $ ./run_benchmark.sh 127.0.0.1:8003
    ** SIEGE 4.0.2
    ** Preparing 25 concurrent users for battle.
    The server is now under siege...
    Lifting the server siege...
    Transactions:              35470 hits
    Availability:             100.00 %
    Elapsed time:              59.95 secs
    Data transferred:           0.00 MB
    Response time:              0.04 secs
    Transaction rate:         591.66 trans/sec
    Throughput:                 0.00 MB/sec
    Concurrency:               24.95
    Successful transactions:   35470
    Failed transactions:           0
    Longest transaction:        0.72
    Shortest transaction:       0.00

A short conclusion is that ``multiprocessing`` approach shows the best results,
but more thorough testing may show more hidden details.
