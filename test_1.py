import sys
import SimpleHTTPServer
import SocketServer
import settings
import tasks

try:
    task_name = sys.argv[1]
except IndexError:
    task_name = "sleep_sync"
task = tasks.get_task(task_name)


class SyncServer(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self, *args, **kwargs):
        task()
        self.send_response(200, message=settings.TEMPLATE)
        self.end_headers()


def run():
    Handler = SyncServer
    httpd = SocketServer.TCPServer(("", settings.PORT), Handler)
    print "serving at port", settings.PORT
    httpd.serve_forever()


if __name__ == '__main__':
    run()
