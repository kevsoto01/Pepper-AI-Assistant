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
            **kwargs,
        )

        return widget

    def radiobutton(self, text="Option", variable=None, value=None, command=None, **kwargs):
        if variable is None:
            variable = tk.StringVar()

        widget = ttk.Radiobutton(
            self.main_frame,
            text=text,
            variable=variable,
            value=value,
            command=command,
            **kwargs,
        )

        return widget

    # INPUTS
    def entry(self, variable=None, width=25, **kwargs):
        if variable is None:
            variable = tk.StringVar()

        widget = ttk.Entry(
            self.main_frame,
            textvariable=variable,
            width=width,
            **kwargs,
        )

        return widget

    def password_entry(self, variable=None, width=25, **kwargs):
        if variable is None:
            variable = tk.StringVar()

        widget = ttk.Entry(
            self.main_frame,
            textvariable=variable,
            width=width,
            show="*",
            **kwargs,
        )

        return widget

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
            **kwargs,
        )

        return widget

    # SELECTION ELEMENTS
    def combobox(
        self,
        values=None,
        variable=None,
        width=25,
        state="readonly",
        default_to_first=True,
        **kwargs,
    ):
        """
        Build a combobox without overwriting an existing Tk variable value.

        The previous implementation always called widget.current(0), which
        replaced saved config selections whenever the launcher re-rendered.
        """
        values = list(values or [])

        if variable is None:
            variable = tk.StringVar()

        current_value = variable.get()

        if current_value and current_value not in values:
            values.insert(0, current_value)
        elif not current_value and values and default_to_first:
            variable.set(values[0])

        widget = ttk.Combobox(
            self.main_frame,
            values=values,
            textvariable=variable,
            width=width,
            state=state,
            **kwargs,
        )

        return widget

    def listbox(self, values=None, width=30, height=8, **kwargs):
        values = values or []
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
            **kwargs,
        )

        return widget

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
            **kwargs,
        )

        return widget

    def progress_bar(self, variable=None, maximum=100, mode="determinate", **kwargs):
        if variable is None:
            variable = tk.DoubleVar(value=0)

        widget = ttk.Progressbar(
            self.main_frame,
            variable=variable,
            maximum=maximum,
            mode=mode,
            **kwargs,
        )

        return widget

    # CONTAINERS
    def frame(self, **kwargs):
        return ttk.Frame(self.main_frame, **kwargs)

    def label_frame(self, text="Section", **kwargs):
        return ttk.LabelFrame(self.main_frame, text=text, **kwargs)

    def canvas(self, width=300, height=200, **kwargs):
        return tk.Canvas(self.main_frame, width=width, height=height, **kwargs)

    def paned_window(self, orient="horizontal", **kwargs):
        orient_value = tk.VERTICAL if orient == "vertical" else tk.HORIZONTAL
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
            **kwargs,
        )

    def horizontal_scrollbar(self, command=None, **kwargs):
        return ttk.Scrollbar(
            self.main_frame,
            orient="horizontal",
            command=command,
            **kwargs,
        )

    # TREE / TABLE
    def treeview(self, columns=None, show="headings", height=8, **kwargs):
        columns = columns or []
        widget = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show=show,
            height=height,
            **kwargs,
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
