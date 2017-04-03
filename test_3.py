import sys
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado import gen
import settings
import tasks


try:
    task_name = sys.argv[1]
except IndexError:
    task_name = "sleep_sync"
task = tasks.get_task(task_name)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", UserHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


class UserHandler(tornado.web.RequestHandler):

    executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)

    @run_on_executor
    def background_task(self):
        task()

    @gen.coroutine
    def get(self):
        res = yield self.background_task()
        self.write(settings.TEMPLATE)
        self.finish()


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    print "serving at port", settings.PORT
    http_server.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
