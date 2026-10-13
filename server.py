import http.server
import socketserver
import webbrowser
import threading
import os
import subprocess
import urllib.parse

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')

# file types we block or scan before serving
DANGEROUS_EXTS = {
    '.exe', '.msi', '.sh', '.bat', '.dll', '.bin', '.deb', '.rpm', '.apk', '.dmg', '.pkg'
}

class SafeHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # keep server quiet
        pass

    def send_text(self, code, text):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(text.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def is_dangerous(self, path):
        _, ext = os.path.splitext(path.lower())
        return ext in DANGEROUS_EXTS

    def scan_file(self, filepath):
        # run clamscan to check file. returns (status, message)
        # status: 'clean', 'infected', 'error', 'noscanner'
        try:
            proc = subprocess.run(['clamscan', '--no-summary', '--infected', filepath],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            return ('noscanner', 'ClamAV (clamscan) not found on this host. Install clamav to enable auto-scanning.')

        if proc.returncode == 0:
            return ('clean', 'File is clean')
        elif proc.returncode == 1:
            # infected
            return ('infected', proc.stdout or proc.stderr or 'File flagged as infected')
        else:
            return ('error', proc.stderr or proc.stdout or 'Scanner error')

    def do_GET(self):
        # parse path and map to filesystem
        parsed = urllib.parse.urlparse(self.path)
        safe_path = parsed.path

        # don't allow paths that try to go up
        if '..' in safe_path:
            self.send_text(400, 'Bad request')
            return

        fs_path = os.path.join(WEB_DIR, safe_path.lstrip('/'))

        # if path is directory, let base handler handle index
        if os.path.isdir(fs_path):
            return super().do_GET()

        # if file exists and is dangerous, scan it first
        if os.path.isfile(fs_path) and self.is_dangerous(fs_path):
            status, msg = self.scan_file(fs_path)
            if status == 'noscanner':
                self.send_text(503, 'Scanner not installed. Please install ClamAV (clamscan) to enable safe downloads.')
                return
            if status == 'infected':
                self.send_text(403, 'Download blocked: file appears infected.')
                return
            if status == 'error':
                self.send_text(500, 'Scanner error: cannot serve file.')
                return
            # if clean, fall through and serve file

        # for all other cases, use default serving
        return super().do_GET()


def run_server():
    os.chdir(WEB_DIR)
    handler = SafeHandler
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"Jezker server running at http://127.0.0.1:{PORT}/")
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
