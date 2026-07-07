import time

from .controls.keyboard import exit_key_pressed, stop_key_pressed
from .audio.ptt_audio_recorder import record_audio_with_preroll
from .utils.language import LANGUAGE_NAME
from .utils.text_processing import (
    remove_formatting, 
    normalize_numbers_for_tts,
    detect_language,
    find_filtered_term
    )

class AIAgentController:
    
    def __init__(
            self, 
            whisper, 
            llm_system,
            piper, 
            web_ui_controller,
            local_ui_controller,
            pepper_controller, 
            config_controller
            # languages, 
            # user_age,
            # keep_local, 
            # use_ui
            ):
        
        # AI Assistants
        self.sr = whisper
        self.llm = llm_system
        self.tts = piper
        
        # Controllers
        self.web_ui = web_ui_controller
        self.local_ui = local_ui_controller
        self.pepper = pepper_controller
        self.config_controller = config_controller
        
    
    def run_assistant(self):
        self.start()
        print("-"*50)
        while not exit_key_pressed():
            if self.use_ui: self.web_ui.set_idle()
            audio_input = self.record_audio()
            
            self.timer1 = time.time() 
            self.timer2 = time.time()
            
            if audio_input is not None:
                user_text, detected_language = self.transcribe_audio(audio_input)
                if detected_language in self.valid_languages:
                    if self.check_safety(user_text, use_llm=False):
                        self.handle_valid_input(user_text, detected_language)
                    else:
                        self.handle_filtered_content()
                else:
                    self.handle_misheard_input(detected_language)   
            print("\n"+"-"*50)
            time.sleep(0.01)
            
        self.stop()
    
    
    def start(self):
        self.apply_config()
        print("Config applied.")
        print("Use Pepper?: {}".format(self.keep_local))
        if self.use_ui: self.web_ui.load()
        if not self.keep_local: self.pepper.start()
        self.sr.load()
        self.tts.load()
        self.llm.load()
        
    def stop(self):
        if self.use_ui: self.web_ui.unload()
        if not self.keep_local: self.pepper.stop()
        self.llm.unload()
        print("\n"+"-"*30+"\nPLEASE TURN OFF THE MICROPHONE\n"+"-"*30+"\n")
        
    def apply_config(self)->None:
        self.valid_languages = self.config_controller.get_setting("general", "languages")
        self.age = self.config_controller.get_setting("general", "user_age")
        self.keep_local = not self.config_controller.get_setting("pepper", "should_use")
        self.use_ui = self.config_controller.get_setting("web_ui", "use_ui")
    
    def timer(self, total_time:bool = False):
        time_elapsed = int(1000*(time.time() - self.timer2))
        if total_time:
            time_elapsed = int(1000*(time.time() - self.timer1))
        self.timer2 = time.time()
        return time_elapsed
        
    
    def print_time(self, process:str=""):
        time = self.timer()
        print(f"({process}: {time} ms)")
        
        
    def record_audio(self):
        audio_input = record_audio_with_preroll(
            on_listening_start=self.web_ui.set_listening if self.use_ui else None,
            on_listening_stop=self.web_ui.set_thinking if self.use_ui else None
            )
        print("Saved:", audio_input)
        return audio_input
    
    
    def transcribe_audio(self, audio_input):
        print("\nTranscribing...")
        if self.use_ui: self.web_ui.set_thinking()
        
        transcription = self.sr.transcribe_audio(audio_input)
        user_text = transcription["text"]
        detected_language = transcription["language"]
        print("\nUnfiltered transcription:", user_text)
        self.print_time("Transcription:")
        return user_text, detected_language
    
    
    def speak(self, message):
        language = detect_language(message)
        print(language)
        
        message = normalize_numbers_for_tts(message)
        print("TTS-readable response:", message)
        
        self.tts.generate_speech(message, language)
        self.print_time("Text-to-speech")
        print("\nTotal response time: ", self.timer(True), " ms") 
        
        time.sleep(0.05)
        playback_time = self.tts.get_wav_duration_seconds()
        print("Speaking...")
        
        if self.use_ui: self.web_ui.set_speaking(reply=message)
        
        if not self.keep_local: self.pepper.play_audio()
        else: self.tts.play_audio_locally()
        
        if not self.keep_local:
            start_time = time.time()
            while time.time()-start_time<playback_time:
                if stop_key_pressed(): 
                    self.pepper.stop_audio()
                    break
                time.sleep(0.01)
    
    #%% Safety Check
    def check_safety_regex(self, text):
        filter_result = find_filtered_term(text)
        if filter_result["matched"]:
            print("Hard filter matched:", filter_result)
            return False
        return True
    
    def check_safety_llm(self, text):
        llm_result = self.llm.verify_safety(text)
        print("LLM safety result:", llm_result)
        self.print_time("LLM Safety Check")
        return llm_result
    
    def check_safety(self, text, use_llm:bool=True):
        if not self.check_safety_regex(text):
            return False
        if use_llm:
            if not self.check_safety_llm(text):
                return False
        return True
       
    #%% Input Handling     
    def handle_valid_input(self, user_text, detected_language):
        print("\nHeard:", user_text, "\n")
        print("Language:", LANGUAGE_NAME[detected_language])
        if self.use_ui: self.web_ui.set_thinking(heard=user_text)
        print("Sending to Ollama...")
        
        response = self.llm.answer_question(user_text, LANGUAGE_NAME[detected_language])
        print("Raw LLM response:", response)
        response = remove_formatting(response)
        
        self.print_time("Answer Generator")
        # if self.age<=18:
        #     response = self.llm.simplify_answer(response, self.age)
        #     print("\Raw unfiltered LLM response:", response,"\n")
        #     response = remove_formatting(response)
        if self.check_safety(response):
            if self.use_ui: self.web_ui.set_speaking(reply=response)
            print("\nConverting to speech...")
            self.speak(response)
        else:
            self.handle_filtered_content()
            
    
    def handle_filtered_content(self):
        error_msg = "Sorry, I can't process that request." #randomized error messages
        print(error_msg, "Filtered content detected.")
        if self.use_ui: 
            self.web_ui.set_thinking(heard="Filtered content detected.")
            self.web_ui.set_speaking(reply=error_msg)
        self.speak(error_msg)
        return
    
    
    def handle_misheard_input(self, detected_language):
        error_msg = "I don't think I heard you right. Please try again." 
        print(error_msg, f"({LANGUAGE_NAME[detected_language]})")
        if self.use_ui: 
            self.web_ui.set_thinking(heard=f"Detected: {LANGUAGE_NAME[detected_language]}")
            self.web_ui.set_speaking(reply=error_msg)
        self.speak(error_msg)
        return
    
    #%% Content Generation
    # def generate_answer(self, user_text, detected_language):