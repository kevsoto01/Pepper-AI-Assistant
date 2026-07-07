#%% Import Modules

# Services
from app.audio.tts import PiperTTS
from app.llm.llm_system import LLMSystem
from app.audio.speech_recognition import WhisperTranscriber

# Managers
from app.pepper.ssh import SSHManager
from app.pepper.tablet import PepperTabletManager
from app.pepper.playback import PepperPlaybackManager
from app.ui.web_ui.web_renderer import WebRenderingManager
from app.ui.web_ui.web_state import WebStateManager
from app.config.config_manager import ConfigManager
from app.ui.local_ui.local_ui_manager import LocalUIManager

# Controllers
from app.pepper.pepper_controller import PepperController
from app.ui.web_ui.web_ui_controller import WebUIController
from trash.local_ui_controller import LocalUIController
from app.config.config_controller import ConfigController
from app.agent_controller import AIAgentController

# Hubs
from app.llm.llm import ModelHub

#%% Run Agent

def run_assistant():
    
    # Config
    config_manager = ConfigManager()
    config_controller = ConfigController(config_manager)
    
    # Pepper
    ssh_manager = SSHManager()
    pepper_audio = PepperPlaybackManager(ssh_manager)
    pepper_tablet = PepperTabletManager(ssh_manager)
    pepper_controller = PepperController(ssh_manager, pepper_tablet, pepper_audio)

    # Web UI
    web_state_manager = WebStateManager()
    web_rendering_manager = WebRenderingManager(state_manager=web_state_manager, use_background=True)
    web_ui_controller = WebUIController(web_state_manager, web_rendering_manager)
 
    # Local UI
    local_ui_manager = LocalUIManager()
    local_ui_controller = LocalUIController(local_ui_manager, config_controller) 
 
    # LLM Assistants
    model_hub = ModelHub(config_controller)
    llm_system = LLMSystem(model_hub)
 
    # Audio Assistants
    whisper = WhisperTranscriber(config_controller)
    piper = PiperTTS()

    agent = AIAgentController(
        llm_system=llm_system,
        whisper=whisper,
        piper=piper,
        web_ui_controller=web_ui_controller,
        local_ui_controller=local_ui_controller,
        pepper_controller=pepper_controller,
        config_controller=config_controller
    )

    agent.run_assistant()