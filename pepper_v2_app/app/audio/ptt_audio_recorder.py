# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 13:31:02 2026

@author: kevso
"""

import numpy as np
import sounddevice as sd
import wave

from pathlib import Path
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

from ..utils.paths import LOCAL_USER_AUDIO
from ..controls.keyboard import is_key_pressed


USB_MIC_NAME = "Realtek"


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


class PushToTalkAudioRecorder:
    def __init__(
        self,
        config: AudioRecordConfig | None = None
    ):
        self.config = config or AudioRecordConfig()
        self.state = self._create_record_state()

    @staticmethod
    def find_input_device(name_contains: str) -> int:
        devices = sd.query_devices()

        for i, device in enumerate(devices):
            has_input = device["max_input_channels"] > 0
            name_matches = name_contains.lower() in device["name"].lower()

            if has_input and name_matches:
                return i

        raise ValueError(f"No input device found matching: {name_contains}")

    def set_input_device_by_name(self, name_contains: str) -> None:
        self.config.input_device = self.find_input_device(name_contains)

    def _get_preroll_block_count(self) -> int:
        return max(
            1,
            int(
                (self.config.sample_rate * self.config.preroll_ms / 1000)
                / self.config.blocksize
            ),
        )

    def _create_record_state(self) -> AudioRecordState:
        preroll_blocks = self._get_preroll_block_count()
        return AudioRecordState(preroll_buffer=deque(maxlen=preroll_blocks))

    def _reset_state(self) -> None:
        self.state = self._create_record_state()

    def _read_frame(self, stream: sd.InputStream) -> np.ndarray:
        frame, _ = stream.read(self.config.blocksize)
        return frame.copy()

    def _write_wav(self, audio: np.ndarray) -> str:
        output_file = str(self.config.output_file)

        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.config.sample_rate)
            wf.writeframes(audio.tobytes())

        return output_file

    @staticmethod
    def _cancel_requested(should_cancel: Callable[[], bool] | None = None) -> bool:
        if should_cancel is None:
            return False

        try:
            return bool(should_cancel())
        except Exception:
            # Do not let UI/state callback errors crash the audio stream.
            return False

    def _wait_for_ptt_press(
        self,
        stream: sd.InputStream,
        should_cancel: Callable[[], bool] | None = None,
    ) -> bool:
        print("\nWaiting for push-to-talk...")

        while not self.record_key_pressed():
            if self.exit_key_pressed() or self._cancel_requested(should_cancel):
                return True

            frame = self._read_frame(stream)
            self.state.preroll_buffer.append(frame)

        return False

    def _capture_ptt_audio(
        self,
        stream: sd.InputStream,
        should_cancel: Callable[[], bool] | None = None,
    ) -> bool:
        print("Recording... release push-to-talk key to stop.")

        self.state.recorded_frames.extend(self.state.preroll_buffer)

        while self.record_key_pressed():
            if self.exit_key_pressed() or self._cancel_requested(should_cancel):
                return True

            frame = self._read_frame(stream)
            self.state.recorded_frames.append(frame)

        return False

    def set_keybinds(self, listen_key, exit_key):
        self.listen_key = listen_key
        self.exit_key = exit_key

    def record_key_pressed(self):
        return is_key_pressed(self.listen_key)

    def exit_key_pressed(self):
        return is_key_pressed(self.exit_key)

    def record(
        self,
        on_listening_start=None,
        on_listening_stop=None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> str | None:
        self._reset_state()

        with sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            blocksize=self.config.blocksize,
            device=self.config.input_device,
        ) as stream:

            exit_requested = self._wait_for_ptt_press(stream, should_cancel=should_cancel)

            if exit_requested:
                return None

            if on_listening_start is not None:
                on_listening_start()

            try:
                exit_requested = self._capture_ptt_audio(
                    stream,
                    should_cancel=should_cancel,
                )

                if exit_requested:
                    return None

            finally:
                if on_listening_stop is not None:
                    on_listening_stop()

        if not self.state.recorded_frames:
            return None

        audio = np.concatenate(self.state.recorded_frames, axis=0)

        return self._write_wav(audio)
