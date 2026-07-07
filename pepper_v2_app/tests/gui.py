import tkinter as tk
from tkinter import ttk


class VariableModifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Variable Modifier GUI")
        self.root.geometry("600x620")

        # Variables
        self.slider_var = tk.IntVar(value=50)
        self.dropdown_1_var = tk.StringVar(value="Option A")
        self.dropdown_2_var = tk.StringVar(value="Low")
        self.text_var = tk.StringVar(value="Example text")
        self.toggle_var = tk.BooleanVar(value=False)

        self.build_ui()

    def build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.controls_tab = ttk.Frame(self.notebook, padding=20)
        self.console_tab = ttk.Frame(self.notebook, padding=20)

        self.notebook.add(self.controls_tab, text="Controls")
        self.notebook.add(self.console_tab, text="Console Output")

        self.build_controls_tab()
        self.build_console_tab()

    def build_controls_tab(self):
        # Slider row
        slider_row = ttk.Frame(self.controls_tab)
        slider_row.pack(fill="x", pady=(0, 5))

        ttk.Label(slider_row, text="Slider Variable").pack(side="left")

        self.slider_percent_label = ttk.Label(slider_row, text="50%")
        self.slider_percent_label.pack(side="right")

        self.slider = ttk.Scale(
            self.controls_tab,
            from_=0,
            to=100,
            variable=self.slider_var,
            orient="horizontal",
            command=self.update_slider_label
        )
        self.slider.pack(fill="x", pady=5)

        # Dropdown 1
        ttk.Label(self.controls_tab, text="Dropdown 1").pack(anchor="w", pady=(15, 0))

        self.dropdown_1 = ttk.Combobox(
            self.controls_tab,
            textvariable=self.dropdown_1_var,
            values=["Option A", "Option B", "Option C"],
            state="readonly"
        )
        self.dropdown_1.pack(fill="x", pady=5)

        # Dropdown 2
        ttk.Label(self.controls_tab, text="Dropdown 2").pack(anchor="w", pady=(15, 0))

        self.dropdown_2 = ttk.Combobox(
            self.controls_tab,
            textvariable=self.dropdown_2_var,
            values=["Low", "Medium", "High"],
            state="readonly"
        )
        self.dropdown_2.pack(fill="x", pady=5)

        # Text box
        ttk.Label(self.controls_tab, text="Text Box").pack(anchor="w", pady=(15, 0))

        self.text_entry = ttk.Entry(
            self.controls_tab,
            textvariable=self.text_var
        )
        self.text_entry.pack(fill="x", pady=5)

        # Big toggle button
        self.toggle_button = tk.Button(
            self.controls_tab,
            text="FALSE",
            font=("Arial", 18, "bold"),
            height=2,
            bg="red",
            fg="white",
            activebackground="darkred",
            activeforeground="white",
            command=self.toggle_button_state
        )
        self.toggle_button.pack(fill="x", pady=20)

        # Submit button
        self.submit_button = ttk.Button(
            self.controls_tab,
            text="Update Variables",
            command=self.submit_values
        )
        self.submit_button.pack(pady=10)

        # Heard output
        ttk.Label(self.controls_tab, text="Heard:").pack(anchor="w", pady=(10, 0))

        self.heard_output = tk.Text(
            self.controls_tab,
            height=3,
            wrap="word",
            state="disabled"
        )
        self.heard_output.pack(fill="x", pady=5)

        # Reply output
        ttk.Label(self.controls_tab, text="Reply:").pack(anchor="w", pady=(10, 0))

        self.reply_output = tk.Text(
            self.controls_tab,
            height=3,
            wrap="word",
            state="disabled"
        )
        self.reply_output.pack(fill="x", pady=5)

    def build_console_tab(self):
        ttk.Label(self.console_tab, text="Console Output:").pack(anchor="w")

        self.console_output = tk.Text(
            self.console_tab,
            height=25,
            wrap="word",
            state="disabled"
        )
        self.console_output.pack(fill="both", expand=True, pady=5)

        self.clear_button = ttk.Button(
            self.console_tab,
            text="Clear Console",
            command=self.clear_console
        )
        self.clear_button.pack(pady=10)

    def update_slider_label(self, value):
        int_value = int(float(value))
        self.slider_var.set(int_value)
        self.slider_percent_label.config(text=f"{int_value}%")

    def toggle_button_state(self):
        current_value = self.toggle_var.get()
        new_value = not current_value
        self.toggle_var.set(new_value)

        if new_value is True:
            self.toggle_button.config(
                text="TRUE",
                bg="green",
                activebackground="darkgreen"
            )
        else:
            self.toggle_button.config(
                text="FALSE",
                bg="red",
                activebackground="darkred"
            )

    def submit_values(self):
        slider_value = int(self.slider_var.get())
        dropdown_1_value = self.dropdown_1_var.get()
        dropdown_2_value = self.dropdown_2_var.get()
        text_value = self.text_var.get()
        toggle_value = self.toggle_var.get()

        heard_text = (
            f"I heard slider={slider_value}%, "
            f"dropdown_1={dropdown_1_value}, "
            f"dropdown_2={dropdown_2_value}, "
            f"text='{text_value}', "
            f"toggle={toggle_value}"
        )

        reply_text = (
            f"Using {dropdown_1_value} mode at {dropdown_2_value} level. "
            f"Toggle is currently {toggle_value}."
        )

        console_text = (
            "UPDATED VARIABLES\n"
            "-----------------\n"
            f"Slider: {slider_value}%\n"
            f"Dropdown 1: {dropdown_1_value}\n"
            f"Dropdown 2: {dropdown_2_value}\n"
            f"Text Box: {text_value}\n"
            f"Toggle: {toggle_value}\n\n"
        )

        self.set_text_output(self.heard_output, heard_text)
        self.set_text_output(self.reply_output, reply_text)
        self.append_console(console_text)

    def set_text_output(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state="disabled")

    def append_console(self, text):
        self.console_output.config(state="normal")
        self.console_output.insert(tk.END, text)
        self.console_output.see(tk.END)
        self.console_output.config(state="disabled")

    def clear_console(self):
        self.console_output.config(state="normal")
        self.console_output.delete("1.0", tk.END)
        self.console_output.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = VariableModifierGUI(root)
    root.mainloop()