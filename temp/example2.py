import tkinter as tk
from tkinter import ttk


def create_widgets():
    # Create a frame for the content of the first tab
    tab1_frame = ttk.Frame(notebook)
    notebook.add(tab1_frame, text="Tab 1")

    # Create a Label widget inside tab1_frame using grid
    label = ttk.Label(tab1_frame, text="This is a label")
    label.grid(row=0, column=0, padx=10, pady=10)

    # Create a Button widget inside tab1_frame using grid
    button = ttk.Button(tab1_frame, text="Click Me")
    button.grid(row=1, column=0, padx=10, pady=10)


# Create the main window
root = tk.Tk()
root.title("Tkinter Notebook Example")

# Create a Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create widgets for the first tab
create_widgets()

root.mainloop()
