import time
from tornado.concurrent import return_future
from datetime import timedelta
import requests
import feedparser
import tornado.ioloop


class User(object):

    def save(self):
        time.sleep(0.02)

    def send_email(self):
        time.sleep(0.06)

    def social_api(self):
        time.sleep(0.2)

class AsyncUser(object):

    def __init__(self, callback):
        self.callback = callback

    def save(self):
        tornado.ioloop.IOLoop.add_timeout(tornado.ioloop.IOLoop.instance(), timedelta(milliseconds=20), self.send_email)

    def send_email(self):
        tornado.ioloop.IOLoop.add_timeout(tornado.ioloop.IOLoop.instance(), timedelta(milliseconds=60), self.social_api)

    def social_api(self):
        tornado.ioloop.IOLoop.add_timeout(tornado.ioloop.IOLoop.instance(), timedelta(milliseconds=200), self.callback)


def sleep():
    user = User()
    user.save()
    user.send_email()
    user.social_api()


def sleep_non_blocking(calback):
    user = AsyncUser(calback)
    user.save()


def sleep_sync():
    sleep()


@return_future
def sleep_non_blocking_async(callback=None):
    sleep_non_blocking(callback)


@return_future
def sleep_async(callback=None):
    sleep()
    callback()


def network_sync():
    res = requests.get("http://localhost/")
    return res.content


def network_https_sync():
    res = requests.get("https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&output=rss")
    return res.content


def network_https_cpu_bound_sync():
    res = requests.get("https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&output=rss")
    for i in xrange(20):
        data = feedparser.parse(res.content)
    return data


def file_sync():
    f = open("template.html")
    content = f.read()
    f.close()
    return content


def get_task(name):
    return globals()[name]
