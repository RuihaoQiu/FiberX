from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


plt.style.use("ggplot")


def plot_curve(x_wavelength, y_dark, y_ref, y_realtime):
    fig, ax = plt.subplots()
    ax.plot(x_wavelength, y_dark, marker=".", linestyle="-")
    ax.plot(x_wavelength, y_ref, marker=".", linestyle="-")
    ax.plot(x_wavelength, y_realtime, marker=".", linestyle="-")
    ax.set_xlabel("Wave Length")
    ax.set_ylabel("Intensity")
    ax.legend()
    return fig


def create_tab_intensity(parent, x_wavelength, y_dark, y_ref, y_realtime):
    tab = ttk.Frame(parent)
    parent.add(tab, text="光谱")
    fig = plot_curve(x_wavelength, y_dark, y_ref, y_realtime)
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
