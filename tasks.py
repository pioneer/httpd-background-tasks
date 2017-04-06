import os
import time
import tempfile
from tornado import gen
from tornado.concurrent import return_future
from tornado.httpclient import AsyncHTTPClient
import requests
import feedparser


class User(object):

    def save(self):
        time.sleep(0.02)

    def send_email(self):
        time.sleep(0.06)

    def social_api(self):
        time.sleep(0.2)


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
    res = requests.get("http://localhost/")
    return res.content


def network_async_local():
    client = AsyncHTTPClient()
    return client.fetch("http://localhost/")


def network_sync_google():
    res = requests.get("http://google.com/")
    return res.content


def network_async_google():
    client = AsyncHTTPClient()
    return client.fetch("http://google.com/")


def network_https_sync():
    res = requests.get("https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&output=rss")
    return res.content


def network_https_async(res=None):
    client = AsyncHTTPClient()
    return client.fetch("https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&output=rss")


def network_https_cpu_bound_sync():
    res = requests.get("https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&output=rss")
    for i in xrange(20):
        data = feedparser.parse(res.content)
    return data


@return_future
def network_https_cpu_bound_async(callback=None):
    res = requests.get("https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&output=rss")
    for i in xrange(20):
        data = feedparser.parse(res.content)
    callback()


@return_future
def cpu_bound_async(res, callback=None):
    for i in xrange(20):
        data = feedparser.parse(res.body)
    callback()


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


def get_task(name):
    return globals()[name]


GROUPS = {"sleep_async_split":
            ["sleep_async_split_1",
             "sleep_async_split_2",
             "sleep_async_split_3"],
          "network_https_cpu_bound_async_split":
            ["network_https_async",
             "cpu_bound_async"]}

def get_group_tasks(group):
    return [get_task(name) for name in GROUPS[group]]
