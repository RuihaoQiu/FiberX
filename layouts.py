import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def create_tab_intensity(parent, x_values, y_values):
    tab = ttk.Frame(parent)
    parent.add(tab, text="光谱")

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker=".", linestyle="-")
    ax.set_xlabel("Wave Length")
    ax.set_ylabel("Intensity")

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def create_tab_ration(parent, x_values, y_values):
    tab = ttk.Frame(parent)
    parent.add(tab, text="吸收")

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker=".", linestyle="-")
    ax.set_xlabel("Wave Length")
    ax.set_ylabel("Ration")

    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    window_size = (1280, 960)
    tab.winfo_toplevel().geometry(f"{window_size[0]}x{window_size[1]}")


def main():
    root = tk.Tk()
    root.title("FiberX")

    # Sample data
    x_values = [1, 2, 3, 4, 5]
    y_values = [2, 3, 5, 7, 11]

    plt.style.use("ggplot")

    # Create a Notebook widget
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Create tabs with plots
    create_tab_intensity(notebook, x_values, y_values)
    create_tab_ration(notebook, x_values, [y + 1 for y in y_values])

    style = ttk.Style()
    style.configure("TNotebook.Tab", padding=(20, 10), font=(14))
    root.mainloop()


if __name__ == "__main__":
    main()
