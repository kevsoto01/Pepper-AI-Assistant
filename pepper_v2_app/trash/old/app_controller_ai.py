from time import sleep
import threading
import traceback


class AppController:
    """
    Main application controller.

    This class owns the main app flow:
    - initializes app services
    - starts the background app loop
    - starts the local Tkinter UI
    - runs the agent dialogue cycle
    - shuts down services safely

    This class should NOT:
    - build Tkinter widgets directly
    - read/write config directly unless needed
    - store UI state directly
    - contain Pepper robot logic directly
    """

    def __init__(
            self,
            config_controller,
            audio_recorder,
            state_manager
            ):

        print("App controller loaded")

        self.config_controller = config_controller
        self.audio_recorder = audio_recorder
        self.state = state_manager

        # Shortcuts to controllers owned by AppStateManager
        self.web_ui = self.state.web_ui
        self.local_ui = self.state.local_ui
        self.pepper = self.state.pepper
        self.agent_controller = self.state.agent_controller

        # Runtime state
        self.worker_thread = None
        self.audio_input = None
        self.app_running = False
        self.dialogue_cycle_running = False

        # Loop settings
        self.tick_sleep_seconds = 0.01

    # =============================================================
    # App entrypoint
    # =============================================================

    def run_app(self):
        """
        Main app entrypoint.

        Starts app services, launches the background app loop,
        then starts the local Tkinter UI on the main thread.
        """

        self.initialize_app()

        self.worker_thread = threading.Thread(
            target=self.app_loop,
            daemon=True
        )

        self.worker_thread.start()

        try:
            self.state.start_local_ui()

        except KeyboardInterrupt:
            self.request_stop_app()

        except Exception as error:
            self.handle_error(error)

        finally:
            self.stop_app()

    # =============================================================
    # Main app loop
    # =============================================================

    def app_loop(self):
        """
        Background app loop.

        Runs while the app is active.
        Checks UI/keyboard requests through AppStateManager.
        Runs agent dialogue cycles when allowed.
        """

        self.app_running = True

        while not self.state.app_is_stopping():
            try:
                self.app_tick()

                if self.state.app_is_stopping():
                    break

                self.agent_dialogue_cycle()

                if self.state.app_is_stopping():
                    break

                sleep(self.tick_sleep_seconds)

            except Exception as error:
                self.handle_error(error)
                sleep(0.25)

        self.app_running = False

    def app_tick(self):
        """
        One app update tick.

        Delegates request handling to AppStateManager.
        """

        self.state.update()

        if hasattr(self.state, "process_manual_input_if_available"):
            self.state.process_manual_input_if_available()

    # =============================================================
    # Agent dialogue cycle
    # =============================================================

    def agent_dialogue_cycle(self):
        """
        Full voice interaction cycle:

        1. record user audio
        2. send audio/text to agent
        3. play response audio

        If no audio is captured, nothing happens.
        """

        if self.dialogue_cycle_running:
            return

        if not self.should_run_dialogue_cycle():
            return

        self.dialogue_cycle_running = True

        try:
            audio_input = self.get_audio_input()

            if audio_input is None:
                return

            self.audio_input = audio_input

            self.get_agent_response(audio_input)
            self.say_agent_response()

        except Exception as error:
            self.handle_error(error)

        finally:
            self.dialogue_cycle_running = False
            self.state.set_status("idle")

    def should_run_dialogue_cycle(self) -> bool:
        """
        Determines whether the agent dialogue loop should run.
        """

        if self.state.app_is_stopping():
            return False

        if not getattr(self.state, "is_agent_running", False):
            return False

        if self.audio_recorder is None:
            return False

        if self.agent_controller is None:
            return False

        return True

    def get_audio_input(self):
        """
        Records user input through the audio recorder.
        """

        self.state.set_status("idle")

        audio_input = self.audio_recorder.record(
            on_listening_start=lambda: self.state.set_status("listening"),
            on_listening_stop=lambda: self.state.set_status("thinking")
        )

        if audio_input:
            self.forward_heard_text(audio_input)

        return audio_input

    def get_agent_response(self, audio_input):
        """
        Sends user input to the agent controller.

        Expected agent_controller behavior:
        - answer_question(audio_input)
        - stores response internally, or
        - returns response text
        """

        self.state.set_status("thinking")

        response = self.agent_controller.answer_question(audio_input)

        if response:
            self.forward_reply_text(response)

        return response

    def say_agent_response(self):
        """
        Plays the agent's response audio locally.
        """

        self.state.set_status("speaking")

        if not hasattr(self.agent_controller, "tts"):
            return

        if self.agent_controller.tts is None:
            return

        self.agent_controller.tts.play_audio_locally()

    # =============================================================
    # Forwarding helpers
    # =============================================================

    def forward_heard_text(self, text):
        """
        Sends heard text/audio reference to the UI state.
        """

        if hasattr(self.state, "update_heard_text"):
            self.state.update_heard_text(str(text))

    def forward_reply_text(self, text):
        """
        Sends agent response text to the UI state.
        """

        if hasattr(self.state, "update_reply_text"):
            self.state.update_reply_text(str(text))

    # =============================================================
    # App launcher helpers
    # =============================================================

    def initialize_app(self):
        """
        Initializes app services before the UI starts.
        """

        self.state.start()

    def request_stop_app(self):
        """
        Requests app shutdown.
        """

        if hasattr(self.state, "request_stop_app"):
            self.state.request_stop_app()

    def stop_app(self):
        """
        Stops app safely.

        This is called after the Tkinter UI exits.
        """

        print("Stopping app")

        try:
            self.state.shutdown()

        except Exception as error:
            print("Error during app shutdown:")
            print(error)

    # =============================================================
    # Thread helpers
    # =============================================================

    def wait_for_worker_thread(self, timeout=2):
        """
        Optionally waits for worker thread to end.
        """

        if self.worker_thread is None:
            return

        if not self.worker_thread.is_alive():
            return

        self.worker_thread.join(timeout=timeout)

    # =============================================================
    # Error handling
    # =============================================================

    def handle_error(self, error):
        """
        Central app error handler.
        """

        error_message = str(error)

        print("App error:")
        print(error_message)
        traceback.print_exc()

        if hasattr(self.state, "set_error"):
            self.state.set_error(error_message)

    # =============================================================
    # Debug helpers
    # =============================================================

    def get_runtime_snapshot(self) -> dict:
        """
        Returns app controller runtime state.
        """

        state_snapshot = {}

        if hasattr(self.state, "get_runtime_state_snapshot"):
            state_snapshot = self.state.get_runtime_state_snapshot()

        return {
            "app_controller": {
                "app_running": self.app_running,
                "dialogue_cycle_running": self.dialogue_cycle_running,
                "worker_thread_alive": (
                    self.worker_thread.is_alive()
                    if self.worker_thread is not None
                    else False
                ),
                "audio_input": self.audio_input,
            },
            "state_manager": state_snapshot,
        }