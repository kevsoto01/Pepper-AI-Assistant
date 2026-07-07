import tkinter as tk
from tkinter import ttk


class SimpleTemplateGUI:
    def __init__(self):
        # This creates the main application window.
        # Every Tkinter GUI needs one root window.
        self.root = tk.Tk()

        # This sets the title that appears at the top of the window.
        self.root.title("Simple GUI Template")

        # This sets the starting window size.
        # Format is "widthxheight".
        self.root.geometry("400x300")

        # This variable stores the current value of the slider.
        # IntVar is used because the slider value is a number.
        self.slider_var = tk.IntVar(value=50)

        # This variable stores whether the toggle is ON or OFF.
        # BooleanVar stores True or False.
        self.toggle_var = tk.BooleanVar(value=False)

        # This variable stores the currently selected dropdown option.
        # StringVar is used because dropdown values are text.
        self.dropdown_var = tk.StringVar(value="Option 1")

        # This list contains the choices that will appear in the dropdown menu.
        self.dropdown_options = [
            "Option 1",
            "Option 2",
            "Option 3"
        ]

        # This method builds and places all the widgets on the screen.
        self.build_ui()

    def build_ui(self):
        # This frame is a container that holds all the widgets.
        # Frames help keep the layout organized.
        main_frame = ttk.Frame(self.root, padding=10)

        # pack() places the frame inside the window.
        # fill="both" lets it stretch horizontally and vertically.
        # expand=True lets it use available extra space.
        main_frame.pack(fill="both", expand=True)

        # This label is just a title for the GUI.
        title_label = ttk.Label(
            main_frame,
            text="Simple GUI Template",
            font=("Arial", 16, "bold")
        )

        # pady adds vertical spacing under the label.
        title_label.pack(pady=(0, 20))

        # -----------------------------
        # SLIDER SECTION
        # -----------------------------

        # This label tells the user what the slider is for.
        slider_label = ttk.Label(
            main_frame,
            text="Slider Value"
        )
        slider_label.pack(anchor="w")

        # This label will show the current slider value as text.
        self.slider_value_label = ttk.Label(
            main_frame,
            text="50"
        )
        self.slider_value_label.pack(anchor="w", pady=(0, 5))

        # This creates the slider.
        # from_=0 means the lowest value is 0.
        # to=100 means the highest value is 100.
        # variable=self.slider_var connects the slider to slider_var.
        # command=self.update_slider_label runs a function whenever the slider moves.
        slider = ttk.Scale(
            main_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.slider_var,
            command=self.update_slider_label
        )
        slider.pack(fill="x", pady=(0, 20))

        # -----------------------------
        # TOGGLE SECTION
        # -----------------------------

        # This button acts like a toggle switch.
        # When clicked, it changes between ON and OFF.
        self.toggle_button = tk.Button(
            main_frame,
            text="Toggle: OFF",
            command=self.toggle_switch,
            width=15,
            bg="red",
            fg="white"
        )
        self.toggle_button.pack(pady=(0, 20))

        # -----------------------------
        # DROPDOWN SECTION
        # -----------------------------

        # This label tells the user what the dropdown is for.
        dropdown_label = ttk.Label(
            main_frame,
            text="Choose an Option"
        )
        dropdown_label.pack(anchor="w")

        # This creates the dropdown menu.
        # textvariable connects the selected value to dropdown_var.
        # values gives the dropdown its list of choices.
        # state="readonly" prevents the user from typing custom text.
        dropdown = ttk.Combobox(
            main_frame,
            textvariable=self.dropdown_var,
            values=self.dropdown_options,
            state="readonly"
        )
        dropdown.pack(fill="x", pady=(5, 20))

        # This button prints all current values to the terminal.
        # It is useful for testing the template.
        print_button = ttk.Button(
            main_frame,
            text="Print Current Values",
            command=self.print_values
        )
        print_button.pack()

    def update_slider_label(self, value):
        # Tkinter gives the slider value as a string-like number.
        # float(value) converts it to a decimal number.
        # int(...) removes the decimal part.
        slider_value = int(float(value))

        # This updates the label so the user can see the current slider value.
        self.slider_value_label.config(text=str(slider_value))

    def toggle_switch(self):
        # This gets the current toggle value.
        current_value = self.toggle_var.get()

        # This flips the toggle value.
        # If it was False, it becomes True.
        # If it was True, it becomes False.
        new_value = not current_value

        # This saves the new toggle value.
        self.toggle_var.set(new_value)

        # This changes the button appearance depending on the toggle state.
        if new_value:
            self.toggle_button.config(
                text="Toggle: ON",
                bg="green",
                fg="white"
            )
        else:
            self.toggle_button.config(
                text="Toggle: OFF",
                bg="red",
                fg="white"
            )

    def print_values(self):
        # This gets the current slider value.
        slider_value = self.slider_var.get()

        # This gets the current toggle value.
        toggle_value = self.toggle_var.get()

        # This gets the selected dropdown option.
        dropdown_value = self.dropdown_var.get()

        # This prints the values to the terminal.
        # This is where you would later connect the GUI to your real program logic.
        print("Slider value:", slider_value)
        print("Toggle value:", toggle_value)
        print("Dropdown value:", dropdown_value)

    def run(self):
        # mainloop() keeps the GUI open.
        # Without this, the window would open and immediately close.
        self.root.mainloop()


# This checks whether the file is being run directly.
# If this script is imported into another file, this part will not run automatically.
if __name__ == "__main__":
    # This creates the GUI object.
    app = SimpleTemplateGUI()

    # This starts the GUI.
    app.run()