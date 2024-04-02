from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

plt.style.use("ggplot")


def make_plot(x_values, y_values):
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker=".", linestyle="-")
    ax.set_xlabel("Wave Length")
    ax.set_ylabel("Intensity")
    return fig


def create_tab_intensity(parent, x_values, y_values):
    tab = ttk.Frame(parent)
    parent.add(tab, text="光谱")
    fig = make_plot(x_values, y_values)

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
