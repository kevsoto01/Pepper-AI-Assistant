import tkinter as tk
import threading
import time


class SharedState:
    def __init__(self):
        self._lock = threading.Lock()
        self._volume = 50

    def set_volume(self, value: int):
        with self._lock:
            self._volume = value

    def get_volume(self) -> int:
        with self._lock:
            return self._volume


def worker_loop(shared_state: SharedState, stop_event: threading.Event):
    while not stop_event.is_set():
        volume = shared_state.get_volume()
        print(f"Worker thread sees volume: {volume}")
        time.sleep(0.5)


def main():
    shared_state = SharedState()
    stop_event = threading.Event()

    root = tk.Tk()
    root.title("Threaded Slider Test")
    root.geometry("400x150")

    label = tk.Label(root, text="Volume: 50")
    label.pack(pady=10)

    def on_slider_change(value):
        value = int(float(value))
        shared_state.set_volume(value)
        label.config(text=f"Volume: {value}")

    slider = tk.Scale(
        root,
        from_=0,
        to=100,
        orient="horizontal",
        command=on_slider_change,
        length=300
    )
    slider.set(50)
    slider.pack(pady=10)

    worker_thread = threading.Thread(
        target=worker_loop,
        args=(shared_state, stop_event),
        daemon=True
    )
    worker_thread.start()

    def on_close():
        stop_event.set()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


if __name__ == "__main__":
    main()