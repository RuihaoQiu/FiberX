import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from ctypes import *

error_code = 0
lib = cdll.LoadLibrary(
    r"C:\Users\ruihq\Desktop\ProfZ\sdk4.1\[4] USB Dome\[3] python demo for windows\SeaBreeze.dll"
)

# 打开所有光谱仪
devcount = lib.seabreeze_open_all_spectrometers(error_code)


class RealTimePlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Plot")

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # First tab: Load data and plot
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="光谱")

        # Create a frame to contain the plot
        self.plot_frame = tk.Frame(self.tab1)
        self.plot_frame.pack()

        plt.style.use("ggplot")

        self.figure, self.ax = plt.subplots()
        # Set x and y labels
        self.ax.set_xlabel("Wavelength")
        self.ax.set_ylabel("Intensity")

        # plt.subplots_adjust(
        #     top=0.925, bottom=0.16, left=0.11, right=0.90, hspace=0.2, wspace=0.2
        # )

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.tab1)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        (self.dot_line,) = self.ax.plot([], [], "-", label="Raw Data")

        self.start_button = tk.Button(
            self.tab1, text="Load dark", command=self.start_plot
        )
        self.start_button.pack(side=tk.LEFT)

    def start_plot(self):
        print("hey")


def main():
    root = tk.Tk()
    app = RealTimePlotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
