import tkinter as tk
from tkinter import ttk

class LocalUIElementTemplateBuilder:
    def __init__(self, main_frame):
        self.main_frame = main_frame
        
    def label(self, text="Label", **kwargs):
        return ttk.Label(self.main_frame, text=text, **kwargs)

    def title_label(self, text="Title", **kwargs):
        return ttk.Label(self.main_frame, text=text, font=("Arial", 18, "bold"), **kwargs)

    def subtitle_label(self, text="Subtitle", **kwargs):
        return ttk.Label(self.main_frame, text=text, font=("Arial", 12), **kwargs)

    def status_label(self, text="Status: Idle", **kwargs):
        return ttk.Label(self.main_frame, text=text, **kwargs)

    # BUTTONS
    def button(self, text="Button", command=None, **kwargs):
        return ttk.Button(self.main_frame, text=text, command=command, **kwargs)

    def checkbutton(self, text="Checkbutton", variable=None, command=None, **kwargs):
        if variable is None:
            variable = tk.BooleanVar()

        widget = ttk.Checkbutton(
            self.main_frame,
            text=text,
            variable=variable,
            command=command,
            **kwargs
        )

        return widget, variable

    def radiobutton(self, text="Option", variable=None, value=None, command=None, **kwargs):
        if variable is None:
            variable = tk.StringVar()

        widget = ttk.Radiobutton(
            self.main_frame,
            text=text,
            variable=variable,
            value=value,
            command=command,
            **kwargs
        )

        return widget, variable

    # INPUTS
    def entry(self, variable=None, width=25, **kwargs):
        if variable is None:
            variable = tk.StringVar()

        widget = ttk.Entry(
            self.main_frame,
            textvariable=variable,
            width=width,
            **kwargs
        )

        return widget, variable

    def password_entry(self, variable=None, width=25, **kwargs):
        if variable is None:
            variable = tk.StringVar()

        widget = ttk.Entry(
            self.main_frame,
            textvariable=variable,
            width=width,
            show="*",
            **kwargs
        )

        return widget, variable

    def text_box(self, width=40, height=8, **kwargs):
        return tk.Text(self.main_frame, width=width, height=height, **kwargs)

    def spinbox(self, from_=0, to=100, variable=None, width=10, **kwargs):
        if variable is None:
            variable = tk.IntVar(value=from_)

        widget = ttk.Spinbox(
            self.main_frame,
            from_=from_,
            to=to,
            textvariable=variable,
            width=width,
            **kwargs
        )

        return widget, variable

    # SELECTION ELEMENTS
    def combobox(self, values=None, variable=None, width=25, state="readonly", **kwargs):
        if values is None:
            values = []

        if variable is None:
            variable = tk.StringVar()

        widget = ttk.Combobox(
            self.main_frame,
            values=values,
            textvariable=variable,
            width=width,
            state=state,
            **kwargs
        )

        if values:
            widget.current(0)

        return widget, variable

    def listbox(self, values=None, width=30, height=8, **kwargs):
        if values is None:
            values = []

        widget = tk.Listbox(self.main_frame, width=width, height=height, **kwargs)

        for value in values:
            widget.insert(tk.END, value)

        return widget

    # SLIDERS / SCALES
    def horizontal_slider(self, from_=0, to=100, variable=None, command=None, **kwargs):
        if variable is None:
            variable = tk.DoubleVar(value=from_)

        widget = ttk.Scale(
            self.main_frame,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=variable,
            command=command,
            **kwargs
        )

        return widget, variable

    def vertical_slider(self, from_=0, to=100, variable=None, command=None, **kwargs):
        if variable is None:
            variable = tk.DoubleVar(value=from_)

        widget = ttk.Scale(
            self.main_frame,
            from_=from_,
            to=to,
            orient="vertical",
            variable=variable,
            command=command,
            **kwargs
        )

        return widget, variable

    def progress_bar(self, variable=None, maximum=100, mode="determinate", **kwargs):
        if variable is None:
            variable = tk.DoubleVar(value=0)

        widget = ttk.Progressbar(
            self.main_frame,
            variable=variable,
            maximum=maximum,
            mode=mode,
            **kwargs
        )

        return widget, variable

    # CONTAINERS
    def frame(self, **kwargs):
        return ttk.Frame(self.main_frame, **kwargs)

    def label_frame(self, text="Section", **kwargs):
        return ttk.LabelFrame(self.main_frame, text=text, **kwargs)

    def canvas(self, width=300, height=200, **kwargs):
        return tk.Canvas(self.main_frame, width=width, height=height, **kwargs)

    def paned_window(self, orient="horizontal", **kwargs):
        if orient == "vertical":
            orient_value = tk.VERTICAL
        else:
            orient_value = tk.HORIZONTAL

        return ttk.PanedWindow(self.main_frame, orient=orient_value, **kwargs)

    def notebook(self, **kwargs):
        return ttk.Notebook(self.main_frame, **kwargs)

    def tab(self, notebook_widget, text="Tab"):
        frame = ttk.Frame(notebook_widget)
        notebook_widget.add(frame, text=text)
        return frame

    # MENUS
    def menu_bar(self, root):
        menu = tk.Menu(root)
        root.config(menu=menu)
        return menu

    def menu(self, main_menu, label="Menu"):
        submenu = tk.Menu(main_menu, tearoff=False)
        main_menu.add_cascade(label=label, menu=submenu)
        return submenu

    def menu_command(self, menu, label="Command", command=None):
        menu.add_command(label=label, command=command)

    def menu_separator(self, menu):
        menu.add_separator()

    # SCROLLBARS
    def vertical_scrollbar(self, command=None, **kwargs):
        return ttk.Scrollbar(
            self.main_frame,
            orient="vertical",
            command=command,
            **kwargs
        )

    def horizontal_scrollbar(self, command=None, **kwargs):
        return ttk.Scrollbar(
            self.main_frame,
            orient="horizontal",
            command=command,
            **kwargs
        )

    # TREE / TABLE
    def treeview(self, columns=None, show="headings", height=8, **kwargs):
        if columns is None:
            columns = []

        widget = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show=show,
            height=height,
            **kwargs
        )

        for column in columns:
            widget.heading(column, text=column)
            widget.column(column, width=120)

        return widget

    # SEPARATORS
    def horizontal_separator(self, **kwargs):
        return ttk.Separator(self.main_frame, orient="horizontal", **kwargs)

    def vertical_separator(self, **kwargs):
        return ttk.Separator(self.main_frame, orient="vertical", **kwargs)

    # TK-SPECIFIC VARIABLE HELPERS
    def string_var(self, value=""):
        return tk.StringVar(value=value)

    def int_var(self, value=0):
        return tk.IntVar(value=value)

    def double_var(self, value=0.0):
        return tk.DoubleVar(value=value)

    def bool_var(self, value=False):
        return tk.BooleanVar(value=value)

