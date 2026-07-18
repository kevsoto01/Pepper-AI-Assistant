import json
import os
from pathlib import Path
from typing import Any

from ..utils.paths import CONFIG_PATH

DEFAULT_CONFIG: dict[str, Any] = {
    "general": {
        "user_age": 100,
        "languages": ["en", "es"],
        "max_turns": 3,
        "word_count": 30,
    },
    "writer_llm": {
        "model": "qwen2.5:3b-instruct-q4_K_M",
        "temperature": 0.0,
        "max_tokens": 4096,
        "default_model": "qwen2.5:3b-instruct-q4_K_M",
    },
    "judge_llm": {
        "model": "qwen2.5:1.5b-instruct-q4_K_M",
        "temperature": 0.0,
        "max_tokens": 256,
        "default_model": "qwen2.5:3b-instruct-q4_K_M",
    },
    "speech_recognition": {
        "model": "base",
    },
    "keybinds": {
        "listen_key": "end",
        "stop_key": "home",
        "exit_key": "esc",
    },
    "logging": {
        "log_conversation": True,
        "verbose": False,
    },
    "network": {
        "show_ipv4_on_start": True,
        "host": "0.0.0.0",
        "port": 8000,
    },
    "ssh": {
        "enabled": False,
        "host": "",
        "port": 22,
    },
    "web_ui": {
        "should_use": False,
        "use_background": False,
    },
    "pepper": {
        "should_use": False,
        "volume": 80,
    },
    "_notes": {
        "_llm_models": [
            "qwen2.5:7b-instruct-q4_K_M",
            "qwen2.5:3b-instruct-q4_K_M",
            "qwen2.5:1.5b-instruct-q4_K_M",
            "qwen2.5:0.5b-instruct-q4_K_M",
            "gemma:2b-instruct-q4_K_M",
            "llama3.2",
        ],
        "_ollama_install_examples": [
            "ollama pull qwen2.5:7b-instruct-q4_K_M",
            "ollama pull gemma:2b-instruct-q4_K_M",
        ],
        "_whisper_models": [
            "tiny",
            "base",
            "small",
            "medium",
            "large",
        ],
    },
}



class ConfigManager:
    def __init__(self):
        self.config_path = Path(CONFIG_PATH)
        self.default_config = DEFAULT_CONFIG

    def _read_json_file(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file: 
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object in {path}, got {type(data).__name__}")

        return data

    def _write_json_file(self, path: Path, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise TypeError("Config data must be a dictionary")

        path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = path.with_name(f".{path.name}.tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
            file.write("\n")

        os.replace(temp_path, path)

    def _read_config(self) -> dict[str, Any]:
        try:
            return self._read_json_file(self.config_path)
        except FileNotFoundError:
            print("Config could not be found, rewriting to default config.")
            return self._reset()
        except (json.JSONDecodeError, ValueError):
            print("Found config is not of type dict, rewriting to default config.")
            return self._reset()

    def _reset(self) -> dict[str, Any]:
        self._write_json_file(self.config_path, self.default_config)
        return self.default_config

    def get_config(self) -> dict[str, Any]:
        return self._read_config()

    def set_config(self, new_config: dict[str, Any]) -> None:
        if not isinstance(new_config, dict):
            raise TypeError("new_config must be a dictionary")
        self._write_json_file(self.config_path, new_config)
        
    def get_config_value(self, group: str, key: str) -> Any:
        config = self._read_config()
        return config[group].get(key)

    def set_config_value(self, group: str, key: str, value: Any) -> None:
        config = self._read_config()
        config[group][key] = value
        self._write_json_file(self.config_path, config)
