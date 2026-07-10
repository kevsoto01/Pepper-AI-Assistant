import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from .local_ui_templates import LocalUIElementTemplateBuilder


class LocalUIRenderer:
    def __init__(self, llm_options=None, sr_options=None):
        self.root = tk.Tk()
        self.root.withdraw()

        self.controller = None
        self.content_frame = None
        self.template = None

        self.llm_options = list(llm_options or [])
        self.sr_options = list(sr_options or [])

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def set_controller(self, controller):
        self.controller = controller

    def set_options(self, llm_options=None, sr_options=None):
        if llm_options is not None:
            self.llm_options = list(llm_options)

        if sr_options is not None:
            self.sr_options = list(sr_options)

    def create_window(self, geometry: str = ""):
        self.configure_styles()
        self.root.title("Pepper Launcher")

        if geometry:
            self.root.geometry(geometry)

        if self.controller is not None:
            self.root.protocol(
                "WM_DELETE_WINDOW",
                self.controller.on_close_app_request,
            )

        self.render_launcher()

        self.root.deiconify()
        self.root.lift()
        self.root.mainloop()

    def render_launcher(self):
        self.clear_widgets()
        self.build_launcher_widgets()

    def render_control_panel(self):
        self.clear_widgets()
        self.build_panel_widgets()

    def close_window(self):
        self.root.destroy()

    # ------------------------------------------------------------------
    # State access
    # ------------------------------------------------------------------
    def get_state_vars(self):
        if self.controller is None:
            raise RuntimeError("LocalUIRenderer has no controller.")

        return self.controller.get_ui_state()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def _create_content_frame(self):
        self.content_frame = ttk.Frame(self.root, padding=20)
        self.content_frame.pack(fill="both", expand=True)

        self.template = LocalUIElementTemplateBuilder(self.content_frame)

    def _pack(self, widget, **pack_options):
        defaults = {
            "anchor": "w",
            "fill": "x",
            "pady": 4,
        }

        defaults.update(pack_options)

        clean_options = {
            key: value
            for key, value in defaults.items()
            if value is not None
        }

        widget.pack(**clean_options)
        return widget

    def _add_labeled_combobox(self, label_text, values, variable):
        self._pack(
            self.template.label(text=label_text),
            pady=(10, 2),
        )

        return self._pack(
            self.template.combobox(
                values=values,
                variable=variable,
                width=44,
                default_to_first=True,
            )
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def build_launcher_widgets(self):
        self._create_content_frame()

        state_vars = self.get_state_vars()

        self.launcher_title = self._pack(
            self.template.title_label(text="Pepper Launcher"),
            pady=(0, 12),
        )

        self.use_pepper_checkbox = self._pack(
            self.template.checkbutton(
                text="Connect to Pepper robot",
                variable=state_vars["use_pepper_var"],
            )
        )

        self.local_audio_checkbox = self._pack(
            self.template.checkbutton(
                text="Play audio locally (only if using Pepper)",
                variable=state_vars["use_local_audio_var"],
            )
        )

        self.use_web_ui_checkbox = self._pack(
            self.template.checkbutton(
                text="Use web UI",
                variable=state_vars["use_web_ui_var"],
            )
        )

        self.use_llm_filter_checkbox = self._pack(
            self.template.checkbutton(
                text="Use AI-powered content safety filter (recommended)",
                variable=state_vars["use_llm_filter_var"],
            )
        )

        self.whisper_model_combobox = self._add_labeled_combobox(
            "Speech Recognition Model",
            self.sr_options,
            state_vars["whisper_model_var"],
        )

        self.writer_model_combobox = self._add_labeled_combobox(
            "Writer LLM Model",
            self.llm_options,
            state_vars["writer_model_var"],
        )

        self.judge_model_combobox = self._add_labeled_combobox(
            "Judge LLM Model",
            self.llm_options,
            state_vars["judge_model_var"],
        )
        
        self.llm_model_warning = self._pack(
            self.template.label(
                text="Warning: writer and judge LLMs should be different for proper functionality",
                foreground="red",
                font=tkfont.nametofont("TkDefaultFont").copy().configure(size=2)
            )
        )

        

        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill="x", pady=(16, 0))

        button_template = LocalUIElementTemplateBuilder(button_frame)

        self.start_agent_button = button_template.button(
            text="Start Agent",
            command=self.controller.on_start_agent_request,
        )
        self.start_agent_button.pack(side="left", padx=(0, 8))

        self.close_app_button = button_template.button(
            text="Close App",
            command=self.controller.on_close_app_request,
        )
        self.close_app_button.pack(side="left", padx=(0, 8))

        self.sing_button = button_template.button(
            text="Sing Happy Birthday",
            command=self.controller.on_sing_happy_birthday_request,
        )
        self.sing_button.pack(side="left")

    def build_panel_widgets(self):
        self._create_content_frame()

        state_vars = self.get_state_vars()

        self.panel_title = self._pack(
            self.template.title_label(text="Pepper Control Panel"),
            pady=(0, 12),
        )

        if state_vars["use_pepper_var"].get():
            self.pepper_volume_slider_label = self._pack(
                self.template.label(text="Pepper Volume:"),
                pady=(8, 2),
            )

            self.pepper_volume_slider = self._pack(
                self.template.horizontal_slider(
                    from_=0,
                    to=100,
                    variable=state_vars["pepper_volume_var"],
                    # command=self.controller.on_change_volume_request
                )
            )

            # self.pepper_volume_slider.bind(
            #     "<ButtonRelease-1>",
            #     self.controller.on_change_volume_request
            # )

        self.stop_agent_button = self._pack(
            self.template.button(
                text="Stop Agent",
                command=self.controller.on_stop_agent_request,
            ),
            fill=None,
            pady=(16, 0),
        )

    # ------------------------------------------------------------------
    # Cleanup / styles
    # ------------------------------------------------------------------
    def clear_widgets(self):
        if self.content_frame is not None:
            self.content_frame.destroy()
            self.content_frame = None
            self.template = None

    def configure_styles(self):
        style = ttk.Style()

        self.large_font = tkfont.nametofont("TkDefaultFont").copy()
        self.large_font.configure(size=14)

        self.small_font = tkfont.nametofont("TkDefaultFont").copy()
        self.small_font.configure(size=12)

        style.configure("TLabel", font=self.large_font)
        style.configure("TButton", font=self.small_font)
        style.configure("TCheckbutton", font=self.small_font)
        style.configure("TCombobox", font=self.small_font)