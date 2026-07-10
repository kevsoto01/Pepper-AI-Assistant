import json
from dataclasses import dataclass
from pathlib import Path

PEPPER_SSH_CONFIG_PATH = Path.home() / ".pepper_ai" / "pepper_ssh.json"

DEFAULT_SSH_CONFIG = {
    "username": "",
    "password": "",
    "ip": "",
    "port": 22
}

@dataclass(frozen=True)
class SSHConfig:
    username: str
    password: str
    ip: str
    port: int = 22

def ensure_ssh_config_file() -> None:
    config_dir = PEPPER_SSH_CONFIG_PATH.parent

    config_dir.mkdir(parents=True, exist_ok=True)

    if not PEPPER_SSH_CONFIG_PATH.exists():
        with PEPPER_SSH_CONFIG_PATH.open("w", encoding="utf-8") as file:
            json.dump(DEFAULT_SSH_CONFIG, file, indent=4)

        raise FileNotFoundError(
            f"Created SSH config file here:\n{PEPPER_SSH_CONFIG_PATH}\n\n"
            "Fill in username, password, and ip before running again."
        )

    with PEPPER_SSH_CONFIG_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    updated = False

    for key, value in DEFAULT_SSH_CONFIG.items():
        if key not in data:
            data[key] = value
            updated = True

    if updated:
        with PEPPER_SSH_CONFIG_PATH.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


def load_ssh_config() -> SSHConfig:
    ensure_ssh_config_file()

    with PEPPER_SSH_CONFIG_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    required_fields = ["username", "password", "ip"]

    missing = [
        field
        for field in required_fields
        if not str(data.get(field, "")).strip()
    ]

    if missing:
        raise ValueError(
            f"Missing required SSH config field(s): {', '.join(missing)}\n"
            f"Edit this file:\n{PEPPER_SSH_CONFIG_PATH}"
        )

    return SSHConfig(
        username=data["username"],
        password=data["password"],
        ip=data["ip"],
        port=int(data.get("port", 22)),
    )


def get_ssh_details() -> dict:
    config = load_ssh_config()

    return {
        "username": config.username,
        "password": config.password,
        "ip": config.ip,
        "port": config.port,
    }


if __name__ == "__main__":
    ssh_details = get_ssh_details()
    print("SSH config loaded successfully.")
    print({
        "username": ssh_details["username"],
        "password": "***hidden***",
        "ip": ssh_details["ip"],
        "port": ssh_details["port"],
    })