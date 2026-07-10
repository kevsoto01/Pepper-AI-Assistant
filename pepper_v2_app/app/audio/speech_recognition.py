import torch
from faster_whisper import WhisperModel
import gc

class WhisperTranscriber:
    
    def load(self, whisper_model):
        print("Loading Whisper transcriber...")
        cuda_availability = "Yes" if torch.cuda.is_available() else "No"
        print("\nIs CUDA available: "+cuda_availability)
        if torch.cuda.is_available():
            print("CUDA device: "+torch.cuda.get_device_name(0))
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.whisper_model = WhisperModel(whisper_model, device=self.device, compute_type=self.compute_type)
        

    def unload(self):
        if hasattr(self, "whisper_model"):
            del self.whisper_model
            self.whisper_model = None

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    print("Whisper transcriber unloaded.")
    def transcribe_audio(self, audio):
        if not audio:
            return ""

        segments, info = self.whisper_model.transcribe(audio, beam_size=5)

        text = "".join(segment.text for segment in segments).strip()
        detected_language = info.language
        
        if detected_language == 'pt': detected_language = 'es' #assume portuguese is spanish
        if detected_language == 'cy': detected_language = 'en' #assume welsh is english
        
        return {
            "text": text,
            "language": detected_language
        }
    
