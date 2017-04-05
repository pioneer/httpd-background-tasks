import sys
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado import gen
import settings
import tasks


try:
    group_name = sys.argv[1]
except IndexError:
    group_name = "sleep_async_split"
group_tasks = tasks.get_group_tasks(group_name)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", UserHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


class UserHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        for task in group_tasks:
            res = yield task
        self.write(settings.TEMPLATE)
        self.finish()


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    print "serving at port", settings.PORT
    http_server.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()