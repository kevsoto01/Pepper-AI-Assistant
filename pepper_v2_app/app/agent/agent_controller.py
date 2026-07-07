from __future__ import annotations

from ..utils.language import LANGUAGE_NAME
from ..utils.text_processing import (
    remove_formatting,
    normalize_numbers_for_tts,
    detect_language,
    find_filtered_term,
)


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

        self.valid_languages = ["en","es"]#self.config_controller.get_setting("general", "languages")
        self.age = 100#self.config_controller.get_setting("general", "user_age")

        self.status_callback = None

        self.last_heard_text = ""
        self.last_detected_language = None
        self.last_reply_text = ""

    # ------------------------------------------------------------------
    # Callback wiring
    # ------------------------------------------------------------------
    def set_callback(self, status_callback) -> None:
        self.status_callback = status_callback

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def start(self, writer_model, judge_model, whisper_model):
        self.sr.load(
            whisper_model=whisper_model
            )
        self.tts.load()
        self.llm.load(
            writer_model=writer_model,
            judge_model=judge_model
            )

    def stop(self):
        self.llm.unload()

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------
    def answer_question(self, audio_input, use_llm=True):
        if audio_input is None:
            return None

        # Speech Recognition
        print("Transcribing...")
        user_text, detected_language = self.transcribe_audio(audio_input)

        print(f"Heard: {user_text} ({detected_language})")
        self.set_status(status="thinking", heard=user_text)


        # if self.llm.should_sing_birthday_song(user_text):
        #     return True

        # Answer Generation
        print("Generating response...")
        response = self.response_router(user_text, detected_language, use_llm=use_llm)
        response = self.remove_formatting(response)

        print(f"LLM Response: {response}")
        self.set_status(status="speaking", reply=response)

        # Text-to-speech
        print("Converting response to speech...")
        tts_text = self.clean_for_tts(response)
        speech = self.generate_speech(tts_text)

        # this should return a tuple that provides a recommended animation
        return False

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------
    def response_router(self, user_text, detected_language, use_llm) -> str:
        if detected_language not in self.valid_languages or user_text.strip() == "":
            return self.handle_misheard_input()
        if self.check_safety(user_text, override=False, use_llm=use_llm):
            return self.handle_valid_input(user_text, detected_language, use_llm=use_llm)
        return self.handle_filtered_content()

    def handle_valid_input(self, user_text, detected_language, use_llm) -> str:
        ai_response = self.generate_response(user_text, detected_language)
        filtered_ai_response = self.llm_response_safety_filter(ai_response, use_llm=use_llm)
        return filtered_ai_response

    def handle_filtered_content(self) -> str:
        return "Sorry, I can't help you with that."

    def handle_misheard_input(self) -> str:
        return "I don't think I heard you right."

    # ------------------------------------------------------------------
    # Content generation
    # ------------------------------------------------------------------
    def generate_response(self, user_text, detected_language) -> str:
        language_name = LANGUAGE_NAME.get(detected_language, "English")
        return self.llm.answer_question(user_text, language_name)

    # ------------------------------------------------------------------
    # Audio helpers
    # ------------------------------------------------------------------
    def transcribe_audio(self, audio_input):
        transcription = self.sr.transcribe_audio(audio_input)

        if not isinstance(transcription, dict):
            print("Invalid transcription result.")
            return "", None

        user_text = transcription.get("text", "")
        detected_language = transcription.get("language")
        return user_text, detected_language

    def generate_speech(self, message):
        language = self.detect_language(message)
        voice_response = self.tts.generate_speech(message, language)
        return voice_response

    # ------------------------------------------------------------------
    # Publishing helper
    # ------------------------------------------------------------------
    def set_status(self, status: str, **kwargs) -> None:
        self.status_callback(status, **kwargs)

    # ------------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------------
    def detect_language(self, text):
        return detect_language(text)

    def clean_for_tts(self, text):
        return normalize_numbers_for_tts(text)

    def remove_formatting(self, text):
        return remove_formatting(text)

    # ------------------------------------------------------------------
    # Safety helpers
    # ------------------------------------------------------------------
    def llm_response_safety_filter(self, text:str, use_llm:bool=True, override:str=False) -> str:
        if self.check_safety(text, use_llm, override):
            return text
        return self.handle_filtered_content()

    def check_safety_regex(self, text) -> bool:
        filter_result = find_filtered_term(text)
        if filter_result["matched"]:
            return False
        return True

    def check_safety_llm(self, text) -> bool:
        return self.llm.verify_safety(text)

    def check_safety(self, text:str, use_llm:bool, override:bool=False) -> bool:
        if override: return True
        if not self.check_safety_regex(text): return False
        if use_llm and not self.check_safety_llm(text): return False
        return True
