# simple http server for Jezker
# run with: python3 server.py

import http.server
import socketserver
import webbrowser
import threading
import os

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def run_server():
    os.chdir(WEB_DIR)
    handler = SilentHandler
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"Jezker server serving http://127.0.0.1:{PORT}/")
        httpd.serve_forever()

if __name__ == '__main__':
    if not os.path.isdir(WEB_DIR):
        print("web/ folder not found. Make sure web/index.html exists.")
        raise SystemExit(1)

    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    # open default browser to the page
    webbrowser.open(f"http://127.0.0.1:{PORT}/")

    try:
        t.join()
    except KeyboardInterrupt:
        print('\nserver stopped')
