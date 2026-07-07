import tkinter as tk
from copy import deepcopy
from typing import Any


class LocalUIController:
    def __init__(self, rendering_manager):
        self.renderer = rendering_manager
        self.renderer.set_controller(self)

        self.root = self.renderer.root
        self.ui_state: dict[str, tk.Variable] = {}

        # "ui_state_var": ("app_state_group", "app_state_key")
        self.ui_to_config_translator = {
            "use_pepper_var": ("general", "use_pepper"),
            "pepper_volume_var": ("general", "pepper_volume"),
            "use_web_ui_var": ("general", "use_web_ui"),

            "writer_model_var": ("writer_llm", "model"),
            "judge_model_var": ("judge_llm", "model"),
            "whisper_model_var": ("speech_recognition", "model"),

            "show_launcher_var": ("local_ui", "show_launcher"),
            "show_control_panel_var": ("local_ui", "show_control_panel"),
        }

    # ------------------------------------------------------------------
    # Tk state helpers
    # ------------------------------------------------------------------
    def get_ui_state(self) -> dict[str, tk.Variable]:
        if self.ui_state:
            return self.ui_state

        self.ui_state = {
            "use_pepper_var": tk.BooleanVar(master=self.root, value=False),
            "pepper_volume_var": tk.IntVar(master=self.root, value=50),
            "use_web_ui_var": tk.BooleanVar(master=self.root, value=False),
            "use_llm_filter_var": tk.BooleanVar(master=self.root, value=True),

            "writer_model_var": tk.StringVar(master=self.root, value=""),
            "judge_model_var": tk.StringVar(master=self.root, value=""),
            "whisper_model_var": tk.StringVar(master=self.root, value=""),

            "show_launcher_var": tk.BooleanVar(master=self.root, value=True),
            "show_control_panel_var": tk.BooleanVar(master=self.root, value=False),

        }

        return self.ui_state

    def get_var(self, key: str) -> Any:
        state = self.get_ui_state()

        if key not in state:
            raise KeyError(f"Unknown UI state variable: {key}")

        return state[key].get()

    def set_var(self, key: str, value: Any) -> None:
        state = self.get_ui_state()

        if key not in state:
            raise KeyError(f"Unknown UI state variable: {key}")

        state[key].set(value)

    # ------------------------------------------------------------------
    # App lifecycle
    # ------------------------------------------------------------------
    def start(self) -> None:
        self.get_ui_state()
        self.renderer.create_window()

    def stop(self):
        self.renderer.close_window()

    def set_callbacks(
            self,
            on_start_agent_request=None,
            on_stop_agent_request=None,
            on_close_app_request=None,
            on_sing_happy_birthday_request=None,
            on_change_volume_request=None
    ):
        if (
            on_start_agent_request is None
            or on_stop_agent_request is None
            or on_close_app_request is None
            or on_sing_happy_birthday_request is None
            or on_change_volume_request is None
        ):
            raise Exception("App callbacks not set")
        
        self.on_start_agent_callback = on_start_agent_request
        self.on_stop_agent_callback = on_stop_agent_request
        self.on_close_app_callback = on_close_app_request
        self.on_sing_happy_birthday_callback = on_sing_happy_birthday_request
        self.on_change_volume_callback = on_change_volume_request
        
    def on_start_agent_request(self) -> None:
        self.on_start_agent_callback()
        self.set_var("show_launcher_var", False)
        self.set_var("show_control_panel_var", True)
        self.renderer.render_control_panel()

    def on_stop_agent_request(self) -> None:
        self.on_stop_agent_callback()
        self.set_var("show_launcher_var", True)
        self.set_var("show_control_panel_var", False)
        self.renderer.render_launcher()

    def on_close_app_request(self) -> None:
        self.on_close_app_callback()
        self.renderer.close_window()

    def on_sing_happy_birthday_request(self) -> None:
        self.on_sing_happy_birthday_callback()

    def on_change_volume_request(self, _) -> None:
        volume = self.get_ui_state()["pepper_volume_var"].get()
        self.on_change_volume_callback(volume)

    def on_set_filter_request(self, _) -> None:
        # value = self.get_ui_state()["use_llm_filter_var"].get()
        # self.on_set_filter_callback(value)
        print("Placeholder.")
    # ------------------------------------------------------------------
    # UI state -> App state
    # ------------------------------------------------------------------
    def update_appstate_from_uistate(
        self,
        current_app_state: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, dict[str, Any]]:
        app_state = deepcopy(current_app_state) if current_app_state else {}

        for ui_key, app_path in self.ui_to_appstate_translator.items():
            group, app_key = app_path

            if group not in app_state:
                app_state[group] = {}

            app_state[group][app_key] = self.get_var(ui_key)

        return app_state

    # ------------------------------------------------------------------
    # App state -> UI state
    # ------------------------------------------------------------------
    def update_uistate_from_appstate(
        self,
        app_state: dict[str, dict[str, Any]],
    ) -> None:
        self.get_ui_state()

        for ui_key, app_path in self.ui_to_appstate_translator.items():
            group, app_key = app_path

            if group in app_state and app_key in app_state[group]:
                self.set_var(ui_key, app_state[group][app_key])