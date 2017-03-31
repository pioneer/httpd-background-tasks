import time
import datetime
from tornado.concurrent import return_future
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado import gen


TEMPLATE = "<html><head><title>Test</title></head><body><p>Test</p></body></html>"


class AsyncUser(object):

    @return_future
    def save(self, callback=None):
        time.sleep(0.02)
        result = datetime.datetime.utcnow()
        callback(result)

    @return_future
    def send_email(self, callback=None):
        time.sleep(0.06)
        result = datetime.datetime.utcnow()
        callback(result)

    @return_future
    def social_api(self, callback=None):
        time.sleep(0.2)
        result = datetime.datetime.utcnow()
        callback(result)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", UserHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


class UserHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        user = AsyncUser()
        response = yield (user.save())
        response2 = yield (user.send_email())
        response3 = yield (user.social_api())
        self.write(TEMPLATE)
        self.finish()


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    PORT = 8001
    print "serving at port", PORT
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
