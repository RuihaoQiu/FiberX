import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

import os
import ctypes
import random
import pandas as pd
import openpyxl
import numpy as np
from shapely.geometry import Polygon
from scipy.ndimage import gaussian_filter1d

from device_io import SignalGenerator, resource_path
from file_io import (
    load_file,
    save_dark_file,
    save_bright_file,
    make_results_file,
    make_results_path,
)

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ctypes.windll.kernel32.SetDllDirectoryW(None)

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.figsize": (10.1, 6.6),
        "figure.autolayout": True,
        "lines.linewidth": 2.0,
        "lines.markersize": 10.0,
    }
)


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)
        self.running = True
        self.ts_running = True
        self.int_time = 200
        self.sample_time = 1000
        self.diff = 25
        self.ini_position = 700
        self.position = None
        self.min_idx = None
        self.min_idx_display = None
        self.fix_minimum = False
        self.centroid_x, self.centroid_y = None, None
        self.intensities = []
        self.intensities_sm = []
        self.mins = []
        self.centroids = []
        self.centroids_sm = []

        self.init_absorb = False
        self.init_plots = False

        self.x_dark = []
        self.y_dark = []
        self.x_ref = []
        self.y_ref = []
        self.y_refs = []
        self.y_darks = []

        self.x_ab = []
        self.y_abs = []

        self.dark_file, self.bright_file = None, None

        if os.path.exists("data"):
            self.folder_path = "data"
            self.dark_folder = os.path.join(self.folder_path, "dark")
            self.bright_folder = os.path.join(self.folder_path, "bright")
            self.results_folder = os.path.join(self.folder_path, "results")
        else:
            self.folder_path = None
            self.dark_folder = None
            self.bright_folder = None
            self.results_folder = None

        # self.df = pd.read_csv("../time_samples.csv")

        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white")

        self.build_input_block()
        self.build_dark_block()
        self.build_bright_block()
        self.build_control_block()
        self.build_display_block()
        self.build_plot_block()

    def build_input_block(self):
        input_frame = ttk.LabelFrame(self, text="设置", padding=(20, 10))
        input_frame.grid(
            row=0,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        label = ttk.Label(input_frame, text="积分时间(ms):")
        label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.int_entry = ttk.Entry(input_frame, width=10)
        self.int_entry.insert(0, self.int_time)
        self.int_entry.grid(row=0, column=1, padx=(10, 50), pady=(0, 10), sticky="ew")

        label = ttk.Label(input_frame, text="采样时间(ms):")
        label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.sample_entry = ttk.Entry(input_frame, width=10)
        self.sample_entry.insert(0, self.sample_time)
        self.sample_entry.grid(
            row=1, column=1, padx=(10, 50), pady=(0, 10), sticky="ew"
        )

        select_button = ttk.Button(
            input_frame,
            text="选择路径",
            command=self.select_folder,
            style="Accent.TButton",
        )
        select_button.grid(
            row=2, column=0, padx=(10, 50), pady=(10, 10), columnspan=2, sticky="ew"
        )

        start_button = ttk.Button(
            input_frame,
            text="开始",
            command=self.start_real,
            style="Accent.TButton",
        )
        start_button.grid(
            row=3, column=0, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        stop_button = ttk.Button(
            input_frame,
            text="暂停",
            command=self.stop_real,
            style="Accent.TButton",
        )
        stop_button.grid(
            row=3, column=1, padx=(10, 50), pady=(10, 10), columnspan=1, sticky="ew"
        )

        save_dark_button = ttk.Button(
            input_frame,
            text="保存暗光谱",
            command=self.save_dark,
            style="Accent.TButton",
        )
        save_dark_button.grid(
            row=4, column=0, padx=10, pady=(0, 10), columnspan=1, sticky="ew"
        )

        save_bright_button = ttk.Button(
            input_frame,
            text="保存亮光谱",
            command=self.save_bright,
            style="Accent.TButton",
        )
        save_bright_button.grid(
            row=4, column=1, padx=(10, 50), pady=(0, 10), columnspan=1, sticky="ew"
        )

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.dark_folder = os.path.join(self.folder_path, "dark")
        self.bright_folder = os.path.join(self.folder_path, "bright")
        self.results_folder = os.path.join(self.folder_path, "results")
        self.build_dark_block()
        self.build_bright_block()

    def init_real(self):
        int_time = int(self.int_entry.get())
        self.signal_generator = SignalGenerator(int_time=int_time)
        self.signal_generator.start()
        self.x = self.signal_generator.generate_x()
        self.y = self.signal_generator.generate_y()
        self.y_s = gaussian_filter1d(self.y, sigma=100)
        self.realtime.set_data(self.x, self.y_s)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.init_absorb = True
        self.init_ratio()

    def start_real(self):
        if self.init_absorb == False:
            self.init_real()
            self.update_real()
        else:
            self.update_real()

    def update_real(self):
        if self.running == True:
            self.x = self.signal_generator.generate_x()
            self.y = self.signal_generator.generate_y()
            self.y_s = gaussian_filter1d(self.y, sigma=100)
            self.realtime.set_data(self.x, self.y_s)
            self.canvas1.mpl_connect("scroll_event", self.on_scroll)
            self.canvas1.draw()
            self.update_ratio()
            self.after(self.int_time, self.update_real)
        else:
            self.running = True

    def stop_real(self):
        self.signal_generator.close_spectrometers()
        self.init_absorb = False
        self.running = False

    def save_dark(self):
        save_dark_file(self.x, self.y, self.dark_folder)
        self.build_dark_block()

    def save_bright(self):
        save_bright_file(self.x, self.y, self.bright_folder)
        self.build_bright_block()

    def build_dark_block(self):
        dark_frame = ttk.LabelFrame(self, text="暗光谱", padding=(20, 10))
        dark_frame.grid(
            row=1,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        var = tk.StringVar()
        if self.dark_folder:
            filenames = os.listdir(self.dark_folder)[::-1]
            for file in filenames[:4]:
                b = ttk.Checkbutton(
                    dark_frame,
                    text=file,
                    variable=var,
                    onvalue=file,
                    command=lambda var=var: self.load_dark(var),
                )
                b.pack(anchor=tk.W)
        else:
            label = ttk.Label(dark_frame, text="请选择数据文件。")
            label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")

    def load_dark(self, file_path):
        self.dark_file = os.path.join(self.dark_folder, file_path.get())
        try:
            self.x_dark, self.y_dark = load_file(self.dark_file)
            self.y_darks = gaussian_filter1d(self.y_dark, sigma=100)
            self.dark.set_data(self.x_dark, self.y_darks)
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas1.draw()
        except FileNotFoundError:
            self.dark.set_data([], [])
            self.canvas1.draw()

    def build_bright_block(self):
        ref_frame = ttk.LabelFrame(self, text="参考光谱", padding=(20, 10))
        ref_frame.grid(
            row=2,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        var = tk.StringVar()
        if self.bright_folder:
            filenames = os.listdir(self.bright_folder)[::-1]
            for file in filenames[:4]:
                b = ttk.Checkbutton(
                    ref_frame,
                    text=file,
                    variable=var,
                    onvalue=file,
                    command=lambda var=var: self.load_bright(var),
                )
                b.pack(anchor=tk.W)

    def load_bright(self, file_path):
        self.bright_file = os.path.join(self.bright_folder, file_path.get())
        try:
            self.x_ref, self.y_ref = load_file(self.bright_file)
            self.y_refs = gaussian_filter1d(self.y_ref, sigma=100)
            self.reference.set_data(self.x_ref, self.y_refs)
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas1.draw()
        except FileNotFoundError:
            self.reference.set_data([], [])
            self.canvas1.draw()

    def build_display_block(self):
        real_frame = ttk.LabelFrame(self, text="实时数据", padding=(20, 10))
        real_frame.grid(
            row=4,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        fix_button = ttk.Checkbutton(
            real_frame,
            text="最低点",
            style="Switch.TCheckbutton",
            command=self.fix_min,
        )

        fix_button.grid(
            row=1, column=0, padx=10, pady=(0, 10), columnspan=1, sticky="ew"
        )

        self.min_label = ttk.Label(real_frame, text="", font=("Arial", 18))
        self.min_label.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        label = ttk.Label(real_frame, text="质心:")
        label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.centroid_label = ttk.Label(real_frame, text="", font=("Arial", 18))
        self.centroid_label.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="ew")

    def build_control_block(self):
        control_frame = ttk.LabelFrame(self, text="控制", padding=(20, 10))
        control_frame.grid(
            row=3,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        label = ttk.Label(control_frame, text="质心范围:")
        label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.diff_entry = ttk.Entry(control_frame, width=7)
        self.diff_entry.insert(0, self.diff)
        self.diff_entry.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="ew")

        label = ttk.Label(control_frame, text="强度位置:")
        label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.position_entry = ttk.Entry(control_frame, width=7)
        self.position_entry.insert(0, self.ini_position)
        self.position_entry.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        start_button = ttk.Button(
            control_frame,
            text="开始时序",
            command=self.start_absorb,
            style="Accent.TButton",
        )
        start_button.grid(
            row=2, column=0, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        stop_button = ttk.Button(
            control_frame,
            text="暂停时序",
            command=self.stop_absorb,
            style="Accent.TButton",
        )
        stop_button.grid(
            row=2, column=1, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        clean_button = ttk.Button(
            control_frame,
            text="清除时序",
            command=self.clean_plots,
            style="Accent.TButton",
        )
        clean_button.grid(
            row=3, column=0, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        save_button = ttk.Button(
            control_frame,
            text="保存数据",
            command=lambda: self.save_data(),
            style="Accent.TButton",
        )
        save_button.grid(
            row=3, column=1, padx=10, pady=(0, 10), columnspan=1, sticky="ew"
        )

    def start_absorb(self):
        self.sample_time = int(self.sample_entry.get())
        self.diff = int(self.diff_entry.get())
        self.position = int(self.position_entry.get())
        closest_x = self.find_interval(self.x, self.position)
        self.idx_y = list(self.x).index(closest_x)
        self.update_plots()

    def clean_plots(self):
        self.times, self.centroids, self.intensities, self.mins = [], [], [], []
        self.timeseries.set_data([], [])
        self.canvas3.draw()
        self.intensity.set_data([], [])
        self.canvas4.draw()
        self.lowest.set_data([], [])
        self.canvas5.draw()

    def build_plot_block(self):
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(
            row=0,
            column=1,
            padx=(25, 25),
            pady=(25, 10),
            sticky="nsew",
            rowspan=5,
        )

        self.notebook = ttk.Notebook(self.paned)
        self.notebook.pack(fill="both", expand=True)

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()
        self.build_tab4()
        self.build_tab5()

    def build_tab1(self):
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="光谱")

        plot_frame = ttk.Frame(tab1)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            pady=(0, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")

        self.canvas1 = FigureCanvasTkAgg(fig1, master=plot_frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas1, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        (self.realtime,) = self.ax1.plot([], [], "-", label="Real time")
        (self.reference,) = self.ax1.plot([], [], "-", label="Reference")
        (self.dark,) = self.ax1.plot([], [], "-", label="Dark")

        self.ax1.legend()

    def build_tab2(self):
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="透射")

        plot_frame = ttk.Frame(tab2)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            pady=(0, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlabel("Wavelength")
        self.ax2.set_ylabel("Ratio")

        self.canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas2, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas2.mpl_connect("scroll_event", self.on_scroll)

        (self.absorb,) = self.ax2.plot([], [], "-", label="Real time")
        (self.center,) = self.ax2.plot([], [], ".", label="Centroid")

    def build_tab3(self):
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="时序")

        plot_frame = ttk.Frame(tab3)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            pady=(0, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig3, self.ax3 = plt.subplots()
        self.ax3.set_xlabel("Time")
        self.ax3.set_ylabel("Wavelength")

        self.canvas3 = FigureCanvasTkAgg(fig3, master=plot_frame)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas3, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas3.mpl_connect("scroll_event", self.on_scroll)

        (self.timeseries,) = self.ax3.plot([], [], "-")

    def build_tab4(self):
        tab4 = ttk.Frame(self.notebook)
        self.notebook.add(tab4, text="强度时序")

        plot_frame = ttk.Frame(tab4)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            pady=(0, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig4, self.ax4 = plt.subplots()
        self.ax4.set_xlabel("Time")
        self.ax4.set_ylabel("Intensity")

        self.canvas4 = FigureCanvasTkAgg(fig4, master=plot_frame)
        self.canvas4.draw()
        self.canvas4.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas4, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas4.mpl_connect("scroll_event", self.on_scroll)

        (self.intensity,) = self.ax4.plot([], [], "-")

    def build_tab5(self):
        tab5 = ttk.Frame(self.notebook)
        self.notebook.add(tab5, text="最低点")

        plot_frame = ttk.Frame(tab5)
        plot_frame.grid(
            row=0,
            column=0,
            padx=(0, 10),
            pady=(0, 10),
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig5, self.ax5 = plt.subplots()
        self.ax5.set_xlabel("Time")
        self.ax5.set_ylabel("Wavelength")

        self.canvas5 = FigureCanvasTkAgg(fig5, master=plot_frame)
        self.canvas5.draw()
        self.canvas5.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas5, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas5.mpl_connect("scroll_event", self.on_scroll)

        (self.lowest,) = self.ax5.plot([], [], "-")

    def _make_absorb(self):
        i = random.randint(0, 9)
        self.x_ab = self.df["Wavelength"].values
        self.y_abs = self.df[f"Ratio_{i}"].values

    def make_absorb(self):
        self.x_ab = self.x[:3000]
        self.y_abs = (
            abs(
                (self.y_s[:3000] - self.y_darks[:3000])
                / (self.y_refs[:3000] - self.y_darks[:3000])
            )
            * 100
        )

    def init_ratio(self):
        if (len(self.y_refs) > 0) and (len(self.y_darks) > 0):
            self.make_absorb()
            self.init_plot2()
        else:
            pass

    def update_ratio(self):
        if (len(self.y_refs) > 0) and (len(self.y_darks) > 0):
            self.make_absorb()
            self.update_plot2()
        else:
            pass

    def update_plots(self):
        if self.ts_running == True:
            self.make_absorb()
            self.min_idx = self.find_minimum(self.y_abs)

            if self.fix_minimum == False:
                self.min_idx_display = self.min_idx
                self.update_min_value()

            self.mins.append(self.x_ab[self.min_idx])

            self.centroid_x, self.centroid_y = self.find_centroid(
                x=self.x_ab, y=self.y_abs, min_idx=self.min_idx_display, diff=self.diff
            )
            self.centroids.append(self.centroid_x)
            self.centroids_sm = gaussian_filter1d(self.centroids, sigma=10)

            self.intensities.append(self.y_abs[self.idx_y])
            self.intensities_sm = gaussian_filter1d(self.intensities, sigma=10)

            self.times = list(range(len(self.centroids)))

            self.update_center_value()
            if self.init_plots == False:
                self.init_plot2()
            else:
                self.update_plot2()
                self.update_plot3()
                self.update_plot4()
                self.update_plot5()
            self.after(self.sample_time, self.update_plots)
        else:
            self.ts_running = True

    def update_min_value(self):
        self.min_label.config(text=f"{self.x[self.min_idx_display]:.3f}")

    def update_center_value(self):
        self.centroid_label.config(text=f"{self.centroid_x:.3f}")

    def init_plot2(self):
        self.absorb.set_data(self.x_ab, self.y_abs)
        if self.centroid_x:
            self.center.set_data([self.centroid_x], [self.centroid_y])
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas2.draw()
        self.init_plots = True

    def update_plot2(self):
        self.absorb.set_data(self.x_ab, self.y_abs)
        if self.centroid_x:
            self.center.set_data([self.centroid_x], [self.centroid_y])
        self.canvas2.draw()

    def update_plot3(self):
        self.timeseries.set_data(self.times, self.centroids)
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.canvas3.draw()

    def update_plot4(self):
        self.intensity.set_data(self.times, self.intensities)
        self.ax4.relim()
        self.ax4.autoscale_view()
        self.canvas4.draw()

    def update_plot5(self):
        self.lowest.set_data(self.times, self.mins)
        self.ax5.relim()
        self.ax5.autoscale_view()
        self.canvas5.draw()

    def stop_absorb(self):
        self.ts_running = False

    def fix_min(self):
        self.fix_minimum = not self.fix_minimum

    @staticmethod
    def find_minimum(y):
        min_index = np.argmin(y)
        return min_index

    @staticmethod
    def find_interval(arr, value):
        if value < arr[0] or value >= arr[-1]:
            return None

        low, high = 0, len(arr) - 1
        while low <= high:
            mid = (low + high) // 2
            if arr[mid] <= value < arr[mid + 1]:
                return arr[mid]
            elif value < arr[mid]:
                high = mid - 1
            else:
                low = mid + 1

        return None

    def find_centroid(self, x, y, min_idx, diff):
        x_min = x[min_idx]
        xl = self.find_interval(x[:min_idx], x_min - diff)
        xr = self.find_interval(x[min_idx:], x_min + diff)
        il, ir = list(x).index(xl), list(x).index(xr)
        boundary = list(
            zip(list(x[il:ir]) + [x[ir], x[il]], list(y[il:ir]) + [100, 100])
        )
        polygon = Polygon(boundary)
        return polygon.centroid.x, polygon.centroid.y

    def save_data(self):
        ininame = make_results_file()
        file_path = filedialog.asksaveasfile(
            initialfile=ininame, defaultextension=".xlsx"
        )
        self.save_to_excel(file_path.name)

    def save_to_excel(self, file_path):

        df1 = pd.DataFrame(
            {
                "Wave Length": self.x_dark,
                "Dark Intensity": self.y_dark,
                "Dark Intensity(smooth)": self.y_darks,
                "Reference Intensity": self.y_ref,
                "Reference Intensity(smooth)": self.y_refs,
            }
        )

        df2 = pd.DataFrame({"Wave Length": self.x_ab, "Ratio": self.y_abs})

        df3 = pd.DataFrame(
            {"Centroid": self.centroids, "Centroid(smooth)": self.centroids_sm}
        )

        df4 = pd.DataFrame(
            {"Intensity": self.intensities, "Intensity(smooth)": self.intensities_sm}
        )

        df5 = pd.DataFrame({"Minimal": self.mins})

        df6 = pd.DataFrame(
            {
                "积分时间(ms)": self.int_time,
                "采样时间(ms)": self.sample_time,
                "暗光谱": self.dark_file,
                "参考光谱": self.bright_file,
                "质心范围(+/-)": self.diff,
                "强度位置": self.position,
                "固定最低点": self.x_ab[self.min_idx_display],
                "数据文件路径": file_path,
            }.items()
        )

        with pd.ExcelWriter(path=file_path) as writer:
            df1.to_excel(writer, sheet_name="光谱", index=False)
            df2.to_excel(writer, sheet_name="吸收", index=False)
            df3.to_excel(writer, sheet_name="时序", index=False)
            df4.to_excel(writer, sheet_name="强度", index=False)
            df5.to_excel(writer, sheet_name="最低点", index=False)
            df6.to_excel(writer, sheet_name="参数", index=False)

    def on_scroll(self, event):
        ax = event.inaxes
        if ax is None:
            return

        xdata, ydata = event.xdata, event.ydata  # Mouse position in data coords
        if xdata is None or ydata is None:
            return  # Ignore scroll events outside the axes

        base_scale = 1.1  # Determines the zoom speed
        if event.button == "up":
            # Zoom in
            scale_factor = 1 / base_scale
        elif event.button == "down":
            # Zoom out
            scale_factor = base_scale
        else:
            # Unhandled button
            return

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Determine the mouse position relative to the plot bounds
        if (ydata - ylim[0]) / (ylim[1] - ylim[0]) < 0.1:
            ax.set_xlim(
                [
                    xdata - (xdata - xlim[0]) * scale_factor,
                    xdata + (xlim[1] - xdata) * scale_factor,
                ]
            )

        elif (xdata - xlim[0]) / (xlim[1] - xlim[0]) < 0.1:
            ax.set_ylim(
                [
                    ydata - (ydata - ylim[0]) * scale_factor,
                    ydata + (ylim[1] - ydata) * scale_factor,
                ]
            )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("FiberX")
    root.state("zoomed")

    azure_path = resource_path("azure/azure.tcl")
    root.tk.call("source", azure_path)
    root.tk.call("set_theme", "light")

    app = App(root)
    app.pack(fill="both", expand=True)

    root.mainloop()
