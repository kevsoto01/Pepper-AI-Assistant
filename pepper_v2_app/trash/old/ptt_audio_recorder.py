import numpy as np
import sounddevice as sd
import wave

from pathlib import Path
from collections import deque
from dataclasses import dataclass, field

from ..utils.paths import LOCAL_USER_AUDIO
from ..controls.keyboard import is_key_pressed, record_key_pressed, exit_key_pressed

# todo \/ \/ \/ consider converting to class, probably fine as just a function

USB_MIC_NAME = "Realtek"

def find_input_device(name_contains: str):
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0 and name_contains.lower() in d["name"].lower():
            return i
    raise ValueError(f"No input device found matching: {name_contains}")

@dataclass
class AudioRecordConfig:
    sample_rate: int = 16000
    channels: int = 1
    dtype: str = "int16"
    output_file: Path | str = LOCAL_USER_AUDIO
    preroll_ms: int = 1000
    blocksize: int = 1024
    input_device: int | None = None


@dataclass
class AudioRecordState:
    preroll_buffer: deque
    recorded_frames: list = field(default_factory=list)


def get_preroll_block_count(sample_rate: int, preroll_ms: int, blocksize: int) -> int:
    return max(1, int((sample_rate * preroll_ms / 1000) / blocksize))

def create_record_state(config: AudioRecordConfig) -> AudioRecordState:
    preroll_blocks = get_preroll_block_count(
        config.sample_rate,
        config.preroll_ms,
        config.blocksize,
    )
    return AudioRecordState(preroll_buffer=deque(maxlen=preroll_blocks))


def read_frame(stream: sd.InputStream, blocksize: int):
    frame, _ = stream.read(blocksize)
    return frame.copy()


def write_wav(audio: np.ndarray, output_file, sample_rate: int, channels: int) -> str:
    output_file = str(output_file)

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    return output_file

def wait_for_ptt_press(stream: sd.InputStream, config: AudioRecordConfig, state: AudioRecordState):
    print("\nWaiting for push-to-talk...")

    while not record_key_pressed():
        if exit_key_pressed():
            return True
        frame = read_frame(stream, config.blocksize)
        state.preroll_buffer.append(frame)

    return False


def capture_ptt_audio(stream: sd.InputStream, config: AudioRecordConfig, state: AudioRecordState):
    print("Recording... release push-to-talk key to stop.")

    state.recorded_frames.extend(state.preroll_buffer)

    while record_key_pressed():
        if exit_key_pressed():
            return True
        frame = read_frame(stream, config.blocksize)
        state.recorded_frames.append(frame)

    return False

def record_audio_with_preroll(
        config: AudioRecordConfig = AudioRecordConfig(),
        on_listening_start=None,
        on_listening_stop=None
        ):
    
    if config is None:
        config = AudioRecordConfig()
        
    state = create_record_state(config)

    with sd.InputStream(
        samplerate=config.sample_rate,
        channels=config.channels,
        dtype=config.dtype,
        blocksize=config.blocksize,
        device=config.input_device,
    ) as stream:

        
        if wait_for_ptt_press(stream, config, state): # returns true if exit key is pressed
            return None
        
        if on_listening_start is not None: 
            on_listening_start()
            
        try: 
            if capture_ptt_audio(stream, config, state): 
                return None 
        
        finally:  
            if on_listening_stop is not None:  
                on_listening_stop()
        
        print("Processing...")
        
    if not state.recorded_frames:
        return None

    audio = np.concatenate(state.recorded_frames, axis=0)
    output_file = write_wav(
        audio=audio,
        output_file=config.output_file,
        sample_rate=config.sample_rate,
        channels=config.channels,
    )

    return output_file