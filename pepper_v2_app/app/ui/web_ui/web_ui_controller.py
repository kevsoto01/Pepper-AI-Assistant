from ...web.webserver import start_webserver, stop_webserver, webserver_running
from ...utils.paths import WEB_DIR, UI_PORT, UI_HOST


class WebUIController:
    def __init__(
        self,
        rendering_manager,
        port=UI_PORT,
        host=UI_HOST,
        ui_directory=WEB_DIR,
    ):
        
        self.rendering_manager = rendering_manager
        self.state_manager = self.rendering_manager.state_manager
        self.port = port
        self.host = host
        self.ui_directory = ui_directory

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _set_renderer_background(self, enabled: bool) -> bool:
        enabled = bool(enabled)

        if hasattr(self.rendering_manager, "set_background_enabled"):
            self.rendering_manager.set_background_enabled(enabled)
            return True

        if hasattr(self.rendering_manager, "use_background"):
            self.rendering_manager.use_background = enabled
            return True

        return False

    def _refresh_template_if_possible(self):
        """
        Rebuilds index.html from the active template if the renderer supports it.
        Different versions of WebRenderingManager may name this differently.
        """
        for method_name in (
            "render_html",
            "write_html",
            "build_html",
            "create_html",
            "init_ui_state",
        ):
            method = getattr(self.rendering_manager, method_name, None)
            if callable(method):
                method()
                return True
        return False

    # ------------------------------------------------------------------
    # UI lifecycle
    # ------------------------------------------------------------------
    def load(self, use_background):
        self._set_renderer_background(use_background)

        print("Starting UI webserver...")
        print("Host:", self.host)
        print("Port:", self.port)
        print("Directory:", self.ui_directory)
        print("Directory exists:", self.ui_directory.exists())
        print("Background enabled:", use_background)

        server_started = start_webserver(
            port=self.port,
            host=self.host,
            directory=self.ui_directory,
        )

        if not server_started:
            raise RuntimeError("UI webserver failed to start.")

        self.rendering_manager.init_ui_state()
        self.set_loading()

    def unload(self):
        self.set_disconnected()
        stop_webserver(port=self.port)

    def stop(self):
        return self.unload()

    def is_loaded(self):
        return webserver_running(self.port)

    # ------------------------------------------------------------------
    # UI background
    # ------------------------------------------------------------------
    def enable_background(self):
        self._set_renderer_background(True)
        self._refresh_template_if_possible()

    def disable_background(self):
        self._set_renderer_background(False)
        self._refresh_template_if_possible()

    def toggle_background(self):
        enabled = not self.background_enabled()
        self._set_renderer_background(enabled)
        self._refresh_template_if_possible()
        return enabled

    def background_enabled(self):
        return bool(getattr(self.rendering_manager, "use_background", False))

    # ------------------------------------------------------------------
    # UI updates
    # ------------------------------------------------------------------
    def update_ui(self, mode=None, heard=None, reply=None):
        self.rendering_manager.ui_update(mode=mode, heard=heard, reply=reply)
        """
        Valid modes:
        - idle
        - listening
        - thinking
        - speaking
        - loading
        - disconnected
        """
    def set_idle(self):
        # Do not clear heard/reply here. Idle often happens immediately after speaking.
        self.update_ui(mode="idle")

    def set_listening(self):
        self.update_ui(mode="listening")

    def set_thinking(self, heard=None):
        self.update_ui(mode="thinking", heard=heard)

    def set_speaking(self, reply=None):
        self.update_ui(mode="speaking", reply=reply)

    def set_loading(self):
        self.update_ui(mode="loading", reply="", heard="")

    def set_disconnected(self):
        self.update_ui(mode="disconnected", reply="", heard="")

    def set_heard(self, text: str, detected_language=None):
        self.update_ui(heard=text or "")

    def set_reply(self, text: str):
        self.update_ui(reply=text or "")

    def clear_exchange_text(self):
        self.update_ui(heard="", reply="")
