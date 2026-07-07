import tkinter as tk
from tkinter import ttk

from .local_ui_element_templates import LocalUIElementTemplateBuilder


class LocalUIRenderingManager:
    """
    Builds and manages the local Tkinter UI.

    This class should:
    - create the Tkinter window
    - create UI elements
    - connect widget changes to state/config updates
    - refresh visible UI from state

    This class should NOT:
    - start the agent directly
    - stop the agent directly
    - talk to Pepper directly
    - run LLM logic directly
    """

    def __init__(self, config_controller=None, state_manager=None):
        print("Local UI rendering manager loaded")

        self.config_controller = config_controller
        self.state_manager = state_manager

        self.template_builder = LocalUIElementTemplateBuilder()

        self.root = None
        self.main_frame = None

        # Widget references
        self.use_pepper_toggle = None
        self.use_web_ui_toggle = None
        self.volume_slider = None

        self.writer_llm_dropdown = None
        self.judge_llm_dropdown = None
        self.whisper_model_dropdown = None

        self.start_agent_button = None
        self.stop_agent_button = None
        self.exit_button = None

        self.status_label = None
        self.heard_text_label = None
        self.reply_text_label = None
        self.error_text_label = None

        # Tkinter variables
        self.use_pepper_toggle_var = None
        self.use_web_ui_toggle_var = None
        self.volume_var = None

        self.writer_llm_dropdown_var = None
        self.judge_llm_dropdown_var = None
        self.whisper_model_dropdown_var = None

    # =============================================================
    # Public API
    # =============================================================

    def build_ui(self):
        self.root = tk.Tk()
        self.root.title("Pepper Local UI")
        self.root.geometry("500x650")
        self.root.minsize(450, 550)

        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        self.build_title_section()
        self.build_mode_section()
        self.build_agent_control_section()
        self.build_settings_section()
        self.build_status_section()

        self.load_initial_values()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def run(self):
        if self.root is None:
            self.build_ui()

        self.start_auto_refresh()
        self.root.mainloop()

    def refresh_from_state(self):
        """
        Pulls display state from LocalUIStateManager and updates the UI.

        This is useful when the agent changes status, heard text,
        reply text, or error text.
        """
        if self.state_manager is None:
            return

        ui_state = self.state_manager.get_ui_state()

        if self.status_label is not None:
            self.status_label.config(
                text=f"Status: {ui_state.get('agent_status', 'idle')}"
            )

        if self.heard_text_label is not None:
            heard_text = ui_state.get("heard_text", "")
            self.heard_text_label.config(text=f"Heard: {heard_text}")

        if self.reply_text_label is not None:
            reply_text = ui_state.get("reply_text", "")
            self.reply_text_label.config(text=f"Reply: {reply_text}")

        if self.error_text_label is not None:
            error_message = ui_state.get("error_message", "")
            self.error_text_label.config(text=f"Error: {error_message}")

    def start_auto_refresh(self):
        """
        Refreshes the UI repeatedly without blocking Tkinter.
        """
        self.refresh_from_state()

        if self.root is not None:
            self.root.after(250, self.start_auto_refresh)

    # =============================================================
    # Sections
    # =============================================================

    def build_title_section(self):
        title = ttk.Label(
            self.main_frame,
            text="Pepper Local UI",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=(0, 20))

    def build_mode_section(self):
        section = ttk.LabelFrame(self.main_frame, text="Mode Settings", padding=15)
        section.pack(fill="x", pady=10)

        self.build_use_pepper_toggle(section)
        self.build_use_web_ui_toggle(section)

    def build_agent_control_section(self):
        section = ttk.LabelFrame(self.main_frame, text="Agent Controls", padding=15)
        section.pack(fill="x", pady=10)

        self.start_agent_button = ttk.Button(
            section,
            text="Start Agent",
            command=self.on_start_agent_clicked
        )
        self.start_agent_button.pack(fill="x", pady=5)

        self.stop_agent_button = ttk.Button(
            section,
            text="Stop Agent",
            command=self.on_stop_agent_clicked
        )
        self.stop_agent_button.pack(fill="x", pady=5)

        self.exit_button = ttk.Button(
            section,
            text="Exit App",
            command=self.on_close
        )
        self.exit_button.pack(fill="x", pady=5)

    def build_settings_section(self):
        section = ttk.LabelFrame(self.main_frame, text="Model Settings", padding=15)
        section.pack(fill="x", pady=10)

        self.build_volume_slider(section)
        self.build_writer_llm_dropdown(section)
        self.build_judge_llm_dropdown(section)
        self.build_whisper_model_dropdown(section)

    def build_status_section(self):
        section = ttk.LabelFrame(self.main_frame, text="Agent Status", padding=15)
        section.pack(fill="both", expand=True, pady=10)

        self.status_label = ttk.Label(section, text="Status: idle")
        self.status_label.pack(anchor="w", pady=5)

        self.heard_text_label = ttk.Label(
            section,
            text="Heard:",
            wraplength=400
        )
        self.heard_text_label.pack(anchor="w", pady=5)

        self.reply_text_label = ttk.Label(
            section,
            text="Reply:",
            wraplength=400
        )
        self.reply_text_label.pack(anchor="w", pady=5)

        self.error_text_label = ttk.Label(
            section,
            text="Error:",
            wraplength=400
        )
        self.error_text_label.pack(anchor="w", pady=5)

    # =============================================================
    # Toggles
    # =============================================================

    def build_use_pepper_toggle(self, parent_frame):
        self.use_pepper_toggle, self.use_pepper_toggle_var = (
            self.template_builder.checkbutton(
                parent_frame,
                text="Use Pepper"
            )
        )

        self.use_pepper_toggle.config(command=self.on_use_pepper_changed)
        self.use_pepper_toggle.pack(anchor="w", pady=5)

    def build_use_web_ui_toggle(self, parent_frame):
        self.use_web_ui_toggle, self.use_web_ui_toggle_var = (
            self.template_builder.checkbutton(
                parent_frame,
                text="Use Web UI"
            )
        )

        self.use_web_ui_toggle.config(command=self.on_use_web_ui_changed)
        self.use_web_ui_toggle.pack(anchor="w", pady=5)

    # =============================================================
    # Sliders
    # =============================================================

    def build_volume_slider(self, parent_frame):
        label = ttk.Label(parent_frame, text="Volume")
        label.pack(anchor="w", pady=(5, 0))

        self.volume_slider, self.volume_var = (
            self.template_builder.horizontal_slider(
                parent_frame,
                from_=0,
                to=100
            )
        )

        self.volume_slider.config(command=self.on_volume_changed)
        self.volume_slider.pack(fill="x", pady=5)

    # =============================================================
    # Dropdowns
    # =============================================================

    def build_writer_llm_dropdown(self, parent_frame):
        label = ttk.Label(parent_frame, text="Writer LLM")
        label.pack(anchor="w", pady=(10, 0))

        values = self.get_config_list("_notes", "_llm_models")

        self.writer_llm_dropdown, self.writer_llm_dropdown_var = (
            self.template_builder.dropdown(
                parent_frame,
                values=values
            )
        )

        self.writer_llm_dropdown.bind(
            "<<ComboboxSelected>>",
            self.on_writer_llm_changed
        )

        self.writer_llm_dropdown.pack(fill="x", pady=5)

    def build_judge_llm_dropdown(self, parent_frame):
        label = ttk.Label(parent_frame, text="Judge LLM")
        label.pack(anchor="w", pady=(10, 0))

        values = self.get_config_list("_notes", "_llm_models")

        self.judge_llm_dropdown, self.judge_llm_dropdown_var = (
            self.template_builder.dropdown(
                parent_frame,
                values=values
            )
        )

        self.judge_llm_dropdown.bind(
            "<<ComboboxSelected>>",
            self.on_judge_llm_changed
        )

        self.judge_llm_dropdown.pack(fill="x", pady=5)

    def build_whisper_model_dropdown(self, parent_frame):
        label = ttk.Label(parent_frame, text="Whisper Model")
        label.pack(anchor="w", pady=(10, 0))

        values = self.get_config_list("_notes", "_whisper_models")

        self.whisper_model_dropdown, self.whisper_model_dropdown_var = (
            self.template_builder.dropdown(
                parent_frame,
                values=values
            )
        )

        self.whisper_model_dropdown.bind(
            "<<ComboboxSelected>>",
            self.on_whisper_model_changed
        )

        self.whisper_model_dropdown.pack(fill="x", pady=5)

    # =============================================================
    # Initial values
    # =============================================================

    def load_initial_values(self):
        """
        Loads saved config values into the visible UI.
        """

        if self.config_controller is None:
            return

        use_pepper = self.get_config_value("ui", "should_use_pepper", False)
        use_web_ui = self.get_config_value("ui", "should_use_web_ui", False)
        volume = self.get_config_value("audio", "volume", 100)

        writer_llm = self.get_config_value("llm", "writer_model", "")
        judge_llm = self.get_config_value("llm", "judge_model", "")
        whisper_model = self.get_config_value("audio", "whisper_model", "")

        if self.use_pepper_toggle_var is not None:
            self.use_pepper_toggle_var.set(use_pepper)

        if self.use_web_ui_toggle_var is not None:
            self.use_web_ui_toggle_var.set(use_web_ui)

        if self.volume_var is not None:
            self.volume_var.set(volume)

        if self.writer_llm_dropdown_var is not None:
            self.writer_llm_dropdown_var.set(writer_llm)

        if self.judge_llm_dropdown_var is not None:
            self.judge_llm_dropdown_var.set(judge_llm)

        if self.whisper_model_dropdown_var is not None:
            self.whisper_model_dropdown_var.set(whisper_model)

    # =============================================================
    # UI callbacks
    # =============================================================

    def on_use_pepper_changed(self):
        value = bool(self.use_pepper_toggle_var.get())

        if self.state_manager is not None:
            self.state_manager.set_use_pepper(value)

        self.set_config_value("pepper", "should_use_pepper", value)

    def on_use_web_ui_changed(self):
        value = bool(self.use_web_ui_toggle_var.get())

        if self.state_manager is not None:
            self.state_manager.set_use_web_ui(value)

        self.set_config_value("web_ui", "should_use_web_ui", value)

    def on_volume_changed(self, event_value=None):
        value = float(self.volume_var.get())

        if self.state_manager is not None:
            self.state_manager.set_volume(value / 100)

        self.set_config_value("pepper", "volume", value)

    def on_writer_llm_changed(self, event=None):
        value = self.writer_llm_dropdown_var.get()
        self.set_config_value("writer_llm", "model", value)

    def on_judge_llm_changed(self, event=None):
        value = self.judge_llm_dropdown_var.get()
        self.set_config_value("judge_llm", "model", value)

    def on_whisper_model_changed(self, event=None):
        value = self.whisper_model_dropdown_var.get()
        self.set_config_value("speech_recognition", "model", value)

    def on_start_agent_clicked(self):
        if self.state_manager is not None:
            self.state_manager.request_agent_start()

    def on_stop_agent_clicked(self):
        if self.state_manager is not None:
            self.state_manager.request_agent_stop()

    def on_close(self):
        if self.state_manager is not None:
            self.state_manager.request_app_stop()

        if self.root is not None:
            self.root.destroy()

    # =============================================================
    # Config helpers
    # =============================================================

    def get_config_value(self, section, key, default=None):
        """
        Safe wrapper around config_controller.get_setting().
        """
        if self.config_controller is None:
            return default

        try:
            value = self.config_controller.get_setting(section, key)

            if value is None:
                return default

            return value

        except Exception:
            return default

    def get_config_list(self, section, key):
        """
        Safe wrapper for dropdown values.
        Always returns a list.
        """
        value = self.get_config_value(section, key, [])

        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]

    def set_config_value(self, section, key, value):
        """
        Safe wrapper around config writing.

        This assumes your config_controller eventually has a method like:
        set_setting(section, key, value)

        If your controller uses a different method name, adjust this one method.
        """
        if self.config_controller is None:
            return

        if hasattr(self.config_controller, "set_setting"):
            self.config_controller.set_setting(section, key, value)

        elif hasattr(self.config_controller, "update_setting"):
            self.config_controller.update_setting(section, key, value)

        elif hasattr(self.config_controller, "set_value"):
            self.config_controller.set_value(section, key, value)