import time
from tornado.concurrent import return_future
import requests
import feedparser
import settings


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


def network_sync():
    res = requests.get("http://localhost")
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
