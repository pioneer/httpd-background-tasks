import os
import resource
import psutil


def get_children_pids():
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    return [child.pid for child in children]

_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}

def _VmB(VmKey, pid=None):
    '''Private.
    '''
    global _scale
    if not pid:
        pid = os.getpid()
    _proc_status = '/proc/%d/status' % pid
     # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
     # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
     # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(pid=None, since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(pid=None, since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since


def peak(pid=None, since=0.0):
    '''Return peak memory usage in bytes.
    '''
    return _VmB('VmPeak:') - since


def get_with_children(fn):
    memory_usage = fn()
    children_pids = get_children_pids()
    for pid in children_pids:
        memory_usage += fn(pid=pid)
    return memory_usage


def max_rss():
    memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss + \
                   resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return memory_usage*1024.0


def get_memory_string():
    memory = get_with_children(peak) / 1024.0 / 1024.0
    return "%7.2f MB" % memory
