from time import sleep
import threading

from ..controls import keyboard

class AppController:
    def __init__(self, 
                 agent_controller, 
                 web_ui_controller, 
                 local_ui_controller, 
                 pepper_controller, 
                 config_controller,
                 audio_recorder,
                 state_manager
                 ):
        
        self.agent_controller = agent_controller
        self.web_ui = web_ui_controller
        self.local_ui = local_ui_controller
        self.pepper = pepper_controller
        self.config_controller = config_controller
        self.audio_recorder = audio_recorder
        self.state = state_manager
        
        self.last_config = None
        self.audio_input = None
    #%% App
        
    def app(self):
        
        self.initialize_app()
        
        self.start_app_launcher()
        
        self.start_app_loop()
            
        self.stop_app()
    
    # def run_app(self):
    #     self.start_app()
        
    #     while not self.should_stop_app():
    #         self.app_tick()
    #         # self.local_ui.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
    
    
    #         # self.local_ui.root.mainloop()
            
    #         sleep(0.01)
    
    def start_app_loop(self):
        while not self.should_stop_app():
            
            self.app_tick
            
            if not self.is_agent_running:
                self.agent_thread.start()
            
            sleep(0.01)
    
    def initialize_app(self):
        self.initialize_instance_attributes()
        
        self.start_local_ui()
        self.start_web_ui()
        self.start_pepper()
        self.load_agent()
        
        self.open_agent_thread()
        
    def open_agent_thread(self):
        self.agent_thread = threading.Thread(target=self.agent_dialogue_loop)
    
    def close_agent_thread(self):
        self.agent_running = False
        self.agent_thread.join()
    
    def app_tick(self):
        self.update_config_from_local_ui()
        if self.ui.start_agent_requested(): self.start_agent()
        if self.ui.stop_agent_requested(): self.stop_agent()
        # self.ui.root.after(30, self.app_tick)
    
    #%% Agent Dialogue Loop
    
    def agent_dialogue_loop(self):
        while not self.should_stop_agent():
            self.agent_dialogue_cycle()
            sleep(0.01)
    
    def agent_dialogue_cycle(self):
        self.get_audio_input()
        self.get_agent_response()
        self.say_agent_response()
        
    def get_audio_input(self):
        self.set_status("idle")
        self.audio_input = self.audio_recorder.record(
            on_listening_start=lambda: self.set_status("listening"),
            on_listening_stop=lambda: self.set_status("thinking")
        )
        
    def get_agent_response(self):
        self.set_status("thinking")
        self.agent_controller.answer_question(self.audio_input)
    
    def say_agent_response(self):
        self.set_status("speaking")
        self.speak()
           
    
        
    #%% Threading
    # def set_status_threadsafe(self, status):
    #     self.local_ui.root.after(
    #         0,
    #         lambda: self.ui.set_status(status)
    #     )

    # def on_window_close(self):
    #     self.is_agent_running = False
    #     self.stop()
    #     self.local_ui.root.destroy()

    #%% Agent Worker
    def start_agent_worker(self):
        if self.is_agent_running: return

        self.is_agent_running = True

        self.worker_thread = threading.Thread(
            target=self.app_worker_function,
            daemon=True
        )

        self.worker_thread.start()
        print("Worker thread started")

    def stop_agent_worker(self):
        self.is_agent_running = False        
        
    def speak(self):
        self.agent_controller.tts.play_audio_locally()
        
    

    #%% App launcher helpers
    
    def stop_app(self):
        print("Stopping app")
        self.local_ui.stop()
        self.agent_controller.stop()
        self.pepper.stop()
        self.web_ui.stop()
    
    def update_variables_from_config(self): 
        # Start Conditions
        self.should_use_pepper = self.config_controller.get_setting("pepper", "should_use")
        self.should_use_web_ui = self.config_controller.get_setting("web_ui", "use_ui")

        # Keybinds
        self.exit_key = self.config_controller.get_setting("keybinds", "exit_key")
        self.listen_key = self.config_controller.get_setting("keybinds", "listen_key")
        self.stop_key = self.config_controller.get_setting("keybinds", "stop_key")

    def start_local_ui(self):
        self.local_ui.load()

    def start_web_ui(self):
        if self.should_use_web_ui: self.web_ui.load()
    
    def start_pepper(self):
        if self.should_use_pepper: self.pepper.start()
            
    def load_agent(self):
        self.agent_controller.load()
        
    
    
    #%% Status helper
    def set_status(self, status:str):
        status_methods = {
            "idle": self.state.set_idle,
            "listening": self.state.set_listening,
            "thinking": self.state.set_thinking,
            "speaking": self.state.set_speaking
            }
        
        status_methods[status]()
        
    