# import tkinter as tk
# from tkinter import ttk


# class LocalUIElementTemplateBuilder:
#     """
#     Template builder for creating common Tkinter / ttk UI elements.

#     Every method takes `main_frame` as the first argument.
#     """

#     # -------------------------
#     # BASIC TEXT ELEMENTS
#     # -------------------------

#     def label(self, main_frame, text="Label", **kwargs):
#         return ttk.Label(main_frame, text=text, **kwargs)

#     def title_label(self, main_frame, text="Title", **kwargs):
#         return ttk.Label(main_frame, text=text, font=("Arial", 18, "bold"), **kwargs)

#     def subtitle_label(self, main_frame, text="Subtitle", **kwargs):
#         return ttk.Label(main_frame, text=text, font=("Arial", 12), **kwargs)

#     def status_label(self, main_frame, text="Status: Idle", **kwargs):
#         return ttk.Label(main_frame, text=text, **kwargs)

#     # -------------------------
#     # BUTTONS
#     # -------------------------

#     def button(self, main_frame, text="Button", command=None, **kwargs):
#         return ttk.Button(main_frame, text=text, command=command, **kwargs)

#     def checkbutton(self, main_frame, text="Checkbutton", variable=None, command=None, **kwargs):
#         if variable is None:
#             variable = tk.BooleanVar()

#         widget = ttk.Checkbutton(
#             main_frame,
#             text=text,
#             variable=variable,
#             command=command,
#             **kwargs
#         )

#         return widget, variable

#     def radiobutton(self, main_frame, text="Option", variable=None, value=None, command=None, **kwargs):
#         if variable is None:
#             variable = tk.StringVar()

#         widget = ttk.Radiobutton(
#             main_frame,
#             text=text,
#             variable=variable,
#             value=value,
#             command=command,
#             **kwargs
#         )

#         return widget, variable

#     # -------------------------
#     # INPUTS
#     # -------------------------

#     def entry(self, main_frame, variable=None, width=25, **kwargs):
#         if variable is None:
#             variable = tk.StringVar()

#         widget = ttk.Entry(
#             main_frame,
#             textvariable=variable,
#             width=width,
#             **kwargs
#         )

#         return widget, variable

#     def password_entry(self, main_frame, variable=None, width=25, **kwargs):
#         if variable is None:
#             variable = tk.StringVar()

#         widget = ttk.Entry(
#             main_frame,
#             textvariable=variable,
#             width=width,
#             show="*",
#             **kwargs
#         )

#         return widget, variable

#     def text_box(self, main_frame, width=40, height=8, **kwargs):
#         return tk.Text(main_frame, width=width, height=height, **kwargs)

