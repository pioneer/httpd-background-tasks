from fabric.api import local
import settings


def run_server(num, task_name=None):
    num = int(num)
    command = "python test_%d.py" % num
    if task_name:
        command += " %s" % task_name
    local(command)


def run_load_test():
    local("siege -b -t%dS 127.0.0.1:%d" % (settings.LOAD_TEST_TIME, settings.PORT))
