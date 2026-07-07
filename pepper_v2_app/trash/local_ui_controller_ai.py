class LocalUIController:
    """
    Coordinates the local Tkinter UI.

    This class connects:
    - LocalUIStateManager
    - LocalUIRenderingManager
    - ConfigController

    It should NOT:
    - create individual Tkinter widgets directly
    - run the AI agent directly
    - talk to Pepper directly
    - contain LLM logic directly

    It should:
    - initialize the rendering manager
    - start the local UI
    - expose clean methods for the main app loop
    - sync state/config when needed
    """

    def __init__(self, state_manager, rendering_manager, config_controller):
        print("Local UI controller loaded")

        self.state_manager = state_manager
        self.rendering_manager = rendering_manager
        self.config_controller = config_controller

        self.is_ui_built = False
        self.is_ui_running = False

        self.refresh_interval_ms = 250

    # =============================================================
    # Setup
    # =============================================================

    def build_ui(self):
        """
        Builds the local UI window.

        This delegates actual Tkinter rendering to LocalUIRenderingManager.
        """
        self.inject_dependencies_into_rendering_manager()

        self.rendering_manager.build_ui()

        self.is_ui_built = True

    def inject_dependencies_into_rendering_manager(self):
        """
        Makes sure the rendering manager has access to the same managers
        used by this controller.

        This is useful if rendering_manager was created before the
        state_manager or config_controller was available.
        """
        self.rendering_manager.state_manager = self.state_manager
        self.rendering_manager.config_controller = self.config_controller

    def run(self):
        """
        Starts the Tkinter UI.

        This should usually be called from main.py.
        """
        if not self.is_ui_built:
            self.build_ui()

        self.is_ui_running = True

        self.start_ui_refresh_loop()

        self.rendering_manager.root.mainloop()

    # =============================================================
    # UI refresh
    # =============================================================

    def start_ui_refresh_loop(self):
        """
        Starts repeated UI refreshes.

        Uses Tkinter's .after() so it does not block the UI.
        """
        root = self.get_root()

        if root is None:
            return

        self.refresh_ui_once()

        root.after(self.refresh_interval_ms, self.start_ui_refresh_loop)

    def refresh_ui_once(self):
        """
        Updates visible widgets from the current state manager values.
        """
        if self.rendering_manager is None:
            return

        self.rendering_manager.refresh_from_state()

        self.update_control_states()

    def update_control_states(self):
        """
        Enables/disables buttons based on current agent state.
        """
        if self.state_manager is None:
            return

        ui_state = self.state_manager.get_ui_state()

        is_agent_running = ui_state.get("is_agent_running", False)

        start_button = getattr(self.rendering_manager, "start_agent_button", None)
        stop_button = getattr(self.rendering_manager, "stop_agent_button", None)

        if start_button is not None:
            if is_agent_running:
                start_button.config(state="disabled")
            else:
                start_button.config(state="normal")

        if stop_button is not None:
            if is_agent_running:
                stop_button.config(state="normal")
            else:
                stop_button.config(state="disabled")

    # =============================================================
    # State request helpers
    # =============================================================

    def should_start_agent(self) -> bool:
        """
        Called by the main app loop.

        Returns True once when the UI requested the agent to start.
        """
        return self.state_manager.consume_agent_start_request()

    def should_stop_agent(self) -> bool:
        """
        Called by the main app loop.

        Returns True once when the UI requested the agent to stop.
        """
        return self.state_manager.consume_agent_stop_request()

    def should_stop_app(self) -> bool:
        """
        Called by the main app loop.

        Returns True if the UI requested the app to close.
        """
        return self.state_manager.consume_app_stop_request()

    def get_manual_input(self):
        """
        Returns manual user input once, then clears it.

        The main app loop can pass this text into the AI agent.
        """
        return self.state_manager.consume_manual_input_request()

    # =============================================================
    # Agent state updates
    # =============================================================

    def set_agent_running(self, value: bool):
        self.state_manager.set_agent_running(value)

    def set_agent_idle(self):
        self.state_manager.set_idle()

    def set_agent_listening(self):
        self.state_manager.set_listening()

    def set_agent_thinking(self):
        self.state_manager.set_thinking()

    def set_agent_speaking(self):
        self.state_manager.set_speaking()

    def set_agent_loading(self):
        self.state_manager.set_loading()

    def set_agent_disconnected(self):
        self.state_manager.set_disconnected()

    def set_agent_error(self, message: str):
        self.state_manager.set_error(message)

    # =============================================================
    # Conversation display updates
    # =============================================================

    def set_heard_text(self, text: str):
        self.state_manager.set_heard_text(text)

    def set_reply_text(self, text: str):
        self.state_manager.set_reply_text(text)

    def clear_conversation_display(self):
        self.state_manager.clear_conversation_display()

    # =============================================================
    # Config syncing
    # =============================================================

    def save_config_if_changed(self):
        """
        Called by the main app loop.

        If UI settings changed, save current config state.
        """
        if self.state_manager is None:
            return

        if self.config_controller is None:
            return

        did_config_change = self.state_manager.consume_config_changed()

        if not did_config_change:
            return

        config_state = self.state_manager.get_config_state()

        if hasattr(self.config_controller, "save"):
            self.config_controller.save(config_state)

        elif hasattr(self.config_controller, "save_config"):
            self.config_controller.save_config(config_state)

        elif hasattr(self.config_controller, "write_config"):
            self.config_controller.write_config(config_state)

    def get_current_ui_config(self) -> dict:
        """
        Returns UI-related config values from the state manager.
        """
        return self.state_manager.get_config_state()

    # =============================================================
    # Shutdown
    # =============================================================

    def request_close(self):
        """
        Requests app shutdown from the local UI side.
        """
        self.state_manager.request_app_stop()
        self.close_window()

    def close_window(self):
        root = self.get_root()

        if root is not None:
            root.destroy()

        self.is_ui_running = False

    # =============================================================
    # Utility
    # =============================================================

    def get_root(self):
        if self.rendering_manager is None:
            return None

        return getattr(self.rendering_manager, "root", None)

    def get_state_snapshot(self) -> dict:
        """
        Useful for debugging.
        """
        return self.state_manager.get_full_state()