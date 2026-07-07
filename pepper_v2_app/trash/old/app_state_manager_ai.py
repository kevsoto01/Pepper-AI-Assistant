from ...app.controls import keyboard


class AppStateManager:
    """
    Central app state manager.

    This class coordinates:
    - config values
    - keyboard requests
    - local UI requests
    - web UI requests
    - Pepper start/stop
    - agent start/stop
    - status forwarding

    This class should NOT:
    - build Tkinter widgets
    - directly render web UI elements
    - contain agent logic
    - contain Pepper robot logic
    """

    def __init__(
            self,
            config_controller,
            web_ui_controller,
            local_ui_controller,
            pepper_controller,
            agent_controller
            ):

        print("App state manager loaded")

        self.config_controller = config_controller
        self.web_ui = web_ui_controller
        self.local_ui = local_ui_controller
        self.pepper = pepper_controller
        self.agent_controller = agent_controller

        # App lifecycle
        self.start_app_requested = False
        self.stop_app_requested = False

        # Agent lifecycle
        self.start_agent_requested = False
        self.stop_agent_requested = False
        self.is_agent_running = False
        self.is_agent_loaded = False

        # Runtime config defaults
        self.should_use_pepper = False
        self.should_use_web_ui = False

        # Keybind defaults
        self.exit_key = "esc"
        self.listen_key = "space"
        self.stop_key = "q"

        # Config comparison
        self.last_config = {}

        # Load config immediately
        self.update_variables_from_config()
        self.last_config = self.get_current_config_snapshot()

    # =============================================================
    # App lifecycle
    # =============================================================

    def request_start_app(self):
        self.start_app_requested = True
        self.stop_app_requested = False

    def request_stop_app(self):
        self.stop_app_requested = True
        self.start_app_requested = False
        self.stop_agent_requested = True
        self.start_agent_requested = False

    def consume_start_app_request(self) -> bool:
        value = self.start_app_requested
        self.start_app_requested = False
        return value

    def consume_stop_app_request(self) -> bool:
        return bool(self.stop_app_requested)

    def app_is_stopping(self) -> bool:
        return bool(self.stop_app_requested)

    def start(self):
        """
        Starts app-level services.
        """

        self.update_variables_from_config()

        self.start_web_ui()
        self.start_pepper()

        self.start_app_requested = False
        self.stop_app_requested = False

        self.set_idle()

    def shutdown(self):
        """
        Stops app-level services safely.
        """

        if self.is_agent_running:
            self.stop_agent_running()

        self.stop_pepper()

        if self.web_ui is not None and self.should_use_web_ui:
            if hasattr(self.web_ui, "stop"):
                self.web_ui.stop()

        self.stop_app_requested = True

    def on_window_close(self):
        self.request_stop_app()

    # =============================================================
    # Agent lifecycle
    # =============================================================

    def request_start_agent(self):
        if self.is_agent_running:
            return

        self.start_agent_requested = True
        self.stop_agent_requested = False

    def request_stop_agent(self):
        self.stop_agent_requested = True
        self.start_agent_requested = False

    def consume_start_agent_request(self) -> bool:
        value = self.start_agent_requested
        self.start_agent_requested = False
        return value

    def consume_stop_agent_request(self) -> bool:
        value = self.stop_agent_requested
        self.stop_agent_requested = False
        return value

    def load_agent(self):
        if self.is_agent_loaded:
            return

        if self.agent_controller is not None:
            self.agent_controller.load()

        self.is_agent_loaded = True

    def start_agent(self):
        if self.is_agent_running:
            return

        self.load_agent()

        if self.agent_controller is not None:
            self.agent_controller.start()

        self.is_agent_running = True

        if self.local_ui is not None:
            self.local_ui.set_agent_running(True)

        self.set_idle()

    def stop_agent(self):
        """
        Request the agent to stop.

        This does not directly stop the agent immediately.
        The main update loop consumes the request.
        """
        self.request_stop_agent()

    def stop_agent_running(self):
        """
        Actually stops the agent.
        """

        if not self.is_agent_running:
            return

        if self.agent_controller is not None:
            self.agent_controller.stop()

        self.is_agent_running = False

        if self.local_ui is not None:
            self.local_ui.set_agent_running(False)

        self.set_idle()

    def set_agent_running(self, value: bool):
        self.is_agent_running = bool(value)

        if self.local_ui is not None:
            self.local_ui.set_agent_running(value)

    # =============================================================
    # Keyboard checks
    # =============================================================

    def check_keyboard_requests(self):
        """
        Reads keyboard shortcuts and converts them into app/agent requests.
        """

        if self.exit_key and keyboard.is_key_pressed(self.exit_key):
            self.request_stop_app()

        if self.listen_key and keyboard.is_key_pressed(self.listen_key):
            self.request_start_agent()

        if self.stop_key and keyboard.is_key_pressed(self.stop_key):
            self.request_stop_agent()

    # =============================================================
    # Local UI checks
    # =============================================================

    def check_local_ui_requests(self):
        """
        Pulls one-shot requests from LocalUIController.
        """

        if self.local_ui is None:
            return

        if self.local_ui.should_start_agent():
            self.request_start_agent()

        if self.local_ui.should_stop_agent():
            self.request_stop_agent()

        if self.local_ui.should_stop_app():
            self.request_stop_app()

    # =============================================================
    # Main update loop
    # =============================================================

    def update(self):
        """
        Main app state tick.

        Call this repeatedly from your main loop.
        """

        self.check_keyboard_requests()
        self.check_local_ui_requests()
        self.update_config_from_local_ui()

        if self.consume_start_agent_request():
            self.start_agent()

        if self.consume_stop_agent_request():
            self.stop_agent_running()

    # =============================================================
    # Config
    # =============================================================

    def update_variables_from_config(self):
        """
        Loads app variables from ConfigController.
        """

        # Start conditions
        self.should_use_pepper = self.get_config_value(
            "pepper",
            "should_use",
            False
        )

        self.should_use_web_ui = self.get_config_value(
            "web_ui",
            "use_ui",
            False
        )

        # Keybinds
        self.exit_key = self.get_config_value(
            "keybinds",
            "exit_key",
            "esc"
        )

        self.listen_key = self.get_config_value(
            "keybinds",
            "listen_key",
            "space"
        )

        self.stop_key = self.get_config_value(
            "keybinds",
            "stop_key",
            "q"
        )

    def update_config_from_local_ui(self):
        """
        Pulls config values from LocalUIController and writes them
        to ConfigController if changed.
        """

        if self.local_ui is None:
            return

        if not hasattr(self.local_ui, "get_current_ui_config"):
            return

        current_config = self.local_ui.get_current_ui_config()

        if current_config != self.last_config:
            self.write_config(current_config)
            self.last_config = current_config
            self.update_variables_from_config()

    def refresh_config(self):
        self.update_variables_from_config()

    def get_config_value(self, section, key, default=None):
        if self.config_controller is None:
            return default

        try:
            value = self.config_controller.get_setting(section, key)

            if value is None:
                return default

            return value

        except Exception:
            return default

    def write_config(self, config_data: dict):
        if self.config_controller is None:
            return

        if hasattr(self.config_controller, "update_config"):
            self.config_controller.update_config(config_data)

        elif hasattr(self.config_controller, "save"):
            self.config_controller.save(config_data)

        elif hasattr(self.config_controller, "save_config"):
            self.config_controller.save_config(config_data)

        elif hasattr(self.config_controller, "write_config"):
            self.config_controller.write_config(config_data)

    def get_current_config_snapshot(self) -> dict:
        return {
            "should_use_pepper": self.should_use_pepper,
            "should_use_web_ui": self.should_use_web_ui,
            "exit_key": self.exit_key,
            "listen_key": self.listen_key,
            "stop_key": self.stop_key,
        }

    # =============================================================
    # Feature flags
    # =============================================================

    def get_should_use_web_ui(self) -> bool:
        return bool(self.should_use_web_ui)

    def get_should_use_pepper(self) -> bool:
        return bool(self.should_use_pepper)

    # =============================================================
    # Local UI / Web UI startup
    # =============================================================

    def start_local_ui(self):
        if self.local_ui is not None:
            self.local_ui.run()

    def start_web_ui(self):
        if not self.should_use_web_ui:
            return

        if self.web_ui is not None:
            if hasattr(self.web_ui, "load"):
                self.web_ui.load()
            elif hasattr(self.web_ui, "start"):
                self.web_ui.start()

    # =============================================================
    # Pepper lifecycle
    # =============================================================

    def start_pepper(self):
        if not self.should_use_pepper:
            return

        if self.pepper is not None:
            self.pepper.start()

    def stop_pepper(self):
        if not self.should_use_pepper:
            return

        if self.pepper is not None:
            self.pepper.stop()

    # =============================================================
    # Status helpers
    # =============================================================

    def set_loading(self):
        if self.local_ui is not None:
            self.local_ui.set_agent_loading()

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_loading"):
                self.web_ui.set_loading()

    def set_idle(self):
        if self.local_ui is not None:
            self.local_ui.set_agent_idle()

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_idle"):
                self.web_ui.set_idle()

    def set_listening(self):
        if self.local_ui is not None:
            self.local_ui.set_agent_listening()

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_listening"):
                self.web_ui.set_listening()

    def set_thinking(self):
        if self.local_ui is not None:
            self.local_ui.set_agent_thinking()

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_thinking"):
                self.web_ui.set_thinking()

    def set_speaking(self):
        if self.local_ui is not None:
            self.local_ui.set_agent_speaking()

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_speaking"):
                self.web_ui.set_speaking()

    def set_disconnected(self):
        if self.local_ui is not None:
            self.local_ui.set_agent_disconnected()

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_disconnected"):
                self.web_ui.set_disconnected()

    def set_error(self, message: str):
        if self.local_ui is not None:
            self.local_ui.set_agent_error(message)

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_error"):
                self.web_ui.set_error(message)

    def set_status(self, status: str):
        status_methods = {
            "idle": self.set_idle,
            "loading": self.set_loading,
            "listening": self.set_listening,
            "thinking": self.set_thinking,
            "speaking": self.set_speaking,
            "disconnected": self.set_disconnected,
            "error": lambda: self.set_error("Unknown error"),
        }

        method = status_methods.get(status)

        if method is None:
            raise ValueError(f"Invalid status: {status}")

        method()

    # =============================================================
    # Conversation display helpers
    # =============================================================

    def update_heard_text(self, text: str):
        if self.local_ui is not None:
            self.local_ui.set_heard_text(text)

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_heard_text"):
                self.web_ui.set_heard_text(text)

    def update_reply_text(self, text: str):
        if self.local_ui is not None:
            self.local_ui.set_reply_text(text)

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "set_reply_text"):
                self.web_ui.set_reply_text(text)

    def clear_conversation_display(self):
        if self.local_ui is not None:
            self.local_ui.clear_conversation_display()

        if self.should_use_web_ui and self.web_ui is not None:
            if hasattr(self.web_ui, "clear_conversation_display"):
                self.web_ui.clear_conversation_display()

    # =============================================================
    # Manual text input
    # =============================================================

    def get_manual_input(self):
        if self.local_ui is None:
            return None

        if hasattr(self.local_ui, "get_manual_input"):
            return self.local_ui.get_manual_input()

        return None

    def process_manual_input_if_available(self):
        manual_text = self.get_manual_input()

        if not manual_text:
            return

        if self.agent_controller is not None:
            if hasattr(self.agent_controller, "handle_manual_input"):
                self.agent_controller.handle_manual_input(manual_text)

    # =============================================================
    # Debug helpers
    # =============================================================

    def get_runtime_state_snapshot(self) -> dict:
        return {
            "app": {
                "start_app_requested": self.start_app_requested,
                "stop_app_requested": self.stop_app_requested,
            },
            "agent": {
                "start_agent_requested": self.start_agent_requested,
                "stop_agent_requested": self.stop_agent_requested,
                "is_agent_running": self.is_agent_running,
                "is_agent_loaded": self.is_agent_loaded,
            },
            "features": {
                "should_use_pepper": self.should_use_pepper,
                "should_use_web_ui": self.should_use_web_ui,
            },
            "keybinds": {
                "exit_key": self.exit_key,
                "listen_key": self.listen_key,
                "stop_key": self.stop_key,
            },
        }