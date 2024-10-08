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
    make_dark_file,
    make_bright_file,
    save_file,
    make_results_file,
)

ctypes.windll.shcore.SetProcessDpiAwareness(2)
ctypes.windll.kernel32.SetDllDirectoryW(None)

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.figsize": (14.8, 8.8),
        "figure.autolayout": True,
        "lines.linewidth": 3.0,
        "lines.markersize": 10.0,
        "font.size": 14,
    }
)


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)
        self.running = True
        self.ts_running = False
        self.int_time = 200
        self.sample_time = 1000
        self.diff = 25
        self.range_low = 500
        self.range_high = 700
        self.ini_position = 700
        self.scale_factor_x = 50
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
        self.area_ratios = []

        self.init_absorb = False
        self.init_plots = False

        self.x_dark = []
        self.y_dark = []
        self.x_ref = []
        self.y_ref = []
        self.y_refs = []
        self.y_darks = []

        self.y_s = []

        self.x_ab = []
        self.y_abs = []

        self.dark_file, self.bright_file = None, None

        if os.path.exists("data"):
            self.folder_path = "data"
            self.dark_folder = os.path.join(self.folder_path, "dark")
            self.bright_folder = os.path.join(self.folder_path, "bright")
            self.results_folder = os.path.join(self.folder_path, "results")
        else:
            self.folder_path = "."
            self.dark_folder = None
            self.bright_folder = None
            self.results_folder = None

        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white")

        self.build_input_block()
        self.build_dark_block()
        self.build_bright_block()
        self.build_range_block()
        self.build_control_block()
        self.build_display_block()
        self.build_plot_block()

    def build_input_block(self):
        input_frame = ttk.LabelFrame(self, text="设置", padding=(20, 5))
        input_frame.grid(
            row=0,
            column=0,
            padx=(10, 10),
            pady=5,
            sticky="nsew",
        )

        label = ttk.Label(input_frame, text="积分时间(ms):")
        label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.int_entry = ttk.Entry(input_frame, width=10)
        self.int_entry.insert(0, self.int_time)
        self.int_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        label = ttk.Label(input_frame, text="采样时间(ms):")
        label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.sample_entry = ttk.Entry(input_frame, width=10)
        self.sample_entry.insert(0, self.sample_time)
        self.sample_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.start_button = ttk.Button(
            input_frame,
            text="开始",
            command=self.start_real,
            style="Accent.TButton",
        )
        self.start_button.grid(
            row=2, column=0, padx=10, pady=5, columnspan=1, sticky="ew"
        )

        self.stop_button = ttk.Button(
            input_frame,
            text="暂停",
            command=self.stop_real,
            style="Accent.TButton",
            state=tk.DISABLED,
        )
        self.stop_button.grid(
            row=2, column=1, padx=10, pady=5, columnspan=1, sticky="ew"
        )

    def select_dark_folder(self):
        self.dark_folder = filedialog.askdirectory(initialdir=self.folder_path)
        self.build_dark_block()

    def select_bright_folder(self):
        self.bright_folder = filedialog.askdirectory(initialdir=self.folder_path)
        self.build_bright_block()

    def init_real(self):
        self.int_time = int(self.int_entry.get())
        self.signal_generator = SignalGenerator(int_time=self.int_time)
        self.signal_generator.start()
        self.x = self.signal_generator.generate_x()
        self.y = self.signal_generator.generate_y()
        self.y_s = gaussian_filter1d(self.y, sigma=100)
        self.plot1_real.set_data(self.x, self.y_s)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.init_absorb = True
        self.init_ratio()

    def start_real(self):
        self.stop_button.config(state=tk.NORMAL)
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
            self.plot1_real.set_data(self.x, self.y_s)
            self.canvas1.mpl_connect("scroll_event", self.on_scroll)
            self.canvas1.draw()
            self.update_ratio()
            self.after(self.int_time, self.update_real)
        else:
            self.running = True

    def stop_real(self):
        self.stop_button.config(state=tk.DISABLED)
        self.signal_generator.close_spectrometers()
        self.init_absorb = False
        self.running = False

    def save_dark(self):
        ininame = make_dark_file()
        file_path = filedialog.asksaveasfile(
            initialfile=ininame, defaultextension=".csv"
        )
        save_file(self.x, self.y, file_path)
        self.build_dark_block()

    def save_bright(self):
        ininame = make_bright_file()
        file_path = filedialog.asksaveasfile(
            initialfile=ininame, defaultextension=".csv"
        )
        save_file(self.x, self.y, file_path)
        self.build_bright_block()

    def build_dark_block(self):
        dark_frame = ttk.LabelFrame(self, text="暗光谱", padding=(20, 5))
        dark_frame.grid(
            row=1,
            column=0,
            padx=(10, 10),
            pady=5,
            sticky="nsew",
        )

        self.dark_canvas = tk.Canvas(dark_frame, width=100, height=100)
        scrollbar = ttk.Scrollbar(
            dark_frame, orient="vertical", command=self.dark_canvas.yview
        )

        scrollable_frame = ttk.Frame(self.dark_canvas)
        scrollable_frame.pack(fill=tk.BOTH)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.dark_canvas.configure(
                scrollregion=self.dark_canvas.bbox("all")
            ),
        )

        self.dark_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.dark_canvas.configure(yscrollcommand=scrollbar.set)

        self.dark_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        dark_frame.bind("<Enter>", self.bind_mousewheel_dark)
        dark_frame.bind("<Leave>", self.unbind_mousewheel_dark)

        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill=tk.BOTH)

        select_button = ttk.Button(
            buttons_frame,
            text="选择路径",
            command=self.select_dark_folder,
            style="Accent.TButton",
        )
        select_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, padx=10, pady=5)

        save_dark_button = ttk.Button(
            buttons_frame,
            text="保存暗光谱",
            command=self.save_dark,
            style="Accent.TButton",
        )
        save_dark_button.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, padx=10, pady=5
        )

        var = tk.StringVar()
        if self.dark_folder:
            filenames = os.listdir(self.dark_folder)[::-1]
            for file in filenames:
                b = ttk.Checkbutton(
                    scrollable_frame,
                    text=file,
                    variable=var,
                    onvalue=file,
                    command=lambda var=var: self.load_dark(var),
                )
                b.pack(anchor=tk.W, padx=10)
        else:
            label = ttk.Label(scrollable_frame, text="请选择暗光谱文件夹。")
            label.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, padx=10)

    def bind_mousewheel_dark(self, event):
        """Bind the mousewheel scroll to the canvas"""
        self.dark_canvas.bind_all("<MouseWheel>", self.on_mousewheel_dark)

    def unbind_mousewheel_dark(self, event):
        """Bind the mousewheel scroll to the canvas"""
        self.dark_canvas.unbind_all("<MouseWheel>")

    def on_mousewheel_dark(self, event):
        """Mouse wheel handler"""
        if event.num == 4:  # Linux wheel up
            delta = -1
        elif event.num == 5:  # Linux wheel down
            delta = 1
        else:
            delta = -1 * event.delta // 120  # Convert from MS units to common value

        self.dark_canvas.yview_scroll(delta, "units")

    def load_dark(self, file_path):
        self.dark_file = os.path.join(self.dark_folder, file_path.get())
        try:
            self.x_dark, self.y_dark = load_file(self.dark_file)
            self.y_darks = gaussian_filter1d(self.y_dark, sigma=100)
            self.plot1_dark.set_data(self.x_dark, self.y_darks)
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas1.draw()
        except FileNotFoundError:
            self.y_darks = []
            self.plot1_dark.set_data([], [])
            self.canvas1.draw()

        if len(self.y_s) > 0:
            self.init_ratio()
            self.update_ratio()

    def build_bright_block(self):
        bright_frame = ttk.LabelFrame(self, text="参考光谱", padding=(20, 5))
        bright_frame.grid(
            row=2,
            column=0,
            padx=(10, 10),
            pady=5,
            sticky="nsew",
        )

        self.bright_canvas = tk.Canvas(bright_frame, width=100, height=200)
        scrollbar = ttk.Scrollbar(
            bright_frame, orient="vertical", command=self.bright_canvas.yview
        )

        scrollable_frame = ttk.Frame(self.bright_canvas)
        scrollable_frame.pack(fill="both")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.bright_canvas.configure(
                scrollregion=self.bright_canvas.bbox("all")
            ),
        )

        self.bright_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.bright_canvas.configure(yscrollcommand=scrollbar.set)

        self.bright_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bright_frame.bind("<Enter>", self.bind_mousewheel_bright)
        bright_frame.bind("<Leave>", self.unbind_mousewheel_bright)

        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill="both")

        select_button = ttk.Button(
            buttons_frame,
            text="选择路径",
            command=self.select_bright_folder,
            style="Accent.TButton",
        )
        select_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, padx=10, pady=5)

        save_bright_button = ttk.Button(
            buttons_frame,
            text="保存亮光谱",
            command=self.save_bright,
            style="Accent.TButton",
        )
        save_bright_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=5)

        var = tk.StringVar()
        if self.bright_folder:
            filenames = os.listdir(self.bright_folder)[::-1]
            for file in filenames:
                b = ttk.Checkbutton(
                    scrollable_frame,
                    text=file,
                    variable=var,
                    onvalue=file,
                    command=lambda var=var: self.load_bright(var),
                )
                b.pack(fill=tk.BOTH, padx=10)
        else:
            label = ttk.Label(scrollable_frame, text="请选择亮光谱文件夹。")
            label.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, padx=10)

        scrollable_frame.bind("<Enter>", self.bind_mousewheel_bright)

    def bind_mousewheel_bright(self, event):
        """Bind the mousewheel scroll to the canvas"""
        self.bright_canvas.bind_all("<MouseWheel>", self.on_mousewheel_bright)

    def unbind_mousewheel_bright(self, event):
        """Bind the mousewheel scroll to the canvas"""
        self.bright_canvas.unbind_all("<MouseWheel>")

    def on_mousewheel_bright(self, event):
        """Mouse wheel handler"""
        if event.num == 4:  # Linux wheel up
            delta = -1
        elif event.num == 5:  # Linux wheel down
            delta = 1
        else:
            delta = -1 * event.delta // 120  # Convert from MS units to common value

        self.bright_canvas.yview_scroll(delta, "units")

    def load_bright(self, file_path):
        self.bright_file = os.path.join(self.bright_folder, file_path.get())
        try:
            self.x_ref, self.y_ref = load_file(self.bright_file)
            self.y_refs = gaussian_filter1d(self.y_ref, sigma=100)
            self.plot1_ref.set_data(self.x_ref, self.y_refs)
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas1.draw()
        except FileNotFoundError:
            self.y_refs = []
            self.plot1_ref.set_data([], [])
            self.canvas1.draw()

        if len(self.y_s) > 0:
            self.init_ratio()
            self.update_ratio()

    def build_range_block(self):
        range_frame = ttk.LabelFrame(self, text="面积范围", padding=(20, 5))
        range_frame.grid(
            row=3,
            column=0,
            padx=(10, 10),
            pady=5,
            sticky="nsew",
        )

        label = ttk.Label(range_frame, text="范围(nm):")
        label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.range1 = ttk.Entry(range_frame, width=7)
        self.range1.insert(0, self.range_low)
        self.range1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        label = ttk.Label(range_frame, text="-")
        label.grid(row=0, column=2, padx=0, pady=0, sticky="ew")
        self.range2 = ttk.Entry(range_frame, width=7)
        self.range2.insert(0, self.range_high)
        self.range2.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    def build_control_block(self):
        control_frame = ttk.LabelFrame(self, text="控制", padding=(20, 5), height=300)
        control_frame.grid(
            row=4,
            column=0,
            padx=(10, 10),
            pady=5,
            sticky="nsew",
        )

        label = ttk.Label(control_frame, text="质心范围(+/-):")
        label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.diff_entry = ttk.Entry(control_frame, width=7)
        self.diff_entry.insert(0, self.diff)
        self.diff_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        label = ttk.Label(control_frame, text="强度位置(nm):")
        label.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.position_entry = ttk.Entry(control_frame, width=7)
        self.position_entry.insert(0, self.ini_position)
        self.position_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        start_ts_button = ttk.Button(
            control_frame,
            text="开始时序",
            command=self.start_absorb,
            style="Accent.TButton",
        )
        start_ts_button.grid(
            row=3, column=0, padx=10, pady=5, columnspan=1, sticky="ew"
        )

        self.stop_ts_button = ttk.Button(
            control_frame,
            text="暂停时序",
            command=self.stop_absorb,
            style="Accent.TButton",
            state=tk.DISABLED,
        )
        self.stop_ts_button.grid(
            row=3, column=1, padx=10, pady=5, columnspan=1, sticky="ew"
        )

        clean_button = ttk.Button(
            control_frame,
            text="清除时序",
            command=self.clean_plots,
            style="Accent.TButton",
        )
        clean_button.grid(row=4, column=0, padx=10, pady=5, columnspan=1, sticky="ew")

        save_button = ttk.Button(
            control_frame,
            text="保存数据",
            command=lambda: self.save_data(),
            style="Accent.TButton",
        )
        save_button.grid(row=4, column=1, padx=10, pady=5, columnspan=1, sticky="ew")

    def start_absorb(self):
        self.stop_ts_button.config(state=tk.NORMAL)
        self.sample_time = int(self.sample_entry.get())
        self.diff = int(self.diff_entry.get())
        self.position = int(self.position_entry.get())
        closest_x = self.find_interval(self.x, self.position)
        self.idx_y = list(self.x).index(closest_x)

        self.calculate_ref_area()

        if not self.ts_running:
            self.ts_running = True
        self.update_plots()

    def calculate_ref_area(self):
        self.range_low = int(self.range1.get())
        closest_range1 = self.find_interval(self.x, self.range_low)
        self.range1_idx = list(self.x).index(closest_range1)

        self.range_high = int(self.range2.get())
        closest_range2 = self.find_interval(self.x, self.range_high)
        self.range2_idx = list(self.x).index(closest_range2)

        self.area_ref = np.dot(
            self.x_ref[self.range1_idx : self.range2_idx],
            self.y_refs[self.range1_idx : self.range2_idx],
        )

    def clean_plots(self):
        self.times, self.centroids, self.intensities, self.mins, self.area_ratios = (
            [],
            [],
            [],
            [],
            [],
        )
        self.plot3_time.set_data([], [])
        self.canvas3.draw()
        self.plot4_intensity.set_data([], [])
        self.canvas4.draw()
        self.plot5_lowest.set_data([], [])
        self.canvas5.draw()
        self.plot6_area.set_data([], [])
        self.canvas6.draw()
        self.ts_running = False

    def build_display_block(self):
        real_frame = ttk.LabelFrame(self, text="实时数据", padding=(20, 5))
        real_frame.grid(
            row=5,
            column=0,
            padx=(10, 10),
            pady=5,
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

    def build_plot_block(self):
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(
            row=0,
            column=1,
            padx=(20, 20),
            pady=5,
            sticky="nsew",
            rowspan=6,
        )

        self.notebook = ttk.Notebook(self.paned)
        self.notebook.pack(fill="both", expand=True)

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()
        self.build_tab4()
        self.build_tab5()
        self.build_tab6()

    def build_tab1(self):
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="光谱")

        plot_frame = ttk.Frame(tab1)
        plot_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")
        (self.plot1_real,) = self.ax1.plot([], [], "-", label="Real time")
        (self.plot1_ref,) = self.ax1.plot([], [], "-", label="Reference")
        (self.plot1_dark,) = self.ax1.plot([], [], "-", label="Dark")
        self.ax1.legend()

        self.canvas1 = FigureCanvasTkAgg(fig1, master=plot_frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas1.mpl_connect("scroll_event", self.on_scroll)

        auto_button = ttk.Button(
            tab1,
            text="自适应",
            command=self.auto_rescale1,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        toolbar = NavigationToolbar2Tk(self.canvas1, tab1, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=110, pady=0, sticky="w")

    def build_tab2(self):
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="透射")

        plot_frame = ttk.Frame(tab2)
        plot_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlabel("Wavelength")
        self.ax2.set_ylabel("Ratio")
        (self.plot2_absorb,) = self.ax2.plot([], [], "-", label="Real time")
        (self.plot2_center,) = self.ax2.plot([], [], ".", label="Centroid")

        self.canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas2.mpl_connect("scroll_event", self.on_scroll)

        auto_button = ttk.Button(
            tab2,
            text="自适应",
            command=self.auto_rescale2,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        toolbar = NavigationToolbar2Tk(self.canvas2, tab2, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=110, pady=0, sticky="w")

    def build_tab3(self):
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="时序")

        plot_frame = ttk.Frame(tab3)
        plot_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig3, self.ax3 = plt.subplots()
        self.ax3.set_xlabel("Time")
        self.ax3.set_ylabel("Wavelength")
        (self.plot3_time,) = self.ax3.plot([], [], "-")

        self.canvas3 = FigureCanvasTkAgg(fig3, master=plot_frame)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas3.mpl_connect("scroll_event", self.on_scroll)

        auto_button = ttk.Button(
            tab3,
            text="自适应",
            command=self.auto_rescale3,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        toolbar = NavigationToolbar2Tk(self.canvas3, tab3, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=110, pady=0, sticky="w")

    def build_tab4(self):
        tab4 = ttk.Frame(self.notebook)
        self.notebook.add(tab4, text="强度时序")

        plot_frame = ttk.Frame(tab4)
        plot_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig4, self.ax4 = plt.subplots()
        self.ax4.set_xlabel("Time")
        self.ax4.set_ylabel("Intensity")
        (self.plot4_intensity,) = self.ax4.plot([], [], "-")

        self.canvas4 = FigureCanvasTkAgg(fig4, master=plot_frame)
        self.canvas4.draw()
        self.canvas4.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas4.mpl_connect("scroll_event", self.on_scroll)

        auto_button = ttk.Button(
            tab4,
            text="自适应",
            command=self.auto_rescale4,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        toolbar = NavigationToolbar2Tk(self.canvas4, tab4, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=110, pady=0, sticky="w")

    def build_tab5(self):
        tab5 = ttk.Frame(self.notebook)
        self.notebook.add(tab5, text="最低点")

        plot_frame = ttk.Frame(tab5)
        plot_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig5, self.ax5 = plt.subplots()
        self.ax5.set_xlabel("Time")
        self.ax5.set_ylabel("Wavelength")
        (self.plot5_lowest,) = self.ax5.plot([], [], "-")

        self.canvas5 = FigureCanvasTkAgg(fig5, master=plot_frame)
        self.canvas5.draw()
        self.canvas5.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas5.mpl_connect("scroll_event", self.on_scroll)

        auto_button = ttk.Button(
            tab5,
            text="自适应",
            command=self.auto_rescale5,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        toolbar = NavigationToolbar2Tk(self.canvas5, tab5, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=110, pady=0, sticky="w")

    def build_tab6(self):
        tab6 = ttk.Frame(self.notebook)
        self.notebook.add(tab6, text="波长x强度")

        plot_frame = ttk.Frame(tab6)
        plot_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew",
            rowspan=3,
            columnspan=3,
        )

        fig6, self.ax6 = plt.subplots()
        self.ax6.set_xlabel("Time")
        self.ax6.set_ylabel("Ratio")
        (self.plot6_area,) = self.ax6.plot([], [], "-")

        self.canvas6 = FigureCanvasTkAgg(fig6, master=plot_frame)
        self.canvas6.draw()
        self.canvas6.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas6.mpl_connect("scroll_event", self.on_scroll)

        auto_button = ttk.Button(
            tab6,
            text="自适应",
            command=self.auto_rescale6,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        toolbar = NavigationToolbar2Tk(self.canvas6, tab6, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=110, pady=0, sticky="w")

    def auto_rescale1(self):
        self.ax1.set_xlim(min(self.x) - 50, max(self.x) + 50)
        y = list(self.y_s) + list(self.y_darks) + list(self.y_refs)
        delta = max(y) - min(y)
        self.ax1.set_ylim(
            min(y) - 0.1 * delta,
            max(y) + 0.1 * delta,
        )
        self.canvas1.draw()

    def auto_rescale2(self):
        self.ax1.set_xlim(min(self.x) - 50, max(self.x) + 50)
        delta = max(self.y_abs) - min(self.y_abs)
        self.ax2.set_ylim(
            min(self.y_abs) - 0.1 * delta,
            max(self.y_abs) + 0.1 * delta,
        )
        self.canvas2.draw()

    def auto_rescale3(self):
        xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
        self.ax3.set_xlim(0, xmax)
        delta = max(self.centroids) - min(self.centroids)
        self.ax3.set_ylim(
            min(self.centroids) - 0.1 * delta,
            max(self.centroids) + 0.1 * delta,
        )
        self.canvas3.draw()

    def auto_rescale4(self):
        xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
        self.ax4.set_xlim(0, xmax)
        delta = max(self.intensities) - min(self.intensities)
        self.ax4.set_ylim(
            min(self.intensities) - 0.1 * delta,
            max(self.intensities) + 0.1 * delta,
        )
        self.canvas4.draw()

    def auto_rescale5(self):
        xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
        self.ax5.set_xlim(0, xmax)
        delta = max(self.mins) - min(self.mins)
        self.ax5.set_ylim(
            min(self.mins) - 0.1 * delta,
            max(self.mins) + 0.1 * delta,
        )
        self.canvas5.draw()

    def auto_rescale6(self):
        xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
        self.ax6.set_xlim(0, xmax)
        delta = max(self.area_ratios) - min(self.area_ratios)
        self.ax6.set_ylim(
            min(self.area_ratios) - 0.1 * delta,
            max(self.area_ratios) + 0.1 * delta,
        )
        self.canvas6.draw()

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

            try:
                self.centroid_x, self.centroid_y = self.find_centroid(
                    x=self.x_ab,
                    y=self.y_abs,
                    min_idx=self.min_idx_display,
                    diff=self.diff,
                )
                self.centroids.append(self.centroid_x)
                self.centroids_sm = gaussian_filter1d(self.centroids, sigma=10)

                self.intensities.append(self.y_abs[self.idx_y])
                self.intensities_sm = gaussian_filter1d(self.intensities, sigma=10)

                self.mins.append(self.x_ab[self.min_idx])

                area_current = np.dot(
                    self.x[self.range1_idx : self.range2_idx],
                    self.y_s[self.range1_idx : self.range2_idx],
                )
                self.area_ratios.append(area_current / self.area_ref * 100)

                self.times = list(range(len(self.centroids)))

                self.update_center_value()
                if not self.init_plots:
                    self.init_plot2()
                    self.init_plot3()
                    self.init_plot4()
                    self.init_plot5()
                    self.init_plot6()
                    self.init_plots = True

                self.update_plot2()
                self.update_plot3()
                self.update_plot4()
                self.update_plot5()
                self.update_plot6()

            except ValueError:
                pass

            self.after(self.sample_time, self.update_plots)
        else:
            self.ts_running = True

    def update_min_value(self):
        self.min_label.config(text=f"{self.x[self.min_idx_display]:.3f}")

    def update_center_value(self):
        self.centroid_label.config(text=f"{self.centroid_x:.3f}")

    def init_plot2(self):
        self.plot2_absorb.set_data(self.x_ab, self.y_abs)
        if self.centroid_x:
            self.plot2_center.set_data([self.centroid_x], [self.centroid_y])
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas2.draw()

    def init_plot3(self):
        self.plot3_time.set_data(self.times, self.centroids)
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.canvas3.draw()

    def init_plot4(self):
        self.plot4_intensity.set_data(self.times, self.intensities)
        self.ax4.relim()
        self.ax4.autoscale_view()
        self.canvas4.draw()

    def init_plot5(self):
        self.plot5_lowest.set_data(self.times, self.mins)
        self.ax5.relim()
        self.ax5.autoscale_view()
        self.canvas5.draw()

    def init_plot6(self):
        self.plot6_area.set_data(self.times, self.area_ratios)
        self.ax6.relim()
        self.ax6.autoscale_view()
        self.canvas6.draw()

    def update_plot2(self):
        self.plot2_absorb.set_data(self.x_ab, self.y_abs)
        if self.centroid_x:
            self.plot2_center.set_data([self.centroid_x], [self.centroid_y])
        self.canvas2.draw()

    def update_plot3(self):
        xmin, xmax = self.ax3.get_xlim()
        if self.times[-1] % self.scale_factor_x == 0:
            new_xmax = self.times[-1] + self.scale_factor_x
            if new_xmax > xmax:
                self.ax3.set_xlim(xmin, new_xmax)

        self.plot3_time.set_data(self.times, self.centroids)
        self.canvas3.draw()

    def update_plot4(self):
        xmin, xmax = self.ax4.get_xlim()
        if self.times[-1] % self.scale_factor_x == 0:
            new_xmax = self.times[-1] + self.scale_factor_x
            if new_xmax > xmax:
                self.ax4.set_xlim(xmin, new_xmax)

        self.plot4_intensity.set_data(self.times, self.intensities)
        self.canvas4.draw()

    def update_plot5(self):
        xmin, xmax = self.ax5.get_xlim()
        if self.times[-1] % self.scale_factor_x == 0:
            new_xmax = self.times[-1] + self.scale_factor_x
            if new_xmax > xmax:
                self.ax5.set_xlim(xmin, new_xmax)

        self.plot5_lowest.set_data(self.times, self.mins)
        self.canvas5.draw()

    def update_plot6(self):
        xmin, xmax = self.ax6.get_xlim()
        if self.times[-1] % self.scale_factor_x == 0:
            new_xmax = self.times[-1] + self.scale_factor_x
            if new_xmax > xmax:
                self.ax6.set_xlim(xmin, new_xmax)

        self.plot6_area.set_data(self.times, self.area_ratios)
        self.canvas6.draw()

    def stop_absorb(self):
        self.ts_running = False
        self.stop_ts_button.configure(state=tk.DISABLED)

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
            initialdir=self.folder_path,
            initialfile=ininame,
            defaultextension=".xlsx",
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

        df6 = pd.DataFrame({"Ratio of area": self.area_ratios})

        df7 = pd.DataFrame(
            {
                "积分时间(ms)": self.int_time,
                "采样时间(ms)": self.sample_time,
                "暗光谱": self.dark_file,
                "参考光谱": self.bright_file,
                "质心范围(+/-)": self.diff,
                "强度位置": self.position,
                "面积范围": f"{self.range_low}-{self.range_high}",
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
            df6.to_excel(writer, sheet_name="面积比", index=False)
            df7.to_excel(writer, sheet_name="参数", index=False)

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
