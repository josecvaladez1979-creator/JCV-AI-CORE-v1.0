from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            data = json.loads(body)
            
            prompt = data.get('prompt','Arrieros somos')
            style = data.get('style','Mexican Regional')
            
            # CHECA SI TIENE LA LLAVE
            api_key = os.environ.get('SUNO_API_KEY') or os.environ.get('SUNO_KEY')
            
            if not api_key:
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error":"Falta SUNO_API_KEY en Vercel > Settings > Environment Variables"}).encode())
                return

            # Aquí iría la llamada real a Suno
            # Por ahora regresamos prueba para ver si conecta
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            # Si llega aquí, la llave SI existe
            self.wfile.write(json.dumps({"audio_url": "", "error": "LLAVE OK pero falta conectar API Suno - dime que ves este mensaje"}).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Error motor: {str(e)}"}).encode())
