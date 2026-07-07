from __future__ import annotations

import atexit
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


server_process: Optional[subprocess.Popen] = None


def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.settimeout(timeout)
		return sock.connect_ex((host, port)) == 0


def get_pid_using_port(port: int) -> Optional[int]:
	if not sys.platform.startswith("win"):
		return None

	cmd = f'netstat -ano | findstr :{port}'

	result = subprocess.run(
		cmd,
		shell=True,
		capture_output=True,
		text=True,
	)

	if result.returncode != 0:
		return None

	for line in result.stdout.splitlines():
		parts = line.split()

		if len(parts) < 5:
			continue

		local_address = parts[1]
		state = parts[3]
		pid_text = parts[4]

		if f":{port}" in local_address and state.upper() == "LISTENING":
			try:
				return int(pid_text)
			except ValueError:
				return None

	return None


def kill_pid(pid: int) -> bool:
	if not sys.platform.startswith("win"):
		return False

	result = subprocess.run(
		["taskkill", "/PID", str(pid), "/F"],
		capture_output=True,
		text=True,
	)

	return result.returncode == 0


def kill_process_using_port(port: int) -> bool:
	pid = get_pid_using_port(port)

	if pid is None:
		return True

	print(f"Killing process using port {port}. PID: {pid}")
	return kill_pid(pid)


def start_webserver(
    	port: int = 8000,
    	directory: str | Path | None = None,
    	host: str = "0.0.0.0",
    	wait: float = 2.0,
    	kill_existing: bool = True,
    ) -> bool:
	global server_process

	if server_process is not None and server_process.poll() is None:
		return True

	check_host = "127.0.0.1" if host == "0.0.0.0" else host

	if is_port_open(check_host, port):
		if kill_existing:
			kill_process_using_port(port)
			time.sleep(0.5)
		else:
			print(f"Port {port} is already in use.")
			return False

	if is_port_open(check_host, port):
		print(f"Port {port} is still in use after kill attempt.")
		return False

	serve_dir = Path(directory) if directory else Path(__file__).resolve().parent
	serve_dir = serve_dir.resolve()

	cmd = [
		sys.executable,
		"-m",
		"http.server",
		str(port),
		"--bind",
		host,
	]

	creationflags = 0

	if sys.platform.startswith("win"):
		creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

	try:
		server_process = subprocess.Popen(
			cmd,
			cwd=str(serve_dir),
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
			creationflags=creationflags,
		)

	except Exception as e:
		print("Failed to start webserver:", e)
		server_process = None
		return False

	start_time = time.time()

	while time.time() - start_time < wait:
		if server_process.poll() is not None:
			server_process = None
			return False

		if is_port_open(check_host, port):
			return True

		time.sleep(0.1)

	return False


def stop_webserver(timeout: float = 3.0, port: int = 8000) -> bool:
	global server_process

	if server_process is not None and server_process.poll() is None:
		try:
			server_process.terminate()
			server_process.wait(timeout=timeout)

		except subprocess.TimeoutExpired:
			server_process.kill()
			server_process.wait()

		except Exception as e:
			print("Failed to stop tracked webserver:", e)

		finally:
			server_process = None

	# Also kill orphaned server caused by Spyder/IPython reloads
	kill_process_using_port(port)

	return True


def webserver_running(port: int = 8000) -> bool:
	if server_process is not None and server_process.poll() is None:
		return True

	return is_port_open("127.0.0.1", port)


atexit.register(stop_webserver)

