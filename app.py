import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import os
import ctypes
import random
import pandas as pd
from shapely.geometry import Polygon
from scipy.ndimage import gaussian_filter1d

from device_io import SignalGenerator

from file_io import (
    load_file,
    save_dark_file,
    save_bright_file,
    make_results_file,
    dark_folder,
    bright_folder,
)

ctypes.windll.shcore.SetProcessDpiAwareness(1)
plt.style.use("ggplot")
plt.rcParams.update({"figure.figsize": (10.4, 6.9), "figure.autolayout": True})


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)
        self.running = True
        self.ts_running = True
        self.int_time = 100
        self.sample_time = 1000
        self.diff = 50
        self.min_idx = None
        self.fix_minimum = False
        self.centroid_x, self.centroid_y = None, None
        self.centroids = []

        self.y_refs = None
        self.y_darks = None

        self.df = pd.read_csv("../time_samples.csv")

        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        self.setup_files()
        self.setup_plots()

        # self.signal_generator = SignalGenerator()
        # self.signal_generator.start()
        # Sizegrip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(row=100, column=100, padx=(0, 3), pady=(0, 3))

    def setup_files(self):
        self.build_dark_block()
        self.build_bright_block()
        self.build_input_block()
        self.build_control_block()
        self.build_display_block()

    def setup_plots(self):
        self.build_plot_block()

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
        filenames = os.listdir(dark_folder)[::-1]
        for file in filenames:
            b = ttk.Checkbutton(
                dark_frame,
                text=file,
                variable=var,
                onvalue=file,
                command=lambda var=var: self.load_dark(var),
            )
            b.pack(anchor=tk.W)

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
        filenames = os.listdir(bright_folder)[::-1]
        for file in filenames:
            b = ttk.Checkbutton(
                ref_frame,
                text=file,
                variable=var,
                onvalue=file,
                command=lambda var=var: self.load_bright(var),
            )
            b.pack(anchor=tk.W)

    def build_input_block(self):
        input_frame = ttk.LabelFrame(self, text="设置", padding=(20, 10))
        input_frame.grid(
            row=0,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        label = ttk.Label(input_frame, text="积分时间:")
        label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.int_entry = ttk.Entry(input_frame, width=10)
        self.int_entry.insert(0, self.int_time)
        self.int_entry.grid(row=0, column=1, padx=(10, 50), pady=(0, 10), sticky="ew")

        label = ttk.Label(input_frame, text="采样时间:")
        label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.sample_entry = ttk.Entry(input_frame, width=10)
        self.sample_entry.insert(0, self.sample_time)
        self.sample_entry.grid(
            row=1, column=1, padx=(10, 50), pady=(0, 10), sticky="ew"
        )

        start_button = ttk.Button(
            input_frame,
            text="开始",
            command=self.start_real,
            style="Accent.TButton",
        )
        start_button.grid(
            row=2, column=0, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        stop_button = ttk.Button(
            input_frame,
            text="暂停",
            command=self.stop_real,
            style="Accent.TButton",
        )
        stop_button.grid(
            row=2, column=1, padx=(10, 50), pady=(10, 10), columnspan=1, sticky="ew"
        )

        save_dark_button = ttk.Button(
            input_frame,
            text="保存暗光谱",
            command=self.save_dark,
            style="Accent.TButton",
        )
        save_dark_button.grid(
            row=3, column=0, padx=10, pady=(0, 10), columnspan=1, sticky="ew"
        )

        save_bright_button = ttk.Button(
            input_frame,
            text="保存亮光谱",
            command=self.save_bright,
            style="Accent.TButton",
        )
        save_bright_button.grid(
            row=3, column=1, padx=(10, 50), pady=(0, 10), columnspan=1, sticky="ew"
        )

    def build_display_block(self):
        real_frame = ttk.LabelFrame(self, text="实时数据", padding=(20, 10))
        real_frame.grid(
            row=4,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        label = ttk.Label(real_frame, text="最低点:")
        label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.min_label = ttk.Label(real_frame, text="123.123", font=("Arial", 18))
        self.min_label.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        label = ttk.Label(real_frame, text="质心:")
        label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.centroid_label = ttk.Label(real_frame, text="123.123", font=("Arial", 18))
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
        self.position_entry.insert(0, 700)
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

        save_button = ttk.Button(
            control_frame,
            text="暂停时序",
            command=self.stop_absorb,
            style="Accent.TButton",
        )
        save_button.grid(
            row=2, column=1, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        confirm_button = ttk.Button(
            control_frame,
            text="固定最低点",
            command=self.fix_min,
            style="Accent.TButton",
        )
        confirm_button.grid(
            row=3, column=0, padx=10, pady=(0, 10), columnspan=1, sticky="ew"
        )

        confirm_button = ttk.Button(
            control_frame,
            text="保存数据",
            command=self.save_all_data,
            style="Accent.TButton",
        )
        confirm_button.grid(
            row=3, column=1, padx=10, pady=(0, 10), columnspan=1, sticky="ew"
        )

    def build_plot_block(self):
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(
            row=0,
            column=1,
            padx=(25, 0),
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

        (self.dark,) = self.ax1.plot([], [], "-", label="Dark")
        (self.reference,) = self.ax1.plot([], [], "-", label="Reference")
        (self.realtime,) = self.ax1.plot([], [], "-", label="Real time")

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

        (self.absorb,) = self.ax2.plot([], [], "-", label="Real time")
        (self.centroid,) = self.ax2.plot([], [], ".", label="Centroid")

        self.ax2.legend()

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
        self.ax3.set_ylabel("Y")

        self.canvas3 = FigureCanvasTkAgg(fig3, master=plot_frame)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        (self.timeseries,) = self.ax3.plot([], [], "-", label="Real time")

        self.ax3.legend()

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
        self.ax4.set_ylabel("Y")

        canvas = FigureCanvasTkAgg(fig4, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        (self.intensity,) = self.ax4.plot([], [], "-", label="Real time")

        self.ax4.legend()

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
        self.ax5.set_ylabel("Lowest Point")

        canvas = FigureCanvasTkAgg(fig5, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        (self.lowest,) = self.ax5.plot([], [], "-", label="Real time")

        self.ax5.legend()

    def load_dark(self, file_path):
        self.x_dark, self.y_dark = load_file(dark_folder + file_path.get())
        self.y_darks = gaussian_filter1d(self.y_dark, sigma=100)
        self.dark.set_data(self.x_dark, self.y_darks)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()

    def load_bright(self, file_path):
        self.x_ref, self.y_ref = load_file(bright_folder + file_path.get())
        self.y_refs = gaussian_filter1d(self.y_ref, sigma=100)
        self.reference.set_data(self.x_ref, self.y_refs)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.canvas1.draw()

    def save_dark(self):
        save_dark_file(self.x, self.y)
        self.build_dark_block()

    def save_bright(self):
        save_bright_file(self.x, self.y)
        self.build_bright_block()

    def update_real(self):
        if self.running == True:
            self.x = self.signal_generator.generate_x()
            self.y = self.signal_generator.generate_y()
            self.realtime.set_data(self.x, self.y)
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas1.draw()
            self.after(self.int_time, self.update_real)
        else:
            self.running = True

    def start_real(self):
        int_time = int(self.int_entry.get())
        self.signal_generator = SignalGenerator(int_time=int_time)
        self.signal_generator.start()
        self.update_real()

    def stop_real(self):
        self.signal_generator.stop_laser()
        self.running = False

    def _start_absorb(self):
        if self.ts_running == True:
            self.sample_time = self.sample_entry.get()
            i = random.randint(0, 9)
            self.x_ab = self.df["Wavelength"].to_list()
            self.y_ab = self.df[f"Ratio_{i}"].to_list()
            self.absorb.set_data(self.x_ab, self.y_ab)
            self.centroid.set_data([self.centroid_x], [self.centroid_y])
            self.ax2.relim()
            self.ax2.autoscale_view()
            self.canvas2.draw()
            self.update_min()
            self.update_centroid()
            self.after(self.sample_time, self.start_absorb)
        else:
            self.ts_running = True

    def start_absorb(self):
        if self.ts_running == True:
            self.y_ab = (self.y_refs - self.y) / (self.y - self.y_darks)
            self.y_abs = gaussian_filter1d(self.y_ab, sigma=100)
            self.absorb.set_data(self.x, self.y_abs)
            self.ax2.relim()
            self.ax2.autoscale_view()
            self.canvas2.draw()
            # self.centroid.set_data([self.centroid_x], [self.centroid_y])
            # self.update_min()
            # self.update_centroid()
            self.after(1000, self.start_absorb)
        else:
            self.ts_running = True

    def stop_absorb(self):
        self.ts_running = False

    def update_min(self):
        if self.fix_minimum == False:
            self.min_idx = self.find_minimum(y=self.y_ab)
            self.min_label.config(text=f"{self.x_ab[self.min_idx]:.3f}")
        else:
            pass

    def fix_min(self):
        self.fix_minimum = True

    def update_centroid(self):
        self.diff = int(self.diff_entry.get())
        self.centroid_x, self.centroid_y = self.find_centroid(
            x=self.x_ab, y=self.y_ab, min_idx=self.min_idx, diff=self.diff
        )
        self.centroid_label.config(text=f"{self.centroid_x:.3f}")

        self.centroids.append(self.centroid_x)
        self.centroids_sm = gaussian_filter1d(self.centroids, sigma=100)
        x_time = range(len(self.centroids))
        self.timeseries.set_data(x_time, self.centroids)
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.canvas3.draw()

    @staticmethod
    def find_minimum(y):
        min_index = y.index(min(y))
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
        il, ir = x.index(xl), x.index(xr)
        boundary = list(zip(x[il:ir], y[il:ir]))
        polygon = Polygon(boundary)
        return polygon.centroid.x, polygon.centroid.y

    def save_absorb(self):
        pass

    def setup_tab3(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="时序")

    def setup_tab4(self):
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="强度时序")

    def save_all_data(self):
        result_file = make_results_file()

        df1 = pd.DataFrame(
            {
                "Wave Length": self.x_dark,
                "Dark Intensity": self.y_dark,
                "Dark Intensity(smooth)": self.y_darks,
                "Reference Intensity": self.y_ref,
                "Reference Intensity(smooth)": self.y_refs,
            }
        )

        df2 = pd.DataFrame({"Wave Length": self.x_ab, "Ratio": self.y_ab})

        df3 = pd.DataFrame(
            {"Centroid": self.centroids, "Centroid(smooth)": self.centroids_sm}
        )

        with pd.ExcelWriter(path=result_file) as writer:
            df1.to_excel(writer, sheet_name="光谱", index=False)
            df2.to_excel(writer, sheet_name="吸收", index=False)
            df3.to_excel(writer, sheet_name="时序", index=False)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("FiberX")
    root.state("zoomed")
    # root.geometry("2500x1400")

    root.tk.call("source", "azure/azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    root.mainloop()
