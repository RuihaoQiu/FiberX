import tkinter as tk
from tkinter import ttk
from tabs import create_tab_ration
from intensity import create_tab_intensity


def main():
    root = tk.Tk()
    root.title("FiberX")

    # Sample data
    x_values = [1, 2, 3, 4, 5]
    y_values = [2, 3, 5, 7, 11]
    y_dark = [2, 3, 5, 7, 11]
    y_ref = [12, 13, 15, 17, 21]
    y_real = [7, 8, 10, 12, 16]

    # Create a Notebook widget
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Create tabs with plots
    create_tab_intensity(notebook, x_values, y_dark, y_ref, y_real)
    create_tab_ration(notebook, x_values, [y + 1 for y in y_values])

    style = ttk.Style()
    style.configure("TNotebook.Tab", padding=(20, 10), font=(14))
    root.mainloop()


if __name__ == "__main__":
    main()
