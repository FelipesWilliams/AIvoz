# Asistente de Voz con Azure Speech Services

Este proyecto implementa un asistente de voz similar a Alexa utilizando Azure Cognitive Services Speech API.

## Requisitos

- Python 3.7 o superior
- Micrófono funcional
- Credenciales de Azure Speech Services

## Configuración

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
SPEECH_KEY=tu_speech_key
SPEECH_REGION=tu_region
SPEECH_ENDPOINT=tu_endpoint
```

## Uso

1. Ejecuta el asistente:
```bash
python voice_assistant.py
```

2. El asistente comenzará a escuchar. Di "Alexa" seguido de tu comando.

## Comandos disponibles

- "Alexa, qué hora es"
- "Alexa, cómo estás"
- "Alexa, adiós"

## Notas

- El asistente está configurado para reconocer español (es-ES)
- Asegúrate de tener un micrófono conectado y funcionando correctamente
- Habla claramente y cerca del micrófono para mejor reconocimiento # AIvoz
# AIvoz
