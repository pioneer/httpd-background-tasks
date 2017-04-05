Benchmarks of running a long-term process within an HTTP server
===============================================================

Inspired by, and code is taken partly from these linkes:

* http://www.maigfrga.ntweb.co/asynchronous-programming-tornado-framework/
* https://gist.github.com/methane/2185380

Below are performance benchmark results for several implementations of an HTTP server which runs a long-term task. All tests were made on a laptop with Intel Core i7-5500U 2.40GHz processor having 2 cores, and 16Gb RAM. To run a test, execute ``fab run_server:1`` (or use any other test number from 1 to 4), and in a separate console execute the benchmark ``fab run_load_test``. You may specify a background task name to be used with a test server, like ``fab run_server:3,network_sync``. Below is the full list of test servers and tasks.

Test servers
------------
1. Synchronous HTTP server
2. Asynchronous Tornado server, the background task runs in the same thread as the event loop (and a grouped variation which can run several tasks, releasing an event loop after each one)
3. Asynchronous Tornado server, an approach using ``threading`` module, the background task runs in a different thread taken from ``ThreadExecutor``
4. Asynchronous Tornado server, an approach using ``multiprocessing`` module, the background task runs in a different process taken from ``ProcessExecutor``

Background tasks
----------------
* *None specified* -- equals to ``sleep_sync`` (in most cases) -- a blocking task which basically just sleeps and returns some HTML (imitating a website user activity)
* ``sleep_async`` -- the same as above, but returns a future and can be embedded in a Tornado event loop
* ``sleep_async_split`` -- a group of tasks, where the sleeps from the above are split to smaller sleeps, which run separately
* ``network_sync_google`` -- fetches a content from google.com and returns it
* ``network_sync_local`` -- fetches a content from localhost and returns it (local Apache serves the URL)
* ``network_https_sync`` -- fetches a content from an https:// URL (here we try to measure the HTTPS parsing overhead)
* ``network_https_cpu_bound_sync`` fetches a content from an https:// URL, then parses the XML taken from it (here we try to measure a CPU-heavy task)
* ``file_sync`` -- reads a file from the filesystem, writes it to a temporary file and returns its content

Prerequisites:

* all packages installed from ``requirements.txt``
* ``siege`` utility, which can be installed on Ubuntu with ``sudo apt install siege``

Benchmark results:
------------------

==================================================  ============  ================  =============
\                                                   Availability  Transaction rate  Response time
--------------------------------------------------  ------------  ----------------  -------------
Sync                                                96.77 %       3.55 trans/sec    1.94 secs
Async                                               100.00 %      3.54 trans/sec    5.38 secs
Async, threading                                    100.00 %      14.20 trans/sec   1.73 secs
Async, multiprocessing                              100.00 %      14.22 trans/sec   1.73 secs
Async, threading, network, google.com               100.00 %      3.29 trans/sec    7.09 secs
Async, multiprocessing, network, google.com         100.00 %      3.16 trans/sec    7.42 secs
Async, threading, network, local Apache             100.00 %      164.64 trans/sec  0.15 secs
Async, multiprocessing, network, local Apache       100.00 %      274.92 trans/sec  0.09 secs
Async, threading, file                              100.00 %      647.20 trans/sec  0.04 secs
Async, multiprocessing, file                        100.00 %      569.03 trans/sec  0.04 secs
Async, threading, network, HTTPS                    100.00 %      4.60 trans/sec    5.31 secs
Async, multiprocessing, network, HTTPS              100.00 %      5.07 trans/sec    4.69 secs
Async, threading, network, HTTPS + CPU-bound        100.00 %      0.45 trans/sec    31.57 secs
Async, multiprocessing, network, HTTPS + CPU-bound  100.00 %      1.15 trans/sec    17.82 secs
==================================================  ============  ================  =============

**Note:** Full results can be found in ``results.txt`` file.

A short conclusion is that ``multiprocessing`` approach shows more or less similar results comparing
to ``threading`` approach, outperforming in some cases, while underperforming in another cases. It seems
very likely, according to the original assumption and the results above, that network and I/O operations
indeed run outside GIL, so using processes instead of threads doesn't help a lot.


