import os
import time
import threading
import json
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
activation_name = "alexa"
is_listening = False
speech_config = None
speech_recognizer = None
personification_data = []  # Lista para almacenar los pares elemento-esencia

def initialize_speech_config():
    global speech_config
    speech_key = os.getenv('SPEECH_KEY')
    speech_region = os.getenv('SPEECH_REGION')
    
    logger.info(f"Inicializando configuración de voz con región: {speech_region}")
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = "es-ES"
    return speech_config

def text_to_speech(text):
    logger.info(f"Enviando texto para síntesis en el frontend: {text}")
    socketio.emit('response', {'text': text})

def process_command(command):
    logger.info(f"Procesando comando: {command}")
    command = command.lower().strip()
    
    # Primero buscar en los datos de personificación
    for pair in personification_data:
        elemento = pair.get('elemento', '').lower()
        if elemento and elemento in command:
            esencia = pair.get('esencia', '')
            if esencia:
                return esencia

    # Si no se encuentra en personificación, usar respuestas predeterminadas
    if "qué hora es" in command:
        return time.strftime("Son las %H:%M")
    elif "cómo estás" in command:
        return "Estoy bien, gracias por preguntar"
    elif "adiós" in command:
        return "¡Hasta luego!"
    else:
        return "Lo siento, no entiendo ese comando"

def check_activation_name(text):
    """Verifica si el texto contiene el nombre de activación y extrae el comando."""
    text = text.lower().strip()
    global activation_name
    
    # Verificar diferentes formatos del nombre de activación
    possible_formats = [
        f"{activation_name},",  # Con coma
        f"{activation_name} ",  # Con espacio
        f"¿{activation_name}",  # Con signo de interrogación
        f"¡{activation_name}"   # Con signo de exclamación
    ]
    
    for format in possible_formats:
        if format in text:
            # Eliminar el formato encontrado y cualquier espacio extra
            command = text.replace(format, "").strip()
            logger.info(f"Nombre de activación '{activation_name}' detectado, comando extraído: '{command}'")
            return True, command
            
    logger.info(f"Nombre de activación '{activation_name}' no detectado en: '{text}'")
    return False, text

def voice_recognition_thread():
    global is_listening, speech_recognizer
    
    logger.info("Iniciando thread de reconocimiento de voz")
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    while True:
        if is_listening:
            try:
                logger.info("Escuchando entrada de voz...")
                result = speech_recognizer.recognize_once_async().get()
                
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    text = result.text.lower()
                    logger.info(f"Texto reconocido: {text}")
                    socketio.emit('transcription', {'text': text})
                    
                    # Usar la nueva función de verificación
                    is_activated, command = check_activation_name(text)
                    if is_activated:
                        response = process_command(command)
                        text_to_speech(response)
                
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    logger.warning(f"No se detectó voz: {result.no_match_details}")
                    
            except Exception as e:
                logger.error(f"Error en reconocimiento de voz: {str(e)}")
                continue
        else:
            time.sleep(0.1)

@app.route('/')
def index():
    logger.info("Página principal solicitada")
    return render_template('index.html', activation_name=activation_name)

@app.route('/update_name', methods=['POST'])
def update_name():
    global activation_name
    data = request.get_json()
    new_name = data.get('name', 'alexa').lower().strip()
    
    if new_name:
        activation_name = new_name
        logger.info(f"Nombre de activación actualizado a: {activation_name}")
        return jsonify({'status': 'success', 'name': activation_name})
    else:
        logger.warning("Intento de actualizar con nombre vacío")
        return jsonify({'status': 'error', 'message': 'El nombre no puede estar vacío'}), 400

@app.route('/update_personification', methods=['POST'])
def update_personification():
    global personification_data
    data = request.get_json()
    personification_data = data.get('personifications', [])
    logger.info(f"Datos de personificación actualizados: {personification_data}")
    return jsonify({'status': 'success'})

@socketio.on('toggle_listening')
def handle_toggle_listening(data):
    global is_listening
    is_listening = data['isListening']
    logger.info(f"Estado de escucha cambiado a: {is_listening}")
    socketio.emit('listening_status', {'isListening': is_listening})

@socketio.on('voice_changed')
def handle_voice_change(data):
    voice = data.get('voice', 'female')
    logger.info(f"Voz cambiada a: {voice}")

@socketio.on('connect')
def handle_connect():
    logger.info("Cliente conectado")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Cliente desconectado")

if __name__ == '__main__':
    logger.info("Iniciando aplicación...")
    initialize_speech_config()
    
    # Start voice recognition thread
    recognition_thread = threading.Thread(target=voice_recognition_thread)
    recognition_thread.daemon = True
    recognition_thread.start()
    
    # Run Flask app
    logger.info("Iniciando servidor web en http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 