#     def spinbox(self, main_frame, from_=0, to=100, variable=None, width=10, **kwargs):
#         if variable is None:
#             variable = tk.IntVar(value=from_)

#         widget = ttk.Spinbox(
#             main_frame,
#             from_=from_,
#             to=to,
#             textvariable=variable,
#             width=width,
#             **kwargs
#         )

#         return widget, variable

#     # -------------------------
#     # SELECTION ELEMENTS
#     # -------------------------

#     def dropdown(self, main_frame, values=None, variable=None, width=25, state="readonly", **kwargs):
#         if values is None:
#             values = []

#         if variable is None:
#             variable = tk.StringVar()

#         widget = ttk.Combobox(
#             main_frame,
#             values=values,
#             textvariable=variable,
#             width=width,
#             state=state,
#             **kwargs
#         )

#         if values:
#             widget.current(0)

#         return widget, variable

#     def listbox(self, main_frame, values=None, width=30, height=8, **kwargs):
#         if values is None:
#             values = []

#         widget = tk.Listbox(main_frame, width=width, height=height, **kwargs)

#         for value in values:
#             widget.insert(tk.END, value)

#         return widget

#     # -------------------------
#     # SLIDERS / SCALES
#     # -------------------------

#     def horizontal_slider(self, main_frame, from_=0, to=100, variable=None, command=None, **kwargs):
#         if variable is None:
#             variable = tk.DoubleVar(value=from_)

#         widget = ttk.Scale(
#             main_frame,
#             from_=from_,
#             to=to,
#             orient="horizontal",
#             variable=variable,
#             command=command,
#             **kwargs
#         )

#         return widget, variable

#     def vertical_slider(self, main_frame, from_=0, to=100, variable=None, command=None, **kwargs):
#         if variable is None:
#             variable = tk.DoubleVar(value=from_)

#         widget = ttk.Scale(
#             main_frame,
#             from_=from_,
#             to=to,
#             orient="vertical",
#             variable=variable,
#             command=command,
#             **kwargs
#         )

#         return widget, variable

#     def progress_bar(self, main_frame, variable=None, maximum=100, mode="determinate", **kwargs):
#         if variable is None:
#             variable = tk.DoubleVar(value=0)

#         widget = ttk.Progressbar(
#             main_frame,
#             variable=variable,
#             maximum=maximum,
#             mode=mode,
#             **kwargs
#         )

#         return widget, variable

#     # -------------------------
#     # CONTAINERS
#     # -------------------------

#     def frame(self, main_frame, **kwargs):
#         return ttk.Frame(main_frame, **kwargs)

#     def label_frame(self, main_frame, text="Section", **kwargs):
#         return ttk.LabelFrame(main_frame, text=text, **kwargs)

#     def canvas(self, main_frame, width=300, height=200, **kwargs):
#         return tk.Canvas(main_frame, width=width, height=height, **kwargs)

#     def paned_window(self, main_frame, orient="horizontal", **kwargs):
#         if orient == "vertical":
#             orient_value = tk.VERTICAL
#         else:
#             orient_value = tk.HORIZONTAL

#         return ttk.PanedWindow(main_frame, orient=orient_value, **kwargs)

#     def notebook(self, main_frame, **kwargs):
#         return ttk.Notebook(main_frame, **kwargs)

#     def tab(self, notebook_widget, text="Tab"):
#         frame = ttk.Frame(notebook_widget)
#         notebook_widget.add(frame, text=text)
#         return frame

#     # -------------------------
#     # MENUS
#     # -------------------------

#     def menu_bar(self, root):
#         menu = tk.Menu(root)
#         root.config(menu=menu)
#         return menu

#     def menu(self, main_menu, label="Menu"):
#         submenu = tk.Menu(main_menu, tearoff=False)
#         main_menu.add_cascade(label=label, menu=submenu)
#         return submenu

#     def menu_command(self, menu, label="Command", command=None):
#         menu.add_command(label=label, command=command)

#     def menu_separator(self, menu):
#         menu.add_separator()

#     # -------------------------
#     # SCROLLBARS
#     # -------------------------

#     def vertical_scrollbar(self, main_frame, command=None, **kwargs):
#         return ttk.Scrollbar(
#             main_frame,
#             orient="vertical",
#             command=command,
#             **kwargs
#         )

#     def horizontal_scrollbar(self, main_frame, command=None, **kwargs):
#         return ttk.Scrollbar(
#             main_frame,
#             orient="horizontal",
#             command=command,
#             **kwargs
#         )

#     # -------------------------
#     # TREE / TABLE
#     # -------------------------

#     def treeview(self, main_frame, columns=None, show="headings", height=8, **kwargs):
#         if columns is None:
#             columns = []

#         widget = ttk.Treeview(
#             main_frame,
#             columns=columns,
#             show=show,
#             height=height,
#             **kwargs
#         )

