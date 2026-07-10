from time import sleep
import threading
from ..utils import text_processing

class AppController:
    def __init__(
        self,
        config_manager,
        audio_recorder,
        agent_controller,
        web_ui,
        local_ui,
        pepper
    ):
        self.config = config_manager
        self.webui = web_ui
        self.localui = local_ui
        self.pepper = pepper
        self.audio = audio_recorder
        self.agent = agent_controller

        # Initialize request flags
        self.should_stop_app = False
        self.should_stop_agent = False
        self.should_start_agent = False

        # Initialize serving running flags
        self.pepper_running = False
        self.webui_running = False
        self.agent_running = False

        self.valid_languages = ["en","es"] #self.config_controller.get_setting("general", "languages")

    # spaghetti
    def agent_dialogue_cycle(self):
        self.set_status(status="idle")

        audio_input = self.get_audio_input()
        if (audio_input is None 
            or self.should_stop_agent 
            or self.should_stop_app): 
            return

        print("Transcribing...")
        user_text, detected_language = self.agent.transcribe_audio(audio_input)

        print(f"Heard: {user_text} ({detected_language})")
        self.set_status(status="thinking", heard=user_text)

        print("Generating response...")
        use_llm_filter = self.localui.get_ui_state()["use_llm_filter_var"].get()

        action = "NONE"
        
        if detected_language not in self.valid_languages or user_text.strip() == "":
            response = "I don't think I heard you right."

        elif not self.agent.is_content_safe(user_text, use_regex=True, use_llm=use_llm_filter):
            response = "Sorry, I can't help you with that."
        
        else:
            action, response = self.agent.generate_response(user_text, detected_language, get_action=self.pepper_running)
            print(f"LLM Response: {response}")

            if not self.agent.is_content_safe(response, use_regex=True, use_llm=use_llm_filter):
                response = "Sorry, I can't help you with that."
            else: response = text_processing.remove_formatting(response)

            self.set_status(status="speaking", heard=user_text, reply=response)

        print("Converting response to speech...")
        tts_text = text_processing.normalize_numbers_for_tts(response)
        self.agent.generate_speech(tts_text)
        
        should_play_audio_thru_pepper = True # placeholder for UI checkbox
        # should_play_audio_thru_pepper = self.localui.get_ui_state()["use_pepper_audio_var"].get()
        if should_play_audio_thru_pepper and self.pepper_running:
            self.pepper.play_audio()
        else: 
            self.agent.tts.play_audio_locally()
       
        pseudocode = """
        if self.pepper_running: 
            if action == "SING": 
                self.pepper.sing_happy_birthday()
            elif action == "WAVE":
                self.pepper.wave()
            ...
            elif action == "BODYTALK"
                self.pepper.body_talk(duration_seconds)
        """
        
        if action == "NONE":
            pass

        elif action == "BODYTALK": 
            duration_seconds = self.agent.tts.get_wav_duration_seconds()
            self.pepper.body_talk(duration_seconds)
            sleep(self.agent.tts.get_wav_duration_seconds()-1)

        elif action == "SING":         
            self.set_status(status="speaking", reply="Sure!")
            self.pepper.sing_happy_birthday()


    def run(self):
        self.initialize_app()

        self.worker_thread = threading.Thread(target=self.app_loop,daemon=True)
        self.worker_thread.start()

        self.start_app_launcher()
 
    def initialize_app(self):
        self.load_appstate_from_config()
        self.sync_localui_from_appstate()
        
        self.set_localui_callbacks()
        
        self.audio.set_keybinds(
            listen_key = self.listen_key,
            exit_key = self.exit_key
        )

    def app_loop(self):
        self.counter = 0 
        while not self.should_stop_app: #todo
            sleep(0.05)

            if not self.agent_running:
                if self.should_start_agent:
                    self.start_agent_services()
                continue

            if self.should_stop_agent:
                self.stop_agent_services()
                continue

            self.agent_dialogue_cycle() #  g

        self.stop_app(close_ui=False)

    def stop_app(self, close_ui:bool):
        self.stop_agent_services()
        if close_ui: self.localui.stop()

    def get_audio_input(self):
        # self.state.set_status("idle")
        # self.state.clear_exchange_text()
        audio_input = self.audio.record(
            on_listening_start=lambda: self.set_status("listening"),
            on_listening_stop=lambda: self.set_status("thinking"),
            should_cancel=lambda: (self.should_stop_agent or self.should_stop_app)
        )
        return audio_input

    def start_app_launcher(self):
        self.localui.renderer.set_options(
            llm_options = self.config.get_config_value("_notes", "_llm_models"),
            sr_options = self.config.get_config_value("_notes", "_whisper_models")
        )
        self.localui.start() 

    def start_agent_services(self):
        self.should_start_agent = False

        if not self.agent_running:
            if self.should_use_web_ui and not self.webui_running: 
                print("Starting web UI...")
                self.webui.load(use_background=True)
                self.webui_running = True
                sleep(0.05)

            if self.should_use_pepper and not self.pepper_running: 
                print("Starting pepper...")
                self.pepper.start()
                self.pepper_running = True
            
            self.agent.start(
                writer_model=self.writer_model, 
                judge_model=self.judge_model,
                whisper_model=self.whisper_model
            )
        
        self.agent_running = True

    def stop_agent_services(self):
        self.should_stop_agent = False
        if self.agent_running:
            if self.pepper_running: 
                self.pepper.stop()
                self.pepper_running = False
            if self.webui_running: 
                self.webui.stop()
                self.webui_running = False
            self.agent.stop()
        self.agent_running = False

    def load_appstate_from_config(self):
        # Runtime Services Options
        self.should_use_pepper = self.config.get_config_value("pepper", "should_use")
        self.should_use_web_ui = self.config.get_config_value("web_ui", "should_use")
        
        # Keybinds
        self.exit_key = self.config.get_config_value("keybinds", "exit_key")
        self.listen_key = self.config.get_config_value("keybinds", "listen_key")
        self.stop_key = self.config.get_config_value("keybinds", "stop_key")
        
        # LLM Models
        self.writer_model = self.config.get_config_value("writer_llm", "model")
        self.judge_model = self.config.get_config_value("judge_llm", "model")
        self.whisper_model = self.config.get_config_value("speech_recognition", "model")

    def save_appstate_to_config(self):
        # Runtime Services Options
        self.config.set_config_value("pepper", "should_use", self.should_use_pepper)
        self.config.set_config_value("web_ui", "should_use", self.should_use_web_ui)

        # Keybinds
        self.config.set_config_value("keybinds", "exit_key", self.exit_key)
        self.config.set_config_value("keybinds", "listen_key", self.listen_key)
        self.config.set_config_value("keybinds", "stop_key", self.stop_key)

        # LLM / speech models
        self.config.set_config_value("writer_llm", "model", self.writer_model)
        self.config.set_config_value("judge_llm", "model", self.judge_model)
        self.config.set_config_value("speech_recognition", "model", self.whisper_model)

    def sync_appstate_from_localui(self):
        self.should_use_pepper = self.localui.get_var("use_pepper_var")
        self.should_use_web_ui = self.localui.get_var("use_web_ui_var")

        self.writer_model = self.localui.get_var("writer_model_var")
        self.judge_model = self.localui.get_var("judge_model_var")
        self.whisper_model = self.localui.get_var("whisper_model_var")

    def sync_localui_from_appstate(self):
        self.localui.set_var("use_pepper_var", self.should_use_pepper)
        self.localui.set_var("use_web_ui_var", self.should_use_web_ui)

        self.localui.set_var("writer_model_var", self.writer_model)
        self.localui.set_var("judge_model_var", self.judge_model)
        self.localui.set_var("whisper_model_var", self.whisper_model)

    def set_localui_callbacks(self):
        self.localui.set_callbacks(
            on_start_agent_request = self.consume_start_agent_request,
            on_stop_agent_request = self.consume_stop_agent_request,
            on_close_app_request = self.consume_close_app_request,
            on_sing_happy_birthday_request = self.consume_sing_request,
            on_change_volume_request = self.consume_change_volume_request
        )

    def consume_start_agent_request(self):
        self.sync_appstate_from_localui()
        self.save_appstate_to_config()
        sleep(0.02)
        self.should_start_agent = True
        self.should_stop_agent = False

    def consume_stop_agent_request(self):
        self.sync_appstate_from_localui()
        self.save_appstate_to_config()
        sleep(0.02)
        self.should_stop_agent = True
        self.should_start_agent = False

    def consume_close_app_request(self):
        self.sync_appstate_from_localui()
        self.save_appstate_to_config()
        sleep(0.02)
        self.should_stop_app = True
        self.should_stop_agent = True
        self.should_start_agent = False

    def consume_sing_request(self):
        self.pepper_running = True
        self.pepper.start()
        self.pepper.sing_happy_birthday(upload=False)
        self.pepper.stop()
        self.pepper_running = False

    def consume_change_volume_request(self, volume):
        # self.sync_appstate_from_localui()
        # self.save_appstate_to_config()
        # sleep(0.02)
        # volume = self.config.get_config_value("pepper", "volume")/100
        volume = float(volume)/100
        self.pepper.set_volume(volume)
        print("Volume set to, {}".format(volume))

    def consume_set_filter_request(self, value:bool):
        self.use_llm_filter = value
        if value: print("LLM filter enabled.")
        if not value: print("LLM filter disabled")

    def set_status(self, status:str, heard:str=None, reply:str=None):
        statement = f"""
        Status: {status}
        Heard: {"" if heard is None else heard}
        Reply: {"" if reply is None else reply}
        """
        print(statement)

        if self.should_use_web_ui: self.webui.update_ui(status, heard, reply)

