from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import os

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            # 1. Leer los datos enviados por el index.html
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.enviar_json(400, {"error": "Petición vacía"})
                return

            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            prompt = body.get("prompt", "")
            tags = body.get("tags", "Mexican Regional, Corrido")

            # 2. Obtener la llave desde Vercel
            suno_api_key = os.environ.get("SUNO_API_KEY")
            if not suno_api_key:
                self.enviar_json(500, {"error": "Falta configurar la variable SUNO_API_KEY en Vercel"})
                return

            # ==========================================
            # CONFIGURACIÓN OFICIAL PARA SUNOAPI.ORG
            # ==========================================
            url_suno = "https://api.sunoapi.org/api/v1/generate" 
            
            headers = {
                "Authorization": f"Bearer {suno_api_key}",
                "Content-Type": "application/json"
            }
            
            # Estructura de parámetros requerida por la documentación de sunoapi
            payload = json.dumps({
                "customMode": True,
                "instrumental": False,
                "model": "V3_5",  # Puedes cambiar a "V4_0" o "V4_5ALL" si tu plan lo soporta
                "prompt": prompt,
                "style": tags,
                "title": "Hit Real JCV"
            }).encode('utf-8')
            # ==========================================

            # 3. Ejecutar la llamada HTTP nativa
            req = urllib.request.Request(url_suno, data=payload, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = response.read().decode('utf-8')
                suno_response_json = json.loads(res_data)
                
                # Devolvemos la respuesta directo a tu HTML
                self.enviar_json(200, suno_response_json)

        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            self.enviar_json(e.code, {"error": f"Error de SunoAPI ({e.code}): {error_msg}"})
        except Exception as e:
            self.enviar_json(500, {"error": f"Fallo interno en el backend Vercel: {str(e)}"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def enviar_json(self, status_code, datos):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(datos).encode('utf-8'))
