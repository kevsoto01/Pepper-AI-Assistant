from __future__ import annotations

# %% Import Modules

# Services
from app.audio.tts import PiperTTS
from app.llm.llm_system import LLMSystem
from app.audio.speech_recognition import WhisperTranscriber
from app.audio.ptt_audio_recorder import PushToTalkAudioRecorder

# Managers
from app.pepper.ssh import SSHManager
from app.pepper.tablet import PepperTabletManager
from app.pepper.playback import PepperPlaybackManager
from app.pepper.movement import PepperMovementManager
from app.ui.web_ui.web_renderer import WebRenderingManager
from app.ui.web_ui.web_state import WebStateManager
from app.config.config_manager import ConfigManager
from app.ui.local_ui.local_ui_renderer import LocalUIRenderer

# Hubs
from app.llm.llm import ModelHub

# Controllers
from app.pepper.pepper_controller import PepperController
from app.ui.web_ui.web_ui_controller import WebUIController
from app.ui.local_ui.local_ui_controller import LocalUIController
from app.agent.agent_controller import AIAgentController
from app.app.app import AppController


# %% Run Agent
def run_assistant(): 
    # Config
    config_manager = ConfigManager()

    # Pepper
    ssh_manager = SSHManager()
    pepper_audio = PepperPlaybackManager(ssh_manager)
    pepper_tablet = PepperTabletManager(ssh_manager)
    pepper_movement = PepperMovementManager(ssh_manager)
    pepper_controller = PepperController(ssh_manager, pepper_tablet, pepper_audio, pepper_movement)

    # Web UI
    web_state_manager = WebStateManager()
    web_rendering_manager = WebRenderingManager(web_state_manager)
    web_ui_controller = WebUIController(rendering_manager=web_rendering_manager)

    # Local UI
    local_ui_renderer = LocalUIRenderer()
    local_ui_controller = LocalUIController(rendering_manager=local_ui_renderer)

    # Audio
    audio_recorder = PushToTalkAudioRecorder()
    whisper = WhisperTranscriber()
    piper = PiperTTS()

    # LLMs
    model_hub = ModelHub()
    llm_system = LLMSystem(model_hub)

    # Agent
    agent_controller = AIAgentController(
            llm_system=llm_system,
            whisper=whisper,
            piper=piper
        )

    # App
    app = AppController(
        config_manager=config_manager,
        audio_recorder=audio_recorder,
        agent_controller=agent_controller,
        web_ui=web_ui_controller,
        local_ui=local_ui_controller,
        pepper=pepper_controller
    )

    app.run()


if __name__ == "__main__":
    run_assistant()
