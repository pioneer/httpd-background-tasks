import os
import psutil
import signal
import subprocess
import time
import tabulate
from fabric.api import local
import settings


LOAD_TEST_CMD = "siege -b -t%dS 127.0.0.1:%d" % (settings.LOAD_TEST_TIME, settings.PORT)


def run_server(name, task_name=None):
    command = "python test_%s.py" % name
    if task_name:
        command += " %s" % task_name
    local(command)


def run_load_test():
    local(LOAD_TEST_CMD)


def run_all_load_tests():

    def parse_siege_output(output):
        availability = response_time = transaction_rate = None
        for line in output.splitlines():
            if line.startswith("Availability"):
                availability = " ".join(line.split()[1:])
            if line.startswith("Response time"):
                response_time = " ".join(line.split()[2:])
            if line.startswith("Transaction rate"):
                transaction_rate = " ".join(line.split()[2:])
        return availability, response_time, transaction_rate

    TESTS = [
             "1",
             "2",
             "2_group",
             "3",
             "4",
            ("2", "network_async_local"),
            ("3", "network_sync_local"),
            ("4", "network_sync_local"),
            ("2", "network_async_external"),
            ("3", "network_sync_external"),
            ("4", "network_sync_external"),
            ("2", "network_https_async"),
            ("3", "network_https_sync"),
            ("4", "network_https_sync"),
            ("2", "network_https_cpu_bound_async"),
            ("3", "network_https_cpu_bound_sync"),
            ("4", "network_https_cpu_bound_sync"),
            ("2", "file_async"),
            ("3", "file_sync"),
            ("4", "file_sync")
           ]
    SUMMARY = []
    for test in TESTS:
        if isinstance(test, tuple):
            command = "python test_%s.py %s" % test
            fab_command = "fab run_server:%s,%s" % test
        else:
            command = "python test_%s.py" % test
            fab_command = "fab run_server:%s" % test
        print fab_command
        p = subprocess.Popen(command.split())
        pid = p.pid
        time.sleep(1)  # Waiting for the server to start properly
        out = local(LOAD_TEST_CMD, capture=True)
        print out.stderr
        availability, response_time, transaction_rate = parse_siege_output(out.stderr)
        summary = [fab_command,
                   availability,
                   response_time,
                   transaction_rate]
        SUMMARY.append(summary)
        print "\n"
        try:
            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            for child in children:
                os.kill(child.pid, signal.SIGTERM)
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            print e
        time.sleep(2)  # Waiting for the server to terminate
    print tabulate.tabulate(SUMMARY, headers=["Task", "Availability", "Response time", "Transaction rate"])
