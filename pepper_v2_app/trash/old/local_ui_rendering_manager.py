import tkinter as tk
from tkinter import ttk

from ..local_ui_element_templates import LocalUIElementTemplateBuilder

class LocalUIRenderingManager:
    def __init__(self):
        print("Local UI placeholder loaded")
        self.template_builder = LocalUIElementTemplateBuilder()
    
    def build_ui(self):
        self.root = tk.Tk()
        self.root.title("UI Builder Test")
        self.root.geometry("400x400")
        
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill="both", expand=True)
        
        self.build_use_pepper_toggle()
        self.build_use_web_ui_toggle()
        self.build_volume_slider()
        self.build_writer_llm_dropdown()
        self.build_judge_llm_dropdown()
        self.build_whisper_model_dropdown()
    
    # Toggles
    def build_use_pepper_toggle(self):
        self.use_pepper_toggle, self.use_pepper_toggle_var = self.template_builder.checkbutton(
            self.main_frame,
            text="Use Pepper"
        )
        self.use_pepper_toggle.pack(pady=10)
        
    def build_use_web_ui_toggle(self):
        self.use_web_ui_toggle, self.use_web_ui_toggle_var = self.template_builder.checkbutton(
            self.main_frame,
            text="Use web UI"
        )
        self.use_web_ui_toggle.pack(pady=10)
        
    # Sliders    
    def build_volume_slider(self):
        self.volume_slider, self.volume_var = self.template_builder.horizontal_slider(
            self.main_frame,
            from_=0,
            to=100
        )
        self.volume_slider.pack(fill="x", pady=10)
    
    # Dropdowns
    def build_writer_llm_dropdown(self):
        self.writer_llm_dropdown, self.writer_llm_dropdown_var = self.template_builder.dropdown(
            self.main_frame,
            values=self.config_controller.get_setting("_notes", "_llm_models")
        )
        self.writer_llm_dropdown.pack(pady=10)
        
    def build_judge_llm_dropdown(self):
        self.judge_llm_dropdown, self.judge_llm_dropdown_var = self.template_builder.dropdown(
            self.main_frame,
            values=self.config_controller.get_setting("_notes", "_llm_models")
        )
        self.judge_llm_dropdown.pack(pady=10)
    
    def build_whisper_model_dropdown(self):
        self.whisper_model_dropdown, self.whisper_model_dropdown_var = self.template_builder.dropdown(
            self.main_frame,
            values=self.config_controller.get_setting("_notes", "_whisper_models")
        )
        self.whisper_model_dropdown.pack(pady=10)
        
   