import winsound
import wave
import gc
from pathlib import Path
from ..utils.paths import LOCAL_PEPPER_AUDIO, PIPER_DIR, PIPER_MODEL_DIR
from piper.voice import PiperVoice
from piper.voice import SynthesisConfig

# from piper import PiperVoice

DEFAULT_CONFIG = {
    'noise_scale': 0.7,
    'length_scale': 0.9,
    'noise_w': 0.75
    }   

class PiperTTS:
    def __init__(self, config=DEFAULT_CONFIG):
        self.voice = {}
        
        self.syn_config = SynthesisConfig(
            noise_scale = config['noise_scale'],
            length_scale= config['length_scale'],
            noise_w_scale = config['noise_w'],
        )
        
        self.audio_dir = str(LOCAL_PEPPER_AUDIO)
        
    def load(self):
        print("Loading Piper TTS...")
        for language, path in PIPER_MODEL_DIR.items():
            model_path = Path(path)
            self.voice[language] = PiperVoice.load(model_path)

    def unload(self):
        try: winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception: pass
        self.voice.clear()
        gc.collect()
        print("Piper TTS unloaded.")

    def generate_speech(self, text, language):   
        with wave.open(self.audio_dir, "wb") as wav_file:
            self.voice[language].synthesize_wav(text, wav_file, syn_config=self.syn_config)
        return self.audio_dir
    
    def get_wav_duration_seconds(self):
        with wave.open(self.audio_dir, "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return frames / float(rate)
    
    def play_audio_locally(self):
        winsound.PlaySound(self.audio_dir, winsound.SND_FILENAME)