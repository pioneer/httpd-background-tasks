import time
from concurrent.futures import ProcessPoolExecutor
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado import gen


TEMPLATE = "<html><head><title>Test</title></head><body><p>Test</p></body></html>"
MAX_WORKERS = 4


class User(object):

    def save(self):
        time.sleep(0.02)

    def send_email(self):
        time.sleep(0.06)

    def social_api(self):
        time.sleep(0.2)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", UserHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


def background_task():
    user = User()
    user.save()
    user.send_email()
    user.social_api()


class UserHandler(tornado.web.RequestHandler):

    executor = ProcessPoolExecutor(max_workers=MAX_WORKERS)

    @gen.coroutine
    def get(self):
        res = yield self.executor.submit(background_task)
        self.write(TEMPLATE)
        self.finish()


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    PORT = 8003
    print "serving at port", PORT
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
