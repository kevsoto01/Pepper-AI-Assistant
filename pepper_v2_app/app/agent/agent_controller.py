from __future__ import annotations

from ..utils.language import LANGUAGE_NAME
from ..utils import text_processing


class AIAgentController:
    def __init__(
        self,
        whisper,
        llm_system,
        piper,
        config
    ):
        self.sr = whisper
        self.llm = llm_system
        self.tts = piper
        self.config = config

        self.last_heard_text = ""
        self.last_detected_language = None
        self.last_reply_text = ""

    # Lifecycle
    def start(self, writer_model, judge_model, whisper_model):
        self.sr.load(whisper_model=whisper_model)
        self.tts.load()
        self.llm.load(writer_model=writer_model, judge_model=judge_model)

    def stop(self):
        self.sr.unload()
        self.llm.unload()
        self.tts.unload()

    # Audio
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
    
    # LLM Helpers
    def generate_response(self, user_text, detected_language) -> str:
        max_turns = self.config_controller.get_setting("general", "max_turns")
        word_count = self.config_controller.get_setting("general", "word_count")
        language_name = LANGUAGE_NAME.get(detected_language, "English")
        response = self.llm.answer_generator.generate_response(user_text, language_name, max_turns, word_count)
        return response
    
    def is_content_safe(self, text:str, use_llm:bool=True, use_regex:bool=True) -> bool:
        if use_regex and not self._check_safety_regex(text):
            return False
        if use_llm and not self._check_safety_llm(text):
            return False
        return True
    
    def simplify_answer(self, user_text, assistant_text):
        age = self.config_controller.get_setting("general", "user_age")
        if age>=18 or not self._should_answer_be_simplified(user_text, assistant_text, age):
            print(f"Answer is already parsed for a(n) {age}-year-old's level of comprehension.")
            return assistant_text
        return self.llm.answer_simplifier.simplify(assistant_text, age)

    def identify_appropriate_action(self):
        pseudocode = """

        if should_i_sing: return "SING"
        elif should_i_wave: return "WAVE"
        elif should_i_dance: return "DANCE"
        else: return "BODYTALK"
        
        """

        return "BODYTALK" # temporary
    
        action = "NONE" if not get_action else self.llm.get_action(user_text)
        return action
    
    def get_relevant_info_for_user_question(self, user_text):
        if not self._does_question_require_rag(user_text):
            return ""
        optimized_query = self.llm.rag_query_optimizer.optimize(user_text)
        results = self.llm.rag.search(query=optimized_query,top_k=4)
        context = self.llm.rag.find_context(question=optimized_query, results=results)
        print(context)
        return context
        

        
    
    # Internal
    def _check_safety_regex(self, text) -> bool:
        filter_result = text_processing.find_filtered_term(text)
        if filter_result["matched"]:
            return False
        return True

    def _check_safety_llm(self, text) -> bool:
        safety_classification = self.llm.child_safety_verifier.classify(text)
        if safety_classification == "SAFE": return True
        if safety_classification == "UNSAFE": return False
        print("Unexpected safety classification, classifying as unsafe.")
        return False
    
    def _does_question_require_rag(self, user_text):
        rag_necessity = self.llm.rag_need_classifier.classify(user_text)
        if rag_necessity == "RAG": return True
        if rag_necessity == "NO_RAG": return False
        print("Unexpected rag necessity classification, classifying as needed.")
        return True  
    
    def _does_user_want_birthday_song(self, user_text):
        birthday_song_intent = self.llm.birthday_classifier.classify(user_text)
        print("birthday_song_intent:", birthday_song_intent)
        if birthday_song_intent == "SING": return True
        if birthday_song_intent == "OTHER": return False
        print("Unexpected birthday song intent classification, classifying as other.")
        return False
    
    def _should_answer_be_simplified(self, user_text, assistant_text, age):
        answer_complexity = self.llm.complexity_classifier.classify(user_text, assistant_text, age)
        if answer_complexity == "COMPLEX": return True
        if answer_complexity == "SIMPLE": return False
        print("Unexpected complexity classification, classifying as simple.")
        return False
    
    """
    To do:

     def _does_user_want_pepper_dance(self):
        return False
    """
    
