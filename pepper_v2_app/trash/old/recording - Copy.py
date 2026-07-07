import numpy as np
import sounddevice as sd
import wave
from collections import deque
from ..utils.paths import LOCAL_USER_AUDIO

AUDIO_FILE_EXT = "wav"
USB_MIC_NAME = "Realtek"
#todo: import from json

def find_input_device(name_contains: str):
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0 and name_contains.lower() in d["name"].lower():
            return i
    raise ValueError(f"No input device found matching: {name_contains}")

# usb_mic = find_input_device(USB_MIC_NAME)

def record_audio_with_preroll(
    sample_rate=16000,
    channels=1,
    dtype="int16",
    output_file=LOCAL_USER_AUDIO,
    preroll_ms=1000,
    blocksize=1024,
    input_device=None
):
    preroll_blocks = max(1, int((sample_rate * preroll_ms / 1000) / blocksize))
    preroll_buffer = deque(maxlen=preroll_blocks)
    recorded_frames = []

    print("\nWaiting for push-to-talk...")
    ui_update(mode="idle", heard="", reply="")
    
    with sd.InputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype=dtype,
        blocksize=blocksize,
        device=input_device
    ) as stream:

        while not is_key_pressed():
            
            if exit_key():
                return None, True
            
            frame, _ = stream.read(blocksize)
            preroll_buffer.append(frame.copy())

        print("Recording... release push-to-talk key to stop.")
        ui_update(mode="listening", reply="")
        
        recorded_frames.extend(preroll_buffer)

        while is_key_pressed():
            
            if exit_key():
                return None, True
            
            frame, _ = stream.read(blocksize)
            recorded_frames.append(frame.copy())

    if not recorded_frames:
        return None, False

    audio = np.concatenate(recorded_frames, axis=0)

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    return output_file, False