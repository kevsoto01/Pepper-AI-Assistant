from pathlib import Path
import socket

ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = ROOT_DIR / "app"

# Config
CONFIG_PATH = ROOT_DIR / "config" / "config.json"

# Models
MODELS_DIR = ROOT_DIR / "models"

# Piper
PIPER_DIR = MODELS_DIR / "piper"
PIPER_MODEL_DIR = {
    "Default": PIPER_DIR / "english" / "en_US-hfc_female-medium.onnx",
    "English": PIPER_DIR / "english" / "en_US-hfc_female-medium.onnx",
    "Spanish": PIPER_DIR / "spanish" / "es_MX-claude-high.onnx",
    # "Chinese": PIPER_DIR / "chinese" / "zh_CN-huayan-medium.onnx"
    }

# LLM
OLLAMA_DIR = MODELS_DIR / "ollama"
OLLAMA_MODELS = {
    "7b4q": "qwen2.5:7b-instruct-q4_K_M",
    "3b": "qwen2.5:3b",
    "3b4q": "qwen2.5:3b-instruct-q4_K_M",
    "2b4q": "gemma:2b-instruct-q4_K_M",
    "1.5b4q": "qwen2.5:1.5b-instruct-q4_K_M", 
    "1.5b": "qwen2.5:1.5b",    
    }
OLLAMA_URL = "http://127.0.0.1:11434/api/tags"

# Speech Recognition
WHISPER_DIR = MODELS_DIR / "whisper"

# Audio
TEMP_AUDIO_DIR = ROOT_DIR / "temp"
LOCAL_USER_AUDIO = TEMP_AUDIO_DIR / r"user_input.wav"
LOCAL_PEPPER_AUDIO = TEMP_AUDIO_DIR / r"piper_output.wav"
REMOTE_PEPPER_AUDIO = r"/home/nao/recordings/piper_output.wav"

# UI
WEB_DIR = APP_DIR / "web"

UI_TEMPLATE_PATH = WEB_DIR / "index_template.html"
UI_TEMPLATE_BACKGROUND_PATH = WEB_DIR / "index_template_background.html"
UI_HTML_PATH = WEB_DIR / "index.html"
UI_STATE_JSON_PATH = WEB_DIR / "state.json"

def get_own_ipv4() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

ip_address = get_own_ipv4()
print("IPv4 address:", ip_address)

UI_HOST = ip_address
UI_PORT = 8000
UI_URL = "http://"+ip_address+":"+str(UI_PORT)+"/index.html"

# PEPPER
PEPPER_ANIMATION_PATHS = {
    # Greetings / attention
    "hello": "animations/Stand/Gestures/Hey_1",
    "wave": "animations/Stand/Gestures/Hey_1",
    "hey": "animations/Stand/Gestures/Hey_1",

    # Agreement / disagreement
    "yes": "animations/Stand/Gestures/Yes_1",
    "no": "animations/Stand/Gestures/No_1",

    # Conversation gestures
    "explain": "animations/Stand/Gestures/Explain_11",
    "thinking": "animations/Stand/Gestures/Thinking_1",
    "dont_know": "animations/Stand/Gestures/IDontKnow_1",

    # Emotion-style gestures
    "happy": "animations/Stand/Emotions/Positive/Happy_4",

    # Not a true dance animation; use as a playful/happy fallback.
    # A real "dance" may be an installed behavior, not an ALAnimationPlayer animation.
    "dance": "animations/Stand/Emotions/Positive/Happy_4",
    "air_guitar1": "animations/Stand/Waiting/AirGuitar_1",
    "air_guitar": "ht_animation_lib/guitar",
    "give": "animations/Stand/Gestures/Give_4"

}