from threading import RLock
from copy import deepcopy


class LocalUIStateManager:
    """
    Owns UI-facing state for the Pepper app.

    This class does NOT:
    - render Tkinter widgets
    - render HTML
    - start the AI agent directly
    - stop the AI agent directly
    - talk to Pepper directly
    - write config.json directly

    It only tracks state and exposes clean methods for controllers
    to read, update, and consume state changes.
    """

    VALID_AGENT_STATUSES = {
        "idle",
        "listening",
        "thinking",
        "speaking",
        "loading",
        "disconnected",
        "error",
        "stopped",
    }

    def __init__(self):
        print("Local UI state manager loaded")

        self._lock = RLock()

        # ---------------------------------------------------------
        # UI / feature toggles
        # ---------------------------------------------------------
        self.should_use_pepper = False
        self.should_use_web_ui = False

        # ---------------------------------------------------------
        # Agent lifecycle state
        # ---------------------------------------------------------
        self.should_start_agent = False
        self.should_stop_agent = False
        self.is_agent_running = False

        # ---------------------------------------------------------
        # App lifecycle state
        # ---------------------------------------------------------
        self.should_stop_app = False

        # ---------------------------------------------------------
        # UI display state
        # ---------------------------------------------------------
        self.agent_status = "idle"
        self.heard_text = ""
        self.reply_text = ""
        self.error_message = ""

        # ---------------------------------------------------------
        # UI interaction state
        # ---------------------------------------------------------
        self.manual_user_input = ""
        self.should_send_manual_input = False

        # ---------------------------------------------------------
        # Settings state
        # ---------------------------------------------------------
        self.dark_mode = False
        self.volume = 1.0

        # ---------------------------------------------------------
        # Dirty flags
        # Useful when another controller needs to know whether
        # config/state changed and should be written somewhere.
        # ---------------------------------------------------------
        self.has_ui_state_changed = False
        self.has_config_changed = False

    # =============================================================
    # Feature toggles
    # =============================================================

    def set_use_pepper(self, value: bool):
        with self._lock:
            self.should_use_pepper = value
            self.has_config_changed = True

    def set_use_web_ui(self, value: bool):
        with self._lock:
            self.should_use_web_ui = bool(value)
            self.has_config_changed = True

    def get_feature_flags(self) -> dict:
        with self._lock:
            return {
                "should_use_pepper": self.should_use_pepper,
                "should_use_web_ui": self.should_use_web_ui,
            }

    # =============================================================
    # Agent lifecycle requests
    # =============================================================

    def request_agent_start(self):
        """
        Called by the UI when the user clicks "Start Agent"
        """
        with self._lock:
            self.should_start_agent = True
            self.should_stop_agent = False
            self.has_ui_state_changed = True

    def request_agent_stop(self):
        """
        Called by the UI when the user clicks "Stop Agent"
        """
        with self._lock:
            self.should_stop_agent = True
            self.should_start_agent = False
            self.has_ui_state_changed = True

    def consume_agent_start_request(self) -> bool:
        """
        One-shot read.

        The app loop should call this.
        If True, the app loop starts the agent worker thread.
        """
        with self._lock:
            value = self.should_start_agent
            self.should_start_agent = False
            return value

    def consume_agent_stop_request(self) -> bool:
        """
        One-shot read.

        The app loop should call this.
        If True, the app loop stops the agent worker thread.
        """
        with self._lock:
            value = self.should_stop_agent
            self.should_stop_agent = False
            return value

    def set_agent_running(self, value: bool):
        with self._lock:
            self.is_agent_running = bool(value)

            if self.is_agent_running:
                self.agent_status = "idle"
            else:
                self.agent_status = "stopped"

            self.has_ui_state_changed = True

    # =============================================================
    # App lifecycle
    # =============================================================

    def request_app_stop(self):
        """
        Called when the user closes the UI or clicks Exit.
        """
        with self._lock:
            self.should_stop_app = True
            self.should_stop_agent = True
            self.should_start_agent = False
            self.has_ui_state_changed = True

    def consume_app_stop_request(self) -> bool:
        """
        One-shot read.

        The main app loop should call this.
        """
        with self._lock:
            value = self.should_stop_app
            return value

    # =============================================================
    # Agent status / UI display state
    # =============================================================

    def set_agent_status(self, status: str):
        if status not in self.VALID_AGENT_STATUSES:
            raise ValueError(
                f"Invalid agent status: {status}. "
                f"Expected one of: {sorted(self.VALID_AGENT_STATUSES)}"
            )

        with self._lock:
            self.agent_status = status
            self.has_ui_state_changed = True

    def set_idle(self):
        self.set_agent_status("idle")

    def set_listening(self):
        self.set_agent_status("listening")

    def set_thinking(self):
        self.set_agent_status("thinking")

    def set_speaking(self):
        self.set_agent_status("speaking")

    def set_loading(self):
        self.set_agent_status("loading")

    def set_disconnected(self):
        self.set_agent_status("disconnected")

    def set_error(self, message: str):
        with self._lock:
            self.agent_status = "error"
            self.error_message = message
            self.has_ui_state_changed = True

    def clear_error(self):
        with self._lock:
            self.error_message = ""
            self.has_ui_state_changed = True

    # =============================================================
    # Heard / reply text
    # =============================================================

    def set_heard_text(self, text: str):
        with self._lock:
            self.heard_text = text or ""
            self.has_ui_state_changed = True

    def set_reply_text(self, text: str):
        with self._lock:
            self.reply_text = text or ""
            self.has_ui_state_changed = True

    def clear_conversation_display(self):
        with self._lock:
            self.heard_text = ""
            self.reply_text = ""
            self.error_message = ""
            self.has_ui_state_changed = True

    # =============================================================
    # Manual user input
    # =============================================================

    def set_manual_user_input(self, text: str):
        with self._lock:
            self.manual_user_input = text or ""
            self.has_ui_state_changed = True

    def request_send_manual_input(self, text: str = ""):
        """
        Called when the user types into the UI and clicks Send.
        """
        with self._lock:
            if text:
                self.manual_user_input = text

            self.should_send_manual_input = True
            self.has_ui_state_changed = True

    def consume_manual_input_request(self) -> str | None:
        """
        One-shot read.

        Returns the manual input text once, then clears the request.
        """
        with self._lock:
            if not self.should_send_manual_input:
                return None

            text = self.manual_user_input

            self.should_send_manual_input = False
            self.manual_user_input = ""

            return text

    # =============================================================
    # Settings
    # =============================================================

    def set_dark_mode(self, value: bool):
        with self._lock:
            self.dark_mode = bool(value)
            self.has_ui_state_changed = True
            self.has_config_changed = True

    def toggle_dark_mode(self) -> bool:
        with self._lock:
            self.dark_mode = not self.dark_mode
            self.has_ui_state_changed = True
            self.has_config_changed = True
            return self.dark_mode

    def set_volume(self, value: float):
        """
        Keeps volume between 0.0 and 1.0.
        """
        with self._lock:
            value = float(value)
            value = max(0.0, min(1.0, value))

            self.volume = value
            self.has_ui_state_changed = True
            self.has_config_changed = True

    # =============================================================
    # Snapshots
    # =============================================================

    def get_ui_state(self) -> dict:
        """
        Used by:
        - Tkinter UI
        - web UI / state.json
        - Flask /state route

        This should be safe to serialize.
        """
        with self._lock:
            return {
                "agent_status": self.agent_status,
                "is_agent_running": self.is_agent_running,
                "heard_text": self.heard_text,
                "reply_text": self.reply_text,
                "error_message": self.error_message,
                "manual_user_input": self.manual_user_input,
                "dark_mode": self.dark_mode,
                "volume": self.volume,
                "should_use_pepper": self.should_use_pepper,
                "should_use_web_ui": self.should_use_web_ui,
            }

    def get_config_state(self) -> dict:
        """
        Used by ConfigController when writing config.json.

        Keep this separate from get_ui_state because config.json
        should not necessarily store temporary UI text like heard/reply.
        """
        with self._lock:
            return {
                "should_use_pepper": self.should_use_pepper,
                "should_use_web_ui": self.should_use_web_ui,
                "dark_mode": self.dark_mode,
                "volume": self.volume,
            }

    def get_full_state(self) -> dict:
        """
        Debugging snapshot.
        """
        with self._lock:
            return deepcopy({
                "features": self.get_feature_flags(),
                "agent": {
                    "should_start_agent": self.should_start_agent,
                    "should_stop_agent": self.should_stop_agent,
                    "is_agent_running": self.is_agent_running,
                    "agent_status": self.agent_status,
                },
                "app": {
                    "should_stop_app": self.should_stop_app,
                },
                "display": {
                    "heard_text": self.heard_text,
                    "reply_text": self.reply_text,
                    "error_message": self.error_message,
                },
                "manual_input": {
                    "manual_user_input": self.manual_user_input,
                    "should_send_manual_input": self.should_send_manual_input,
                },
                "settings": {
                    "dark_mode": self.dark_mode,
                    "volume": self.volume,
                },
                "dirty_flags": {
                    "has_ui_state_changed": self.has_ui_state_changed,
                    "has_config_changed": self.has_config_changed,
                },
            })

    # =============================================================
    # Dirty flag handling
    # =============================================================

    def consume_ui_state_changed(self) -> bool:
        """
        One-shot read.

        Useful for deciding whether to re-render local UI,
        update state.json, or push state to web UI.
        """
        with self._lock:
            value = self.has_ui_state_changed
            self.has_ui_state_changed = False
            return value

    def consume_config_changed(self) -> bool:
        """
        One-shot read.

        Useful for deciding whether ConfigController should write config.json.
        """
        with self._lock:
            value = self.has_config_changed
            self.has_config_changed = False
            return value

    # =============================================================
    # Reset helpers
    # =============================================================

    def reset_agent_requests(self):
        with self._lock:
            self.should_start_agent = False
            self.should_stop_agent = False
            self.should_send_manual_input = False

    def reset_ui_runtime_state(self):
        """
        Clears temporary UI display state without changing config settings.
        """
        with self._lock:
            self.agent_status = "idle"
            self.heard_text = ""
            self.reply_text = ""
            self.error_message = ""
            self.manual_user_input = ""
            self.should_send_manual_input = False
            self.has_ui_state_changed = True

    def reset_all(self):
        """
        Full reset to default startup state.
        """
        with self._lock:
            self.should_use_pepper = False
            self.should_use_web_ui = False

            self.should_start_agent = False
            self.should_stop_agent = False
            self.is_agent_running = False

            self.should_stop_app = False

            self.agent_status = "idle"
            self.heard_text = ""
            self.reply_text = ""
            self.error_message = ""

            self.manual_user_input = ""
            self.should_send_manual_input = False

            self.dark_mode = False
            self.volume = 1.0

            self.has_ui_state_changed = True
            self.has_config_changed = True