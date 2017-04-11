import sys
import SimpleHTTPServer
import SocketServer
import settings
import tasks
import memory_utils

try:
    task_name = sys.argv[1]
except IndexError:
    task_name = "sleep_sync"
task = tasks.get_task(task_name)


class SyncServer(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self, *args, **kwargs):
        if self.path == "/":
            task()
            content = settings.TEMPLATE
        else:
            content = memory_utils.get_memory_string()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(content)
        return


def run():
    Handler = SyncServer
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(("", settings.PORT), Handler)
    print "serving at port", settings.PORT
    httpd.serve_forever()


if __name__ == '__main__':
    run()