#         for column in columns:
#             widget.heading(column, text=column)
#             widget.column(column, width=120)

#         return widget

#     # -------------------------
#     # SEPARATORS
#     # -------------------------

#     def horizontal_separator(self, main_frame, **kwargs):
#         return ttk.Separator(main_frame, orient="horizontal", **kwargs)

#     def vertical_separator(self, main_frame, **kwargs):
#         return ttk.Separator(main_frame, orient="vertical", **kwargs)

#     # -------------------------
#     # TK-SPECIFIC VARIABLE HELPERS
#     # -------------------------

#     def string_var(self, value=""):
#         return tk.StringVar(value=value)

#     def int_var(self, value=0):
#         return tk.IntVar(value=value)

#     def double_var(self, value=0.0):
#         return tk.DoubleVar(value=value)

#     def bool_var(self, value=False):
#         return tk.BooleanVar(value=value)
    
# def example_usage():
#     import tkinter as tk
#     from tkinter import ttk
    
    
#     root = tk.Tk()
#     root.title("UI Builder Test")
#     root.geometry("400x400")
    
#     main_frame = ttk.Frame(root, padding=20)
#     main_frame.pack(fill="both", expand=True)
    
#     builder = LocalUIElementTemplateBuilder()
    
#     title = builder.title_label(main_frame, "Local UI")
#     title.pack(pady=10)
    
#     volume_slider, volume_var = builder.horizontal_slider(
#         main_frame,
#         from_=0,
#         to=100
#     )
#     volume_slider.pack(fill="x", pady=10)
    
#     dropdown, dropdown_var = builder.dropdown(
#         main_frame,
#         values=["Idle", "Listening", "Thinking", "Speaking"]
#     )
#     dropdown.pack(pady=10)
    
#     toggle, toggle_var = builder.checkbutton(
#         main_frame,
#         text="Enable Pepper"
#     )
#     toggle.pack(pady=10)
    
#     root.mainloop()
    
# """
# This class is a template builder for common Tkinter UI elements.

# Each method should create and return one type of UI widget.

# Every widget-building method should take main_frame as an argument so the element knows where it belongs in the interface.

# The goal of this class is not to control the full application logic. Its job is only to provide reusable templates for building UI elements consistently.

# Text elements:

# * Label: basic text used for names, descriptions, instructions, or static information.
# * Title Label: larger heading text used at the top of a page or major section.
# * Subtitle Label: smaller supporting text used under a title or section heading.
# * Status Label: text that can update based on the app state, such as idle, listening, thinking, or speaking.

# Button elements:

# * Button: clickable action used to start, stop, save, reset, or trigger a function.
# * Checkbutton: true/false toggle used for settings that are either on or off.
# * Radiobutton: one option from a group, used when only one choice should be active at a time.

# Input elements:

# * Entry: single-line text input used for short values.
# * Password Entry: hidden single-line input used for passwords, tokens, or secret keys.
# * Text Box: multi-line text input used for longer text, prompts, transcripts, or logs.
# * Spinbox: number selector with up and down arrows, used for controlled numeric values.

# Selection elements:

# * Dropdown: compact list of options where the user selects one value.
# * Listbox: visible list of multiple options, useful when many items should be shown at once.

# Slider and progress elements:

# * Horizontal Slider: left-to-right adjustable value, useful for volume, speed, sensitivity, or brightness.
# * Vertical Slider: up-and-down adjustable value, useful for mixer-style controls.
# * Progress Bar: visual indicator for loading, processing, or completion progress.

# Container elements:

# * Frame: basic container used to group widgets together.
# * Label Frame: titled container used for named sections like Audio Settings or Assistant State.
# * Canvas: drawing area used for custom visuals, waveforms, animations, or status indicators.
# * Paned Window: resizable split layout used when two areas share the screen.
# * Notebook: tabbed interface used when the UI needs multiple pages.
# * Tab: one page inside a notebook.

# Menu elements:

# * Menu Bar: top-level application menu.
# * Menu: dropdown section inside the menu bar.
# * Menu Command: clickable action inside a menu.
# * Menu Separator: divider used to separate groups of menu commands.

# Scroll elements:

# * Vertical Scrollbar: scrolls content up and down.
# * Horizontal Scrollbar: scrolls content left and right.

# Table elements:

# * Treeview: table or hierarchical list used for structured data like devices, statuses, settings, or logs.

# Separator elements:

# * Horizontal Separator: horizontal divider used to separate sections.
# * Vertical Separator: vertical divider used to separate columns.

# Variable helpers:

# * String Variable: stores text connected to widgets.
# * Integer Variable: stores whole numbers connected to widgets.
# * Double Variable: stores decimal numbers connected to widgets.
# * Boolean Variable: stores true/false values connected to widgets.

# Overall purpose:
# This class keeps UI element creation organized, reusable, and separate from the main app controller logic.

# """