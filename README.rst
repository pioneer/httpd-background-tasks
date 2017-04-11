Benchmarks of running a long-term process within an HTTP server
===============================================================

Inspired by, and code is taken partly from these links:

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
* ``network_sync_local`` -- fetches a content from localhost and returns it (local Apache serves the URL)
* ``network_async_local`` -- the same as the above, but asynchronous
* ``network_sync_external`` -- fetches a content from a controlled external server and returns it
* ``network_async_external`` -- the same as the above, but asynchronous
* ``network_async_dns_external`` -- the same as the above, but uses FQDN instead of accessing by IP
* ``network_async_external_retry`` -- the same as ``network_async_external``, but with async retry and randomly generated HTTP 500 error in 50% cases
* ``network_async_dns_external_retry`` -- the same as the above, but uses FQDN instead of accessing by IP
* ``network_https_sync`` -- fetches a content from an https:// URL (here we try to measure the HTTPS parsing overhead)
* ``network_https_async`` -- the same as the above, but asynchronous
* ``network_https_async_retry`` -- the same as the above, but with async retry and randomly generated HTTP 500 error in 50% cases
* ``network_https_dns_async_retry`` -- the same as the above, but uses FQDN instead of accessing by IP
* ``network_https_cpu_bound_sync`` -- fetches a content from an https:// URL, then parses the XML taken from it (here we try to measure a CPU-heavy task)
* ``network_https_cpu_bound_async`` -- the same as the above, but asynchronous
* ``file_sync`` -- reads a file from the filesystem, writes it to a temporary file and returns its content
* ``file_async`` -- the same as the above, but asynchronous

Prerequisites:

* all packages installed from ``requirements.txt``
* ``siege`` utility, which can be installed on Ubuntu with ``sudo apt install siege``

Benchmark results:
------------------

Full results can be found in ``results.txt`` file.

=================================================  ==============  ===============  ==================  =========================
Task                                               Availability    Response time    Transaction rate    Memory peak consumption
-------------------------------------------------  --------------  ---------------  ------------------  -------------------------
fab run_server:1                                   94.58 %         1.96 secs        3.55 trans/sec      75.63 MB
fab run_server:2                                   100.00 %        6.98 secs        3.54 trans/sec      82.66 MB
fab run_server:2_group                             100.00 %        0.28 secs        88.18 trans/sec     81.03 MB
fab run_server:3                                   100.00 %        1.75 secs        14.24 trans/sec     430.34 MB
fab run_server:4                                   100.00 %        1.75 secs        14.24 trans/sec     1484.08 MB
fab run_server:2,network_async_local               100.00 %        0.04 secs        575.20 trans/sec    81.77 MB
fab run_server:3,network_sync_local                100.00 %        0.08 secs        300.91 trans/sec    430.61 MB
fab run_server:4,network_sync_local                96.21 %         0.05 secs        504.18 trans/sec    1494.32 MB
fab run_server:2,network_async_external            100.00 %        0.66 secs        37.99 trans/sec     81.37 MB
fab run_server:2,network_async_dns_external        100.00 %        0.95 secs        26.39 trans/sec     92.05 MB
fab run_server:2,network_async_external_retry      100.00 %        1.15 secs        21.61 trans/sec     84.77 MB
fab run_server:2,network_async_dns_external_retry  100.00 %        1.79 secs        13.88 trans/sec     95.46 MB
fab run_server:3,network_sync_external             100.00 %        1.38 secs        18.06 trans/sec     430.60 MB
fab run_server:4,network_sync_external             100.00 %        1.44 secs        17.30 trans/sec     1483.54 MB
fab run_server:2,network_https_async               100.00 %        1.10 secs        22.68 trans/sec     81.87 MB
fab run_server:2,network_https_dns_async           100.00 %        1.23 secs        20.05 trans/sec     92.87 MB
fab run_server:2,network_https_async_retry         100.00 %        1.38 secs        18.08 trans/sec     85.30 MB
fab run_server:2,network_https_dns_async_retry     100.00 %        2.06 secs        12.05 trans/sec     96.24 MB
fab run_server:3,network_https_sync                100.00 %        2.57 secs        9.67 trans/sec      430.73 MB
fab run_server:4,network_https_sync                100.00 %        2.73 secs        9.10 trans/sec      1482.75 MB
fab run_server:2,network_https_cpu_bound_async     97.65 %         28.60 secs       0.83 trans/sec      85.35 MB
fab run_server:3,network_https_cpu_bound_sync      100.00 %        35.49 secs       0.66 trans/sec      430.72 MB
fab run_server:4,network_https_cpu_bound_sync      100.00 %        15.79 secs       1.54 trans/sec      1793.73 MB
fab run_server:2,file_async                        100.00 %        0.93 secs        26.96 trans/sec     82.66 MB
fab run_server:3,file_sync                         100.00 %        0.54 secs        46.29 trans/sec     430.47 MB
fab run_server:4,file_sync                         100.00 %        0.53 secs        46.86 trans/sec     1486.58 MB
=================================================  ==============  ===============  ==================  =========================

Observations:
-------------

**Multiprocessing** approach, using ``ProcessExecutor`` (``fab run_server:4``, test server #4) shows good results in most cases, especially
in CPU-heavy and filesystem I/O-heavy tasks. Memory consumption is the maximum comparing to other approaches. The code is the most complicated,
due to the fact that Tornado's ``run_on_executor`` doesn't play well with processes. In rare cases this approach shows
non-100% availability, this is under investigation.

**Threading** approach, using ``ThreadExecutor`` (``fab run_server:3``, test server #3) shows slightly slower performance than **multiprocessing**,
but the code is simpler to write and maintain. Memory consumption is better than with **multiprocessing**, but significantly worse
than in **single-threaded async**.

**Single-threaded async** approach (``fab run_server:2`` and ``fab run_server:2_group``, test server #2), surprisingly,
outperforms any other approach in most tests, except
CPU-heavy and filesystem I/O-heavy ones. It seems very likely that network and I/O operations indeed run
outside GIL, so, therefore, using threads or processes doesn't help a lot in those cases. In fact,
saving time by not starting a thread or a process adds a value to the performance, according to the
results above. The best benefit can be achieved when a task is properly prepared for using within an
event loop, by yielding the control back to the loop after each small operation that can be done
asynchronously (see ``fab run_server:2_group`` as an example). The code looks very natural, as it's the recommended way
to write asynchronous code for Tornado. Memory consumption is the least of all, probably except **synchronous** approach,
which is anyway slow. In rare cases this approach shows non-100% availability, this is under investigation.

**Synchronous** approach is slower than any other, so it's here just for testing purposes.

Summary
-------

**Single-threaded async** approach shows very competitive results, so it can be used by default in most cases. Threads or processes can be
considered only for CPU-consuming tasks in high-loaded systems.
