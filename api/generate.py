from http.server import BaseHTTPRequestHandler
import json, os, time, requests

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('content-length',0))
            body = self.rfile.read(length).decode() if length else '{}'
            data = json.loads(body) if body else {}
            
            prompt = data.get('prompt') or 'Arrieros somos y en el camino andamos'
            style = data.get('style','Mexican Regional, Reggaeton')
            title = data.get('title','JCV Song')

            suno_key = os.environ.get('SUNO_API_KEY')
            
            # Si no hay key, responde error claro
            if not suno_key:
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.send_header('Access-Control-Allow-Origin','*')
                self.end_headers()
                self.wfile.write(json.dumps({"error":"No SUNO_API_KEY"}).encode())
                return

            # ENDPOINT REAL SUNO v2
            headers = {"Authorization": f"Bearer {suno_key}", "Content-Type":"application/json"}
            payload = {
                "prompt": f"{title} - {prompt}",
                "style": style,
                "title": title,
                "custom_mode": True,
                "instrumental": False,
                "model": "V3_5"
            }

            # 1. Crear cancion
            r = requests.post("https://api.suno.ai/v1/songs", json=payload, headers=headers, timeout=30)
            # Si falla el primer endpoint, intenta el segundo
            if r.status_code != 200:
                r = requests.post("https://api.sunoapi.com/api/v1/generate", json=payload, headers=headers, timeout=30)
            
            res = r.json()

            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "audio_url": None}).encode())
