#!/usr/bin/env python3
import http.server, json, subprocess, os, sys

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        print('收到指令:', body[:100], flush=True)
        try:
            data = json.loads(body)
            command = data.get('command', '')
            cmd = 'source /root/.nvm/nvm.sh && nvm use 20 && kr-gemini --print ' + repr(command)
            env = os.environ.copy()
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, timeout=120)
            response = {'code': 0, 'stdout': result.stdout[:500], 'stderr': result.stderr[:200]}
        except Exception as e:
            response = {'code': 1, 'error': str(e)}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())
    def log_message(self, format, *args):
        pass

server = http.server.HTTPServer(('', 8080), Handler)
print('CC服务就绪 8080', flush=True)
server.serve_forever()
