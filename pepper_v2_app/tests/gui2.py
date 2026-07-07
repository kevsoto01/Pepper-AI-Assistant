import sys
import queue
import tkinter as tk
from tkinter import ttk


class ConsoleRedirector:
    def __init__(self, output_queue):
        self.output_queue = output_queue

    def write(self, text):
        if text:
            self.output_queue.put(text)

    def flush(self):
        pass


class SetupGUI:
    def __init__(self, model_options):
        self.model_options = model_options
        self.config = None

        self.root = tk.Tk()
        self.root.title("Pepper Setup")
        self.root.state("zoomed")

        self.dark_mode_var = tk.BooleanVar(value=True)

        self.writer_model_var = tk.StringVar(value=model_options[0])
        self.judge_model_var = tk.StringVar(value=model_options[0])

        self.text_vars = [
            tk.StringVar(value=""),
            tk.StringVar(value=""),
            tk.StringVar(value=""),
            tk.StringVar(value=""),
            tk.StringVar(value=""),
        ]

        self.setup_styles()
        self.build_ui()
        self.apply_theme()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def get_colors(self):
        if self.dark_mode_var.get():
            return {
                "bg": "#1e1e1e",
                "panel": "#2b2b2b",
                "input": "#121212",
                "text": "#f0f0f0",
                "muted": "#b5b5b5",
                "button": "#333333",
                "button_hover": "#444444",
                "accent": "#3a7afe",
                "start": "#137333",
                "start_hover": "#0b5724",
            }

        return {
            "bg": "#f4f4f4",
            "panel": "#ffffff",
            "input": "#ffffff",
            "text": "#111111",
            "muted": "#444444",
            "button": "#e6e6e6",
            "button_hover": "#d6d6d6",
            "accent": "#2563eb",
            "start": "#137333",
            "start_hover": "#0b5724",
        }

    def apply_theme(self):
        colors = self.get_colors()

        self.root.configure(bg=colors["bg"])

        self.style.configure(
            "App.TFrame",
            background=colors["bg"]
        )

        self.style.configure(
            "App.TLabel",
            background=colors["bg"],
            foreground=colors["text"]
        )

        self.style.configure(
            "Muted.TLabel",
            background=colors["bg"],
            foreground=colors["muted"]
        )

        self.style.configure(
            "App.TButton",
            background=colors["button"],
            foreground=colors["text"],
            padding=8
        )

        self.style.map(
            "App.TButton",
            background=[
                ("active", colors["button_hover"]),
                ("pressed", colors["accent"])
            ],
            foreground=[
                ("active", colors["text"]),
                ("pressed", colors["text"])
            ]
        )

        self.style.configure(
            "App.TCombobox",
            fieldbackground=colors["input"],
            background=colors["input"],
            foreground=colors["text"],
            arrowcolor=colors["text"]
        )

        self.main_frame.configure(style="App.TFrame")

        for widget in self.text_entries:
            widget.configure(
                bg=colors["input"],
                fg=colors["text"],
                insertbackground=colors["text"]
            )

        self.start_button.configure(
            bg=colors["start"],
            fg="white",
            activebackground=colors["start_hover"],
            activeforeground="white"
        )

        if self.dark_mode_var.get():
            self.dark_mode_button.configure(
                text="Dark Mode: ON",
                bg="#3a7afe",
                fg="white",
                activebackground="#2454b8"
            )
        else:
            self.dark_mode_button.configure(
                text="Dark Mode: OFF",
                bg="#d6d6d6",
                fg="#111111",
                activebackground="#c7c7c7"
            )

    def build_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=20, style="App.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        top_row = ttk.Frame(self.main_frame, style="App.TFrame")
        top_row.pack(fill="x", pady=(0, 20))

        ttk.Label(
            top_row,
            text="Pepper Startup Settings",
            font=("Arial", 18, "bold"),
            style="App.TLabel"
        ).pack(side="left")

        self.dark_mode_button = tk.Button(
            top_row,
            text="Dark Mode: ON",
            command=self.toggle_dark_mode,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=6
        )
        self.dark_mode_button.pack(side="right")

        ttk.Label(
            self.main_frame,
            text="Writer LLM Model",
            style="App.TLabel"
        ).pack(anchor="w")

        self.writer_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.writer_model_var,
            values=self.model_options,
            state="readonly",
            style="App.TCombobox"
        )
        self.writer_dropdown.pack(fill="x", pady=(5, 15))

        ttk.Label(
            self.main_frame,
            text="Judge LLM Model",
            style="App.TLabel"
        ).pack(anchor="w")

        self.judge_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.judge_model_var,
            values=self.model_options,
            state="readonly",
            style="App.TCombobox"
        )
        self.judge_dropdown.pack(fill="x", pady=(5, 15))

        self.text_entries = []

        for index, text_var in enumerate(self.text_vars, start=1):
            ttk.Label(
                self.main_frame,
                text=f"Text Box {index}",
                style="App.TLabel"
            ).pack(anchor="w")

            entry = tk.Entry(
                self.main_frame,
                textvariable=text_var,
                relief="flat",
                font=("Arial", 11)
            )
            entry.pack(fill="x", pady=(5, 10), ipady=7)

            self.text_entries.append(entry)

        self.start_button = tk.Button(
            self.main_frame,
            text="START PEPPER",
            font=("Arial", 16, "bold"),
            height=2,
            relief="flat",
            command=self.start_pepper
        )
        self.start_button.pack(fill="x", pady=(20, 0))

    def toggle_dark_mode(self):
        self.dark_mode_var.set(not self.dark_mode_var.get())
        self.apply_theme()

    def start_pepper(self):
        self.config = {
            "writer_model": self.writer_model_var.get(),
            "judge_model": self.judge_model_var.get(),
            "text_box_1": self.text_vars[0].get(),
            "text_box_2": self.text_vars[1].get(),
            "text_box_3": self.text_vars[2].get(),
            "text_box_4": self.text_vars[3].get(),
            "text_box_5": self.text_vars[4].get(),
            "dark_mode": self.dark_mode_var.get(),
        }

        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.config


