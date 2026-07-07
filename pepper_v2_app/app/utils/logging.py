from datetime import datetime
from pathlib import Path

def init_logging():
    log_dir = Path(r"../logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_name = "log_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    return log_dir / f"{log_name}.txt"
    
def log_conversation_message(role: str, content: str, history_log_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with history_log_file.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role.upper()}: {content}\n")    