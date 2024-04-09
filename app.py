import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from ctypes import *
import os

from file_io import load_file, save_file_dark, save_file_bright


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
        plt.rcParams.update(
            {
                "axes.labelsize": 20,
                "xtick.labelsize": 18,
                "ytick.labelsize": 18,
                "legend.fontsize": 18,
                "lines.linewidth": 3,
            }
        )

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
        self.plot_frame.pack(side=tk.RIGHT)

        button_frame = tk.Frame(self.tab1)
        button_frame.pack(side=tk.LEFT, padx=10)

        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        (self.dark,) = self.ax1.plot([], [], "-", label="Dark")
        (self.reference,) = self.ax1.plot([], [], "-", label="Reference")
        (self.realtime,) = self.ax1.plot([], [], "-", label="Real time")

        self.ax1.legend()

        # Create a button frame

        label = tk.Label(button_frame, text="暗光谱:")
        label.pack(anchor=tk.W)

        var = tk.StringVar()
        dark_folder = "../data/dark/"
        filenames = os.listdir(dark_folder)
        for file in filenames:
            b = tk.Checkbutton(
                button_frame,
                text=file,
                variable=var,
                onvalue=file,
                command=lambda var=var: self.load_dark(var),
            )
            b.deselect()
            b.pack(anchor=tk.W)

        label = tk.Label(button_frame, text="参考光谱:")
        label.pack(anchor=tk.W)

        var = tk.StringVar()
        ref_folder = "../data/reference/"
        filenames = os.listdir(ref_folder)
        for file in filenames:
            b = tk.Checkbutton(
                button_frame,
                text=file,
                variable=var,
                onvalue=file,
                command=lambda var=var: self.load_ref(var),
            )
            b.deselect()
            b.pack(anchor=tk.W)

        # self.load_dark_botton = tk.Button(
        #     self.tab1,
        #     text="加载暗光谱",
        #     command=self.load_dark,
        #     font=("TkDefaultFont", 20),
        # )
        # self.load_dark_botton.pack(side=tk.LEFT)

        # self.load_ref_botton = tk.Button(
        #     self.tab1,
        #     text="加载基础光谱",
        #     command=self.load_ref,
        #     font=("TkDefaultFont", 20),
        # )
        # self.load_ref_botton.pack(side=tk.LEFT)

        self.load_real_botton = tk.Button(
            self.tab1,
            text="实时光谱",
            command=self.update_real,
            font=("TkDefaultFont", 20),
        )
        self.load_real_botton.pack(side=tk.LEFT)

        self.save_dark_botton = tk.Button(
            self.tab1,
            text="保存暗光谱",
            command=self.save_dark,
            font=("TkDefaultFont", 20),
        )
        self.save_dark_botton.pack(side=tk.LEFT)

        self.save_ref_botton = tk.Button(
            self.tab1,
            text="保存基础光谱",
            command=self.save_ref,
            font=("TkDefaultFont", 20),
        )
        self.save_ref_botton.pack(side=tk.LEFT)

        # check_button = tk.Button(
        #     self.tab1,
        #     text="Checklist",
        #     command=self.load_dark,
        #     font=("TkDefaultFont", 20),
        # )
        # check_button.pack(pady=5)

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

    def load_dark(self, file_path):
        folder = "../data/dark/"
        x, y = load_file(folder + file_path.get())
        self.dark.set_data(x, y)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()

    def load_ref(self, file_path):
        folder = "../data/dark/"
        x, y = load_file(folder + file_path.get())
        self.reference.set_data(x, y)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()

    def update_real(self):
        self.x = [1, 2, 3, 4, 5]
        self.y = [random.uniform(1, 10) for _ in range(5)]
        self.realtime.set_data(self.x, self.y)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()
        self.root.after(1000, self.update_real)

    def save_dark(self):
        save_file_dark(self.x, self.y)

    def save_ref(self):
        save_file_bright(self.x, self.y)

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
