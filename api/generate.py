from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import os

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            # 1. Leer los datos JSON que envía el index.html
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.enviar_json(400, {"error": "Petición vacía"})
                return

            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            prompt = body.get("prompt", "")
            tags = body.get("tags", "Mexican Regional, Corrido")

            # 2. Leer la API KEY desde las Variables de Entorno de Vercel
            suno_api_key = os.environ.get("SUNO_API_KEY")

            if not suno_api_key:
                # Si la llave no está en Vercel, arrojará este error claro
                self.enviar_json(500, {"error": "Backend OK pero falta configurar la variable SUNO_API_KEY en Vercel"})
                return

            # 3. Configurar la petición real hacia los servidores de Suno
            # Nota: Cambia esta URL si usas un Proxy/Gateway específico de Suno (ej: http://localhost:3000/api/generate)
            url_suno = "https://suno.ai" 
            
            headers = {
                "Authorization": f"Bearer {suno_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = json.dumps({
                "prompt": prompt,
                "tags": tags,
                "make_instrumental": False,
                "wait_audio": True
            }).encode('utf-8')

            # 4. Hacer la llamada HTTP tradicional (Python Vanilla)
            req = urllib.request.Request(url_suno, data=payload, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = response.read().decode('utf-8')
                suno_response_json = json.loads(res_data)
                
                # Devolver la respuesta de Suno directa a tu HTML
                self.enviar_json(200, suno_response_json)

        except urllib.error.HTTPError as e:
            # Captura si los servidores de Suno rechazan la petición (Ej: Token inválido)
            error_msg = e.read().decode('utf-8')
            self.enviar_json(e.code, {"error": f"Falta conectar API Suno de forma correcta: {error_msg}"})
        except Exception as e:
            # Captura fallas de lógica generales
            self.enviar_json(500, {"error": f"Fallo interno en el backend: {str(e)}"})

    def do_OPTIONS(self):
        # Permite peticiones CORS de prueba
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
