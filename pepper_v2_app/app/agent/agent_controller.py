from __future__ import annotations

from ..utils.language import LANGUAGE_NAME
from ..utils import text_processing


class AIAgentController:
    def __init__(
        self,
        whisper,
        llm_system,
        piper
    ):
        self.sr = whisper
        self.llm = llm_system
        self.tts = piper

         
        self.age = 100 #self.config_controller.get_setting("general", "user_age")

        self.status_callback = None

        self.last_heard_text = ""
        self.last_detected_language = None
        self.last_reply_text = ""

    def start(self, writer_model, judge_model, whisper_model):
        self.sr.load(whisper_model=whisper_model)
        self.tts.load()
        self.llm.load(writer_model=writer_model, judge_model=judge_model)

    def stop(self):
        self.sr.unload()
        self.llm.unload()
        self.tts.unload()

    def generate_response(self, user_text, detected_language, get_action:bool) -> tuple[str,str]:
        language_name = LANGUAGE_NAME.get(detected_language, "English")
        response = self.llm.answer_question(user_text, language_name)
        action = "NONE" if not get_action else self.llm.get_action(user_text)

        return action, response
    
    def transcribe_audio(self, audio_input) -> tuple[str,str|None]:
        transcription = self.sr.transcribe_audio(audio_input)
        if not isinstance(transcription, dict):
            print("Invalid transcription result.")
            return "", None
        user_text = transcription.get("text", "")
        detected_language = transcription.get("language")
        
        return user_text, detected_language

    def generate_speech(self, message) -> None:
        language = text_processing.detect_language(message)
        self.tts.generate_speech(message, language) 
        # this automatically writes the generated speech to temp/piper_output.wav 
        # when calling play audio (pepper or not) it always points to that file

    def is_content_safe(self, text:str, use_llm:bool=True, use_regex:bool=True) -> bool:
        if use_regex and not self.check_safety_regex(text):
            return False
        if use_llm and not self.check_safety_llm(text):
            return False
        return True

    def check_safety_regex(self, text) -> bool:
        filter_result = text_processing.find_filtered_term(text)
        if filter_result["matched"]:
            return False
        return True

    def check_safety_llm(self, text) -> bool:
        return self.llm.verify_safety(text)