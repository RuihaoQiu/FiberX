import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from ctypes import *


class FiberX:
    def __init__(self, root):

        # Create a style for the Notebook
        style = ttk.Style()

        # Configure the font for the Notebook tab buttons
        style.configure("TNotebook.Tab", padding=(10, 10), font=("TkDefaultFont", 20))

        self.root = root
        self.root.title("FiberX")
        self.root.geometry("1600x1200")

        plt.style.use("ggplot")

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=30, pady=30)

        self.init_tab1()
        self.init_tab2()
        self.init_tab3()

    def init_tab1(self):
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="光谱")

        # Create a frame to contain the plot
        self.plot_frame = tk.Frame(self.tab1)
        self.plot_frame.pack()

        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        (self.dot_line1,) = self.ax1.plot([], [], "-", label="Raw Data")

        self.start_button_1 = tk.Button(
            self.tab1,
            text="Load data",
            command=self.update_plot_1,
            font=("TkDefaultFont", 20),
        )
        self.start_button_1.pack(side=tk.LEFT)

    def init_tab2(self):
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="吸收")

        # Create a frame to contain the plot
        self.plot_frame = tk.Frame(self.tab2)
        self.plot_frame.pack()

        self.fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlabel("Wavelength")
        self.ax2.set_ylabel("Intensity")

        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        (self.dot_line2,) = self.ax2.plot([], [], "-", label="Raw Data")

        self.start_button_2 = tk.Button(
            self.tab2,
            text="Load data",
            command=self.update_plot_2,
            font=("TkDefaultFont", 20),
        )
        self.start_button_2.pack(side=tk.LEFT)

    def init_tab3(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="实时")

        # Create a frame to contain the plot
        self.plot_frame = tk.Frame(self.tab3)
        self.plot_frame.pack()

        self.fig3, self.ax3 = plt.subplots()
        self.ax3.set_xlabel("Wavelength")
        self.ax3.set_ylabel("Intensity")

        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.tab3)
        self.canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        (self.dot_line3,) = self.ax3.plot([], [], "-", label="Raw Data")

        self.start_button3 = tk.Button(
            self.tab3,
            text="Load data",
            command=self.update_plot_3,
            font=("TkDefaultFont", 20),
        )
        self.start_button3.pack(side=tk.LEFT)

    def update_plot_1(self):
        self.x = [1, 2, 3, 4, 5]
        self.y = [2, 3, 4, 5, 6]
        self.dot_line1.set_data(self.x, self.y)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()

    def update_plot_2(self):
        self.x = [1, 2, 3, 4, 5]
        self.y = [1, 4, 9, 16, 25]
        self.dot_line2.set_data(self.x, self.y)
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas2.draw()

    def update_plot_3(self):
        self.x = [1, 2, 3, 4, 5]
        self.y = [1, 3, 5, 7, 9]
        self.dot_line3.set_data(self.x, self.y)
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.canvas3.draw()


def main():
    root = tk.Tk()
    app = FiberX(root)
    root.mainloop()


if __name__ == "__main__":
    main()
