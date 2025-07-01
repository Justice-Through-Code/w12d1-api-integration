import tkinter as tk
from tkinter import ttk

def show_data_gui(data):
    root = tk.Tk()
    root.title("Weather Readings")

    tree = ttk.Treeview(root, columns=list(data[0].keys()), show="headings")
    for col in data[0].keys():
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for row in data:
        tree.insert("", "end", values=list(row.values()))

    tree.pack(expand=True, fill="both")
    root.mainloop()

readings = db.get_recent_readings("New York", "US")
if readings:
    show_data_gui(readings)