class PepperGUI:
    def __init__(self, config, on_send=None, on_volume_change=None, on_close=None):
        self.config = config
        self.on_send = on_send
        self.on_volume_change = on_volume_change
        self.on_close = on_close

        self.root = tk.Tk()
        self.root.title("Pepper Control")
        self.root.state("zoomed")

        self.dark_mode_var = tk.BooleanVar(value=config.get("dark_mode", True))
        self.volume_var = tk.IntVar(value=50)
        self.user_input_var = tk.StringVar(value="")

        self.console_queue = queue.Queue()
        self.console_visible = True

        self.setup_styles()
        self.build_main_gui()
        self.apply_theme()
        self.redirect_console_output()

        self.root.protocol("WM_DELETE_WINDOW", self.close_all)

        self.poll_console_queue()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def get_colors(self):
        if self.dark_mode_var.get():
            return {
                "bg": "#1e1e1e",
                "panel": "#2b2b2b",
                "input": "#121212",
                "text": "#f0f0f0",
                "muted": "#b5b5b5",
                "button": "#333333",
                "button_hover": "#444444",
                "accent": "#3a7afe",
                "console_bg": "#050505",
                "console_text": "#00ff88",
            }

        return {
            "bg": "#f4f4f4",
            "panel": "#ffffff",
            "input": "#ffffff",
            "text": "#111111",
            "muted": "#444444",
            "button": "#e6e6e6",
            "button_hover": "#d6d6d6",
            "accent": "#2563eb",
            "console_bg": "#ffffff",
            "console_text": "#111111",
        }

    def apply_theme(self):
        colors = self.get_colors()

        self.root.configure(bg=colors["bg"])

        self.style.configure(
            "App.TFrame",
            background=colors["bg"]
        )

        self.style.configure(
            "Panel.TFrame",
            background=colors["panel"]
        )

        self.style.configure(
            "App.TLabel",
            background=colors["bg"],
            foreground=colors["text"]
        )

        self.style.configure(
            "Panel.TLabel",
            background=colors["panel"],
            foreground=colors["text"]
        )

        self.style.configure(
            "Muted.TLabel",
            background=colors["panel"],
            foreground=colors["muted"]
        )

        self.style.configure(
            "App.TButton",
            background=colors["button"],
            foreground=colors["text"],
            padding=8
        )

        self.style.map(
            "App.TButton",
            background=[
                ("active", colors["button_hover"]),
                ("pressed", colors["accent"])
            ],
            foreground=[
                ("active", colors["text"]),
                ("pressed", colors["text"])
            ]
        )

        self.style.configure(
            "App.Horizontal.TScale",
            background=colors["panel"],
            troughcolor=colors["input"]
        )

        self.main_container.configure(style="App.TFrame")
        self.top_row.configure(style="App.TFrame")
        self.control_frame.configure(style="Panel.TFrame")
        self.console_frame.configure(style="Panel.TFrame")

        self.heard_box.configure(
            bg=colors["input"],
            fg=colors["text"],
            insertbackground=colors["text"]
        )

        self.reply_box.configure(
            bg=colors["input"],
            fg=colors["text"],
            insertbackground=colors["text"]
        )

        self.user_input_entry.configure(
            bg=colors["input"],
            fg=colors["text"],
            insertbackground=colors["text"]
        )

        self.console_output.configure(
            bg=colors["console_bg"],
            fg=colors["console_text"],
            insertbackground=colors["console_text"]
        )

        if self.dark_mode_var.get():
            self.dark_mode_button.configure(
                text="Dark Mode: ON",
                bg="#3a7afe",
                fg="white",
                activebackground="#2454b8"
            )
        else:
            self.dark_mode_button.configure(
                text="Dark Mode: OFF",
                bg="#d6d6d6",
                fg="#111111",
                activebackground="#c7c7c7"
            )

    def build_main_gui(self):
        self.main_container = ttk.Frame(self.root, padding=15, style="App.TFrame")
        self.main_container.pack(fill="both", expand=True)

        self.top_row = ttk.Frame(self.main_container, style="App.TFrame")
        self.top_row.pack(fill="x", pady=(0, 10))

        self.dark_mode_button = tk.Button(
            self.top_row,
            text="Dark Mode: ON",
            command=self.toggle_dark_mode,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=6
        )
        self.dark_mode_button.pack(side="left")

        self.toggle_console_button = ttk.Button(
            self.top_row,
            text="Hide Console",
            command=self.toggle_console_visibility,
            style="App.TButton"
        )
        self.toggle_console_button.pack(side="right")

        self.split_pane = ttk.PanedWindow(
            self.main_container,
            orient="horizontal"
        )
        self.split_pane.pack(fill="both", expand=True)

        self.control_frame = ttk.Frame(self.split_pane, padding=15, style="Panel.TFrame")
        self.console_frame = ttk.Frame(self.split_pane, padding=15, style="Panel.TFrame")

        self.split_pane.add(self.control_frame, weight=1)
        self.split_pane.add(self.console_frame, weight=1)

        self.build_control_panel()
        self.build_console_panel()

    def build_control_panel(self):
        ttk.Label(
            self.control_frame,
            text="Pepper Control Panel",
            font=("Arial", 18, "bold"),
            style="Panel.TLabel"
        ).pack(anchor="w", pady=(0, 15))

        config_text = (
            f"Writer: {self.config['writer_model']} | "
            f"Judge: {self.config['judge_model']}"
        )

        ttk.Label(
            self.control_frame,
            text=config_text,
            style="Muted.TLabel"
        ).pack(anchor="w", pady=(0, 15))

        volume_row = ttk.Frame(self.control_frame, style="Panel.TFrame")
        volume_row.pack(fill="x", pady=(0, 5))

        ttk.Label(
            volume_row,
            text="Volume",
            style="Panel.TLabel"
        ).pack(side="left")

        self.volume_percent_label = ttk.Label(
            volume_row,
            text="50%",
            style="Panel.TLabel"
        )
        self.volume_percent_label.pack(side="right")

        self.volume_slider = ttk.Scale(
            self.control_frame,
            from_=0,
            to=100,
            variable=self.volume_var,
            orient="horizontal",
            command=self.update_volume,
            style="App.Horizontal.TScale"
        )
        self.volume_slider.pack(fill="x", pady=(0, 20))

        ttk.Label(
            self.control_frame,
            text="Heard:",
            style="Panel.TLabel"
        ).pack(anchor="w")

        self.heard_box = tk.Text(
            self.control_frame,
            height=5,
            wrap="word",
            state="disabled",
            relief="flat",
            borderwidth=8
        )
        self.heard_box.pack(fill="x", pady=(5, 15))

        ttk.Label(
            self.control_frame,
            text="Reply:",
            style="Panel.TLabel"
        ).pack(anchor="w")

        self.reply_box = tk.Text(
            self.control_frame,
            height=7,
            wrap="word",
            state="disabled",
            relief="flat",
            borderwidth=8
        )
        self.reply_box.pack(fill="both", expand=True, pady=(5, 15))

        ttk.Label(
            self.control_frame,
            text="User Input:",
            style="Panel.TLabel"
        ).pack(anchor="w")

        input_row = ttk.Frame(self.control_frame, style="Panel.TFrame")
        input_row.pack(fill="x", pady=(5, 0))

        self.user_input_entry = tk.Entry(
            input_row,
            textvariable=self.user_input_var,
            relief="flat",
            font=("Arial", 11)
        )
        self.user_input_entry.pack(side="left", fill="x", expand=True, ipady=7)

        self.send_button = ttk.Button(
            input_row,
            text="Send",
            command=self.send_user_input,
            style="App.TButton"
        )
        self.send_button.pack(side="right", padx=(10, 0))

        self.user_input_entry.bind("<Return>", lambda event: self.send_user_input())

    def build_console_panel(self):
        ttk.Label(
            self.console_frame,
            text="Console Output",
            font=("Arial", 18, "bold"),
            style="Panel.TLabel"
        ).pack(anchor="w", pady=(0, 15))

        self.console_output = tk.Text(
            self.console_frame,
            wrap="word",
            state="disabled",
            relief="flat",
            borderwidth=8,
            font=("Consolas", 10)
        )
        self.console_output.pack(fill="both", expand=True)

        self.clear_button = ttk.Button(
            self.console_frame,
            text="Clear Console",
            command=self.clear_console,
            style="App.TButton"
        )
        self.clear_button.pack(pady=(10, 0))

    def toggle_dark_mode(self):
        self.dark_mode_var.set(not self.dark_mode_var.get())
        self.config["dark_mode"] = self.dark_mode_var.get()
        self.apply_theme()

    def toggle_console_visibility(self):
        if self.console_visible:
            self.split_pane.forget(self.console_frame)
            self.console_visible = False
            self.toggle_console_button.config(text="Show Console")
        else:
            self.split_pane.add(self.console_frame, weight=1)
            self.console_visible = True
            self.toggle_console_button.config(text="Hide Console")

    def redirect_console_output(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        redirector = ConsoleRedirector(
            output_queue=self.console_queue
        )

        sys.stdout = redirector
        sys.stderr = redirector

    def poll_console_queue(self):
        while not self.console_queue.empty():
            text = self.console_queue.get_nowait()
            self.append_console(text)

        self.root.after(100, self.poll_console_queue)

    def append_console(self, text):
        self.console_output.config(state="normal")
        self.console_output.insert(tk.END, text)
        self.console_output.see(tk.END)
        self.console_output.config(state="disabled")

    def clear_console(self):
        self.console_output.config(state="normal")
        self.console_output.delete("1.0", tk.END)
        self.console_output.config(state="disabled")

    def update_volume(self, value):
        volume = int(float(value))
        self.volume_var.set(volume)
        self.volume_percent_label.config(text=f"{volume}%")

        if self.on_volume_change:
            self.on_volume_change(volume)

    def send_user_input(self):
        user_text = self.user_input_var.get().strip()

        if not user_text:
            return

        self.user_input_var.set("")
        self.set_heard(user_text)

        if self.on_send:
            reply = self.on_send(user_text)
        else:
            reply = f"Test reply to: {user_text}"

        self.set_reply(reply)

        print(f"USER INPUT: {user_text}")
        print(f"PEPPER REPLY: {reply}")

    def set_heard(self, text):
        self.heard_box.config(state="normal")
        self.heard_box.delete("1.0", tk.END)
        self.heard_box.insert(tk.END, text)
        self.heard_box.config(state="disabled")

    def set_reply(self, text):
        self.reply_box.config(state="normal")
        self.reply_box.delete("1.0", tk.END)
        self.reply_box.insert(tk.END, text)
        self.reply_box.config(state="disabled")

    def close_all(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

        if self.on_close:
            self.on_close()

        self.root.destroy()

    def run(self):
        self.root.mainloop()
        
def start_writer_model(model_name):
    print(f"Loading writer model: {model_name}")
    # Replace with your real LLM loading logic
    return model_name


def start_judge_model(model_name):
    print(f"Loading judge model: {model_name}")
    # Replace with your real LLM loading logic
    return model_name


def handle_user_input(user_text):
    print("Processing user input...")

    # Replace this with your actual Pepper pipeline
    reply = f"Pepper received: {user_text}"

    return reply


def handle_volume_change(volume):
    print(f"Volume changed to: {volume}%")


def cleanup():
    print("Closing Pepper...")


def main():
    model_options = [
        "llama3.1:8b",
        "llama3.2:3b",
        "mistral:7b",
        "qwen2.5:7b",
        "gemma2:9b"
    ]

    setup_gui = SetupGUI(model_options)
    config = setup_gui.run()

    if config is None:
        print("Pepper startup cancelled.")
        return

    writer_model = start_writer_model(config["writer_model"])
    judge_model = start_judge_model(config["judge_model"])

    print("Startup config:")
    print(config)

    pepper_gui = PepperGUI(
        config=config,
        on_send=handle_user_input,
        on_volume_change=handle_volume_change,
        on_close=cleanup
    )

    pepper_gui.run()


if __name__ == "__main__":
    main()