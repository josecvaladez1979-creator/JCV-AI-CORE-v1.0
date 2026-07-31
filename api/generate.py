from http.server import BaseHTTPRequestHandler
import json, os, time
import requests

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            prompt = data.get('prompt') or data.get('lyrics') or data.get('text') or ''
            style = data.get('style', 'Pop')
            title = data.get('title', 'JCV Song')

            api_key = os.environ.get('SUNO_API_KEY')
            if not api_key:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Falta SUNO_API_KEY en Vercel"}).encode())
                return

            # Llamar a SunoAPI.org
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "prompt": prompt,
                "style": style,
                "title": title,
                "customMode": True,
                "instrumental": False,
                "model": "V4",
                "callStrict": False
            }
            
            r = requests.post("https://api.sunoapi.org/api/v1/generate", json=payload, headers=headers, timeout=30)
            result = r.json()

            # Responder directo a tu frontend
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
