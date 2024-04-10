import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import os
import ctypes

from file_io import load_file, save_dark_file, save_ref_file

ctypes.windll.shcore.SetProcessDpiAwareness(1)
plt.style.use("ggplot")


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.dark_folder = "../data/dark/"
        self.ref_folder = "../data/reference/"

        # Make the app responsive
        for index in [0, 1]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(
            row=0, column=0, pady=(5, 5), sticky="nsew", rowspan=3, columnspan=3
        )

        # Notebook, pane
        self.pane = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane, weight=3)

        # Notebook, pane
        self.notebook = ttk.Notebook(self.pane)
        self.notebook.pack(fill="both", expand=True)

        # Create widgets :)
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()

        # Sizegrip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(row=100, column=100, padx=(0, 3), pady=(0, 3))

    def setup_tab1(self):
        # Tab #1
        self.tab1 = ttk.Frame(self.notebook)
        for index in [0, 1, 2]:
            self.tab1.columnconfigure(index=index, weight=1)
            self.tab1.rowconfigure(index=index, weight=1)
        self.notebook.add(self.tab1, text="光谱")

        # dark frame
        dark_frame = ttk.LabelFrame(self.tab1, text="暗光谱", padding=(20, 10))
        dark_frame.grid(
            row=0,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        var = tk.StringVar()
        filenames = os.listdir(self.dark_folder)
        for file in filenames:
            b = ttk.Checkbutton(
                dark_frame,
                text=file,
                variable=var,
                onvalue=file,
                command=lambda var=var: self.load_dark(var),
            )
            b.pack(anchor=tk.W)

        # reference frame
        ref_frame = ttk.LabelFrame(self.tab1, text="参考光谱", padding=(20, 10))
        ref_frame.grid(
            row=1,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        var = tk.StringVar()
        filenames = os.listdir(self.ref_folder)
        for file in filenames:
            b = ttk.Checkbutton(
                ref_frame,
                text=file,
                variable=var,
                onvalue=file,
                command=lambda var=var: self.load_ref(var),
            )
            b.pack(anchor=tk.W)

        # Create a Frame for buttons
        self.buttons_frame = ttk.Frame(self.tab1, padding=(0, 0, 0, 10))
        self.buttons_frame.grid(row=2, column=0, padx=10, pady=(30, 10), sticky="nsew")
        self.buttons_frame.columnconfigure(index=0, weight=1)

        self.start_button = ttk.Button(
            self.buttons_frame,
            text="开始",
            command=self.start_real,
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="ew")

        self.stop_button = ttk.Button(
            self.buttons_frame,
            text="结束",
            command=self.stop_real,
        )
        self.stop_button.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")

        self.save_dark_button = ttk.Button(
            self.buttons_frame,
            text="保存暗光谱",
            command=self.save_dark,
        )
        self.save_dark_button.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")

        self.save_ref_button = ttk.Button(
            self.buttons_frame,
            text="保存亮光谱",
            command=self.save_ref,
        )
        self.save_ref_button.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="ew")

        # plot frame
        self.plot_frame = ttk.Frame(self.tab1)
        self.plot_frame.grid(
            row=0,
            column=1,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
            rowspan=3,
            columnspan=3,
        )

        self.fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.plot_frame)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas1.draw()

        (self.dark,) = self.ax1.plot([], [], "-", label="Dark")
        (self.reference,) = self.ax1.plot([], [], "-", label="Reference")
        (self.realtime,) = self.ax1.plot([], [], "-", label="Real time")

        self.ax1.legend()

    def load_dark(self, file_path):
        x, y = load_file(self.dark_folder + file_path.get())
        self.dark.set_data(x, y)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()

    def load_ref(self, file_path):
        x, y = load_file(self.ref_folder + file_path.get())
        self.reference.set_data(x, y)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()

    def save_dark(self):
        save_dark_file(self.x, self.y)

    def save_ref(self):
        save_ref_file(self.x, self.y)

    def start_real(self):
        self.x = [1, 2, 3, 4, 5]
        self.y = [random.uniform(1, 10) for _ in range(5)]
        self.realtime.set_data(self.x, self.y)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()
        self.root.after(1000, self.update_real)

    def stop_real(self):
        self.runing = False

    def setup_tab2(self):
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Tab 2")

    def setup_tab3(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Tab 3")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("")
    root.geometry("1600x800")

    root.tk.call("source", "azure/azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))

    root.mainloop()
