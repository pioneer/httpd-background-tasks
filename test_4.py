import sys
from concurrent.futures import ProcessPoolExecutor
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


def background_task():
    task()


class UserHandler(tornado.web.RequestHandler):

    executor = ProcessPoolExecutor(max_workers=settings.MAX_WORKERS)

    @gen.coroutine
    def get(self):
        res = yield self.executor.submit(background_task)
        self.write(settings.TEMPLATE)
        self.finish()


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    print "serving at port", settings.PORT
    http_server.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
