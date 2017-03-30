import time
from datetime import datetime
import SimpleHTTPServer
import SocketServer


class User(object):
    def save(self):
        time.sleep(0.2)

    def send_email(self):
        time.sleep(0.6)

    def social_api(self):
        time.sleep(2)


class SyncServer(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self, *args, **kwargs):
        user = User()
        user.save()
        user.send_email()
        user.social_api()
        self.send_response(200, message='ok')
        self.end_headers()


def run():
    PORT = 8000
    Handler = SyncServer
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "serving at port", PORT
    httpd.serve_forever()


if __name__ == '__main__':
    run()
