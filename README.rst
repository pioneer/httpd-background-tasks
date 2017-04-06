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

Full results can be found in ``results.txt`` file, with summary section at the end of file.

A short conclusion is that ``multiprocessing`` approach shows more or less similar results comparing
to ``threading`` approach, outperforming in some cases, while underperforming in another cases. It seems
very likely, according to the original assumption and the results above, that network and I/O operations
indeed run outside GIL, so using processes instead of threads doesn't help a lot.

**Update:** It seems that single-threaded async approach shows very competitive results, especially
when properly split into smaller tasks, giving back control to the event loop after spawning each task.
