from flask import Flask, render_template, request, jsonify
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

app = Flask(__name__)

# Configuración de la cuenta de servicio
CREDENTIALS_PATH = "" # gen-lang-client-0725079642-3c817099c728.json
SCOPES = ["https://www.googleapis.com/auth/generative-language"]
API_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

# Obtener el token de acceso
def get_access_token():    
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES)
    credentials.refresh(Request())
    return credentials.token

# Función para enviar mensajes a la API
def enviar_mensaje(mensaje_usuario):
    token = get_access_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [
            {"parts": [{"text": mensaje_usuario}]}
        ]
    }
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        try:
            # Procesar la respuesta de la API
            obscenas_json = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            obscenas_json = obscenas_json.replace("```json", "").replace("```", "").strip()
            obscenas = eval(obscenas_json).get("obscenas", 0)
            return obscenas
        except (IndexError, KeyError, TypeError, SyntaxError):
            return 0
    else:
        return 0

@app.route('/analyze', methods=['POST'])
def analyze():
    user_message = request.json.get('message', '')
    instruction = ". Analiza si tiene palabras obscenas en una escala del 1 al 5 (enteros) y guárdalos en un json {'obscenas': valor}. No des explicaciones."
    complete_message = user_message + instruction

    obscenas = enviar_mensaje(complete_message)


    return jsonify({
        'user_message': user_message,
        'obscenas': obscenas
    })

if __name__ == '__main__':
    app.run(debug=True)
