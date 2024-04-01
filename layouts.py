import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def create_tab_with_plot(parent, text, x_values, y_values):
    tab = ttk.Frame(parent)
    parent.add(tab, text=text)

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker="o", linestyle="-")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"Plot in {text}")

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def main():
    root = tk.Tk()
    root.title("Tabbed Widget")

    # Sample data
    x_values = [1, 2, 3, 4, 5]
    y_values = [2, 3, 5, 7, 11]

    # Create a Notebook widget
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Create tabs with plots
    create_tab_with_plot(notebook, "Tab 1", x_values, y_values)
    create_tab_with_plot(notebook, "Tab 2", x_values, [y + 1 for y in y_values])

    root.mainloop()


if __name__ == "__main__":
    main()
