from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Cargar variables de entorno
load_dotenv()

# Variable global para el nombre de activación
activation_name = "alexa"

@app.route('/')
def index():
    return render_template('index.html', activation_name=activation_name)

@app.route('/update_name', methods=['POST'])
def update_name():
    global activation_name
    data = request.get_json()
    activation_name = data.get('name', 'alexa').lower()
    return jsonify({'status': 'success', 'name': activation_name})

@app.route('/get_activation_name')
def get_activation_name():
    return jsonify({'name': activation_name})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 