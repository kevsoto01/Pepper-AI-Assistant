import os
import subprocess
import time
import requests
from ..utils.paths import OLLAMA_URL

class OllamaLauncher:
    def __init__(self, force_restart:bool=True, use_vulkan:bool=True, verbose:bool=False):
        self.force_restart = force_restart
        self.use_vulkan = use_vulkan
        self.verbose = verbose
        
    def is_ollama_running(self) -> bool:
        try:
            response = requests.get(OLLAMA_URL, timeout=1)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    
    def stop_ollama(self):
        subprocess.run(
            ["taskkill", "/F", "/T", "/IM", "ollama.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
        for _ in range(30):
            if not self.is_ollama_running():
                if self.verbose: print("Ollama fully stopped.")
                return
            time.sleep(0.5)
    
        raise RuntimeError("Ollama did not fully stop.")
    
    
    def start_ollama(self):
        if self.is_ollama_running():
            if not self.force_restart:
                if self.verbose: print("Ollama is already running. Not restarting it.")
                return
            if self.verbose: print("Stopping existing Ollama server...")
            self.stop_ollama()
            self.clear_ollama_log()
            time.sleep(2)
        
        
        env = os.environ.copy()
    
        if self.use_vulkan is not None:
            if self.use_vulkan:
                env["OLLAMA_VULKAN"] = "1"
                env["HIP_VISIBLE_DEVICES"] = "-1"
                env["GGML_VK_VISIBLE_DEVICES"] = "0"
                if self.verbose: print("Starting Ollama with Vulkan...")
        
            else:
                env.pop("OLLAMA_VULKAN", None)
                env.pop("HIP_VISIBLE_DEVICES", None)
                env.pop("GGML_VK_VISIBLE_DEVICES", None)
                if self.verbose: print("Starting Ollama without Vulkan...")
            
            if self.verbose:
                print("OLLAMA_VULKAN =", env.get("OLLAMA_VULKAN"))
                print("HIP_VISIBLE_DEVICES =", env.get("HIP_VISIBLE_DEVICES"))
                print("GGML_VK_VISIBLE_DEVICES =", env.get("GGML_VK_VISIBLE_DEVICES"))
        
        subprocess.Popen(
            ["ollama", "serve"],
            env=env,
            # stdout=subprocess.DEVNULL,
            # stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        time.sleep(3)
        if self.verbose:
            self.print_ollama_server_log_tail()
            self.print_ollama_port_owner()
    
        for _ in range(30):
            if self.is_ollama_running():
                if self.use_vulkan: print("Ollama started with Vulkan environment.")
                else: print("Ollama started without Vulkan environment.")
                return
            time.sleep(0.5)
        raise RuntimeError("Ollama did not start.")
    
    def print_process_name(self, pid: str):
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            errors="replace"
        )
        print(result.stdout)
    
    def clear_ollama_log(self):
        log_path = os.path.join(os.environ["LOCALAPPDATA"], "Ollama", "server.log")
    
        try:
            open(log_path, "w", encoding="utf-8").close()
            if self.verbose: print("Cleared Ollama server log.")
        except Exception as e:
            if self.verbose: print("Could not clear Ollama log:", e)
            
    def print_ollama_port_owner(self):
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            errors="replace"
        )
    
        for line in result.stdout.splitlines():
            if ":11434" in line and "LISTENING" in line:
                print("Port 11434 owner:", line)
    
                parts = line.split()
                pid = parts[-1]
                self.print_process_name(pid)
    
    def print_ollama_server_log_tail(self, lines: int = 200):
        log_path = os.path.join(
            os.environ["LOCALAPPDATA"],
            "Ollama",
            "server.log"
        )
    
        print(f"\n--- Ollama server log: last {lines} lines ---")
        print(f"Log path: {log_path}\n")
    
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f'Get-Content "$env:LOCALAPPDATA\\Ollama\\server.log" -Tail {lines}'
            ],
            capture_output=True,
            text=True,
            encoding="cp1252",
            errors="replace"
        )
    
        if result.stdout:
            print(result.stdout)
    
        if result.stderr:
            print("--- PowerShell error ---")
            print(result.stderr)
    
        print("--- End Ollama server log ---\n")