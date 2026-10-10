"""Optional loopback-only web interface; stdlib, no external assets or telemetry."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from planner import ROOT, FEATURES, load_model, recommend
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/':
            body = (ROOT / 'index.html').read_bytes(); kind = 'text/html; charset=utf-8'; code = 200
        elif url.path == '/api/plan':
            q = parse_qs(url.query)
            try:
                result = recommend(load_model(), {f:q.get(f, [''])[0] for f in FEATURES}, q.get('unsafe', ['false'])[0] == 'true', q.get('stationary', ['false'])[0] == 'true')
                body = json.dumps(result).encode(); code = 200
            except (ValueError, KeyError) as e:
                body = json.dumps({'error':str(e)}).encode(); code = 400
            kind = 'application/json'
        else: body = b'Not found'; kind = 'text/plain'; code = 404
        self.send_response(code); self.send_header('Content-Type', kind); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
    def log_message(self, *_): pass
if __name__ == '__main__':
    print('Touch Grass Planner: http://127.0.0.1:8765 (Ctrl+C stops)')
    try: HTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
    except KeyboardInterrupt: pass
