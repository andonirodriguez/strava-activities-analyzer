import json
import time
import requests
import threading
import webbrowser
from flask import Flask, request
from config import STRAVA_CONFIG, DEFAULT_CONFIG, validate_config

class StravaAuth:
    def __init__(self):
        validate_config()
        self.tokens_file = 'strava_tokens.json'
        self.tokens = self._load_tokens()
        self.flask_app = None
        self.auth_code = None

    def _load_tokens(self):
        try:
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _save_tokens(self, tokens):
        with open(self.tokens_file, 'w') as f:
            json.dump(tokens, f)
        self.tokens = tokens

    def get_auth_url(self):
        params = {
            'client_id': STRAVA_CONFIG['client_id'],
            'redirect_uri': STRAVA_CONFIG['redirect_uri'],
            'response_type': 'code',
            'approval_prompt': 'force',
            'scope': STRAVA_CONFIG['scope']
        }
        return f"{DEFAULT_CONFIG['auth_url']}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    def exchange_code_for_token(self, code):
        response = requests.post(
            DEFAULT_CONFIG['token_url'],
            data={
                'client_id': STRAVA_CONFIG['client_id'],
                'client_secret': STRAVA_CONFIG['client_secret'],
                'code': code,
                'grant_type': 'authorization_code'
            }
        )
        if response.status_code == 200:
            self._save_tokens(response.json())
            return response.json()
        else:
            raise Exception(f"Error al intercambiar código: {response.text}")

    def refresh_token(self):
        if not self.tokens or 'refresh_token' not in self.tokens:
            raise Exception("No hay refresh token disponible")
        response = requests.post(
            DEFAULT_CONFIG['token_url'],
            data={
                'client_id': STRAVA_CONFIG['client_id'],
                'client_secret': STRAVA_CONFIG['client_secret'],
                'refresh_token': self.tokens['refresh_token'],
                'grant_type': 'refresh_token'
            }
        )
        if response.status_code == 200:
            self._save_tokens(response.json())
            return response.json()
        else:
            raise Exception(f"Error al refrescar token: {response.text}")

    def get_valid_token(self):
        if not self.tokens:
            self._automatic_oauth_flow()
        # Verificar si el token ha expirado o está por expirar (menos de 1 hora)
        if time.time() >= self.tokens.get('expires_at', 0) - 3600:
            return self.refresh_token()['access_token']
        return self.tokens['access_token']

    def _automatic_oauth_flow(self):
        print("No hay tokens válidos. Iniciando flujo de autenticación OAuth automático...")
        self._start_flask_server()
        auth_url = self.get_auth_url()
        print(f"Abriendo navegador en: {auth_url}")
        webbrowser.open(auth_url)
        self._wait_for_auth_code()
        if self.auth_code:
            self.exchange_code_for_token(self.auth_code)
        else:
            raise Exception("No se pudo obtener el código de autorización.")

    def _start_flask_server(self):
        self.flask_app = Flask(__name__)
        self.auth_code = None
        self._server_thread = threading.Thread(target=self._run_flask, daemon=True)
        self._server_thread.start()

        @self.flask_app.route('/callback')
        def callback():
            code = request.args.get('code')
            self.auth_code = code
            # Mensaje de éxito para el usuario
            return "<h2>Autenticación exitosa. Puedes cerrar esta ventana y volver al terminal.</h2>"

    def _run_flask(self):
        # Extraer el puerto del redirect_uri
        from urllib.parse import urlparse
        parsed = urlparse(STRAVA_CONFIG['redirect_uri'])
        port = parsed.port or 8000
        self.flask_app.run(port=port, debug=False, use_reloader=False)

    def _wait_for_auth_code(self):
        import time
        print("Esperando autorización del usuario...")
        for _ in range(300):  # Espera hasta 5 minutos
            if self.auth_code:
                break
            time.sleep(1)
        if not self.auth_code:
            raise Exception("Timeout esperando el código de autorización.") 