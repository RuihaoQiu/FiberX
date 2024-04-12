import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import os
import ctypes
import random

from file_io import load_file, save_dark_file, save_ref_file

ctypes.windll.shcore.SetProcessDpiAwareness(1)
plt.style.use("ggplot")


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.dark_folder = "../data/dark/"
        self.ref_folder = "../data/reference/"

        # # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        self.setup_files()
        self.setup_buttons()
        self.setup_plots()

        # Sizegrip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(row=100, column=100, padx=(0, 3), pady=(0, 3))

    def setup_files(self):
        self.build_dark_block()
        self.build_ref_block()
        self.build_io_block()

    def setup_buttons(self):
        self.build_input_block()
        self.build_display_block()
        self.build_control_block()

    def setup_plots(self):
        self.build_plot_block()

    def build_dark_block(self):
        dark_frame = ttk.LabelFrame(self, text="暗光谱", padding=(20, 10))
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

    def build_ref_block(self):
        ref_frame = ttk.LabelFrame(self, text="参考光谱", padding=(20, 10))
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

    def build_io_block(self):
        buttons_frame = ttk.LabelFrame(self, text="保存文件", padding=(20, 10))
        buttons_frame.grid(
            row=2,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        save_dark_button = ttk.Button(
            buttons_frame,
            text="保存暗光谱",
            command=self.save_dark,
            style="Accent.TButton",
        )
        save_dark_button.grid(row=0, column=0, padx=30, pady=(0, 10), sticky="ew")

        save_ref_button = ttk.Button(
            buttons_frame,
            text="保存亮光谱",
            command=self.save_ref,
            style="Accent.TButton",
        )
        save_ref_button.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew")

    def build_input_block(self):
        input_frame = ttk.LabelFrame(self, text="设置", padding=(20, 10))
        input_frame.grid(
            row=0,
            column=1,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        label = ttk.Label(input_frame, text="Enter your input:")
        label.grid(row=0, column=0, padx=30, pady=(0, 10), sticky="ew")
        entry = ttk.Entry(input_frame)
        entry.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")

    def build_display_block(self):
        input_frame = ttk.LabelFrame(self, text="实时数据", padding=(20, 10))
        input_frame.grid(
            row=1,
            column=1,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        label = ttk.Label(input_frame, text="波峰:")
        label.grid(row=0, column=0, padx=30, pady=(0, 10), sticky="ew")
        label = ttk.Label(input_frame, text="123")
        label.grid(row=0, column=1, padx=30, pady=(0, 10), sticky="ew")

    def build_control_block(self):
        control_frame = ttk.LabelFrame(self, text="控制", padding=(20, 10))
        control_frame.grid(
            row=2,
            column=1,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        start_button = ttk.Button(
            control_frame,
            text="开始时序",
            command=self.save_dark,
            style="Accent.TButton",
        )
        start_button.grid(row=0, column=0, padx=30, pady=(0, 10), sticky="ew")

        save_button = ttk.Button(
            control_frame,
            text="保存数据",
            command=self.save_ref,
            style="Accent.TButton",
        )
        save_button.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew")

    def build_plot_block(self):
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(
            row=0,
            column=2,
            padx=(25, 10),
            pady=(25, 10),
            sticky="nsew",
            rowspan=3,
        )

        self.notebook = ttk.Notebook(self.paned)
        self.notebook.pack(fill="both", expand=True)

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()
        self.build_tab4()

    def build_tab1(self):
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="光谱")

        plot_frame = ttk.Frame(tab1)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(150, 150),
            pady=(200, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")

        canvas = FigureCanvasTkAgg(fig1, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        (dark,) = self.ax1.plot([], [], "-", label="Dark")
        (reference,) = self.ax1.plot([], [], "-", label="Reference")
        (realtime,) = self.ax1.plot([], [], "-", label="Real time")

        self.ax1.legend()

    def build_tab2(self):
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="透射")

        plot_frame = ttk.Frame(tab2)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(150, 150),
            pady=(200, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlabel("Wavelength")
        self.ax2.set_ylabel("Y")

        canvas = FigureCanvasTkAgg(fig2, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        (realtime,) = self.ax2.plot([], [], "-", label="Real time")

        self.ax2.legend()

    def build_tab3(self):
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="时序")

        plot_frame = ttk.Frame(tab3)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(150, 150),
            pady=(200, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig3, self.ax3 = plt.subplots()
        self.ax3.set_xlabel("Time")
        self.ax3.set_ylabel("Y")

        canvas = FigureCanvasTkAgg(fig3, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        (realtime,) = self.ax3.plot([], [], "-", label="Real time")

        self.ax3.legend()

    def build_tab4(self):
        tab4 = ttk.Frame(self.notebook)
        self.notebook.add(tab4, text="强度时序")

        plot_frame = ttk.Frame(tab4)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(150, 150),
            pady=(200, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig4, self.ax4 = plt.subplots()
        self.ax4.set_xlabel("Time")
        self.ax4.set_ylabel("Y")

        canvas = FigureCanvasTkAgg(fig4, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        (realtime,) = self.ax4.plot([], [], "-", label="Real time")

        self.ax4.legend()

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
        self.after(1000, self.start_real)

    def stop_real(self):
        self.running = False

    def save_absorb(self):
        pass

    def setup_tab3(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="时序")

    def setup_tab4(self):
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="强度时序")


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
