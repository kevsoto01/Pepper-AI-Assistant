import tkinter as tk


def capture_key(event):
    key_name = event.keysym

    keybind_entry.delete(0, tk.END)
    keybind_entry.insert(0, key_name)

    print(f"Captured key: {key_name}")

    return "break"


root = tk.Tk()

keybind_entry = tk.Entry(root, width=30)
keybind_entry.pack(padx=20, pady=20)

keybind_entry.insert(0, "Click here, then press a key")

keybind_entry.bind("<KeyPress>", capture_key)

root.mainloop()