import os
import time
import random
import tempfile
import uuid
from tornado import gen
from tornado.concurrent import Future, return_future
from tornado.httpclient import AsyncHTTPClient, HTTPResponse
from tornado_retry_client import RetryClient
import requests
import feedparser
from checksum import SimpleHash, CheckSumString


class User(object):

    def save(self):
        time.sleep(0.02)

    def send_email(self):
        time.sleep(0.06)

    def social_api(self):
        time.sleep(0.2)


AsyncHTTPClient_cls = AsyncHTTPClient().__class__


class AsyncHTTPRandomErrorClient(AsyncHTTPClient_cls):

    def fetch(self, request, **kwargs):
        if random.random() >= 0.5:
            return super(AsyncHTTPRandomErrorClient, self).fetch(request, **kwargs)
        res = Future()
        res.set_result(HTTPResponse(None, 500, effective_url=request))
        return res


def sleep():
    user = User()
    user.save()
    user.send_email()
    user.social_api()


def sleep_sync():
    sleep()


@return_future
def sleep_async(callback=None):
    sleep()
    callback()


sleep_async_split_1 = lambda res: gen.sleep(0.02)
sleep_async_split_2 = lambda res: gen.sleep(0.06)
sleep_async_split_3 = lambda res: gen.sleep(0.2)


def network_sync_local():
    res = requests.get("http://127.0.0.1/template.html")
    return res.content


@gen.coroutine
def network_async_local():
    client = AsyncHTTPClient()
    res = yield client.fetch("http://127.0.0.1/template.html")
    raise gen.Return(res.body)


def network_sync_external():
    res = requests.get("http://52.58.36.186/template.html")
    return res.content


@gen.coroutine
def network_async_external():
    client = AsyncHTTPClient()
    res = yield client.fetch("http://52.58.36.186/template.html")
    raise gen.Return(res.body)


@gen.coroutine
def network_async_dns_external():
    client = AsyncHTTPClient()
    res = yield client.fetch("http://ec2-52-58-36-186.eu-central-1.compute.amazonaws.com/template.html")
    raise gen.Return(res.body)


@gen.coroutine
def network_async_external_retry():
    client = RetryClient(http_client=AsyncHTTPRandomErrorClient())
    res = yield client.fetch("http://52.58.36.186/template.html")
    raise gen.Return(res.body)


@gen.coroutine
def network_async_dns_external_retry():
    client = RetryClient(http_client=AsyncHTTPRandomErrorClient())
    res = yield client.fetch("http://ec2-52-58-36-186.eu-central-1.compute.amazonaws.com/template.html")
    raise gen.Return(res.body)


def network_https_sync():
    res = requests.get("https://52.58.36.186/template.html", verify=False)
    return res.content


@gen.coroutine
def network_https_async(res=None):
    client = AsyncHTTPClient()
    res = yield client.fetch("https://52.58.36.186/template.html", validate_cert=False)
    raise gen.Return(res.body)


@gen.coroutine
def network_https_dns_async(res=None):
    client = AsyncHTTPClient()
    res = yield client.fetch("https://ec2-52-58-36-186.eu-central-1.compute.amazonaws.com/template.html", validate_cert=False)
    raise gen.Return(res.body)


@gen.coroutine
def network_https_async_retry(res=None):
    client = RetryClient(http_client=AsyncHTTPRandomErrorClient())
    res = yield client.fetch("https://52.58.36.186/template.html", validate_cert=False)
    raise gen.Return(res.body)


@gen.coroutine
def network_https_dns_async_retry(res=None):
    client = RetryClient(http_client=AsyncHTTPRandomErrorClient())
    res = yield client.fetch("https://ec2-52-58-36-186.eu-central-1.compute.amazonaws.com/template.html", validate_cert=False)
    raise gen.Return(res.body)


def network_https_cpu_bound_sync():
    res = requests.get("https://52.58.36.186/news.xml", verify=False)
    for i in xrange(20):
        data = feedparser.parse(res.content)
    return data


@gen.coroutine
def network_https_cpu_bound_async():
    client = AsyncHTTPClient()
    res = yield client.fetch("http://52.58.36.186/news.xml", validate_cert=False)
    for i in xrange(20):
        data = feedparser.parse(res.body)
    raise gen.Return(data)


@gen.coroutine
def cpu_bound_async(res=None):
    for i in xrange(20):
        data = feedparser.parse(res.body)
    raise gen.Return(data)


def file():
    f = open("template.html")
    content = f.read()
    f.close()
    f = tempfile.TemporaryFile()
    f.write(content)
    f.flush()
    os.fsync(f.fileno())
    f.close()
    return content


def file_sync():
    return file()


@return_future
def file_async(callback=None):
    file()
    callback()


def simplehash():
    sh = SimpleHash()
    hash_a = sh.compute_hash("TEST_VALUE")
    enc_hash_a = sh.protect_hash(b'0' * 20)
    dec_hash = sh.unprotect_hash(enc_hash_a)
    return dec_hash


def simplehash_sync():
    return simplehash()


@gen.coroutine
def simplehash_async():
    raise gen.Return(simplehash())


def checksum():
    csum = CheckSumString()
    checksum = csum.get("TEST_VALUE")
    result = csum.verify("TEST_VALUE", checksum)
    return result


def checksum_sync():
    return checksum()


@gen.coroutine
def checksum_async():
    raise gen.Return(checksum())


def get_task(name):
    return globals()[name]


GROUPS = {"sleep_async_split":
            ["sleep_async_split_1",
             "sleep_async_split_2",
             "sleep_async_split_3"]}

def get_group_tasks(group):
    return [get_task(name) for name in GROUPS[group]]
