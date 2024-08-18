import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

import os
import ctypes
import pandas as pd
import openpyxl

from scipy.ndimage import gaussian_filter1d

from device_io import SignalGenerator, resource_path
from file_io import make_results_file

ctypes.windll.shcore.SetProcessDpiAwareness(2)
ctypes.windll.kernel32.SetDllDirectoryW(None)

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.figsize": (15.4, 9),
        "figure.autolayout": True,
        "lines.linewidth": 3.0,
        "lines.markersize": 10.0,
        "font.size": 16,
    }
)


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)
        self.running = True
        self.ts_running = True
        self.int_time = 200
        self.sample_time = 1000
        self.position1 = (600,)
        self.position2 = (900,)
        self.diff1 = (25,)
        self.diff2 = (25,)
        self.scale_factor_x = 50

        self.idx_y1, self.idx_y2 = None, None

        self.area_ratios = []
        self.intensity_ratios = []

        self.init_absorb = False
        self.init_plots = False
        self.results_folder = None

        for index in [0, 1]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white")

        self.build_input_block()
        self.build_control_block()
        self.build_plot_block()

    def build_input_block(self):
        input_frame = ttk.LabelFrame(self, text="设置", padding=(20, 10), height=200)
        input_frame.grid(
            row=0,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        # 积分时间
        label = ttk.Label(input_frame, text="积分时间(ms):")
        label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.int_entry = ttk.Entry(input_frame, width=10)
        self.int_entry.insert(0, self.int_time)
        self.int_entry.grid(row=0, column=1, padx=(10, 50), pady=(0, 10), sticky="ew")

        # 采样时间
        label = ttk.Label(input_frame, text="采样时间(ms):")
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
        self.y_min, self.y_max = self.ax1.get_ylim()
        self.init_absorb = True

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
            self.after(self.int_time, self.update_real)
        else:
            self.running = True

    def stop_real(self):
        self.signal_generator.close_spectrometers()
        self.init_absorb = False
        self.running = False

    def build_control_block(self):
        control_frame = ttk.LabelFrame(self, text="时序", padding=(20, 10))
        control_frame.grid(
            row=1,
            column=0,
            padx=(10, 10),
            pady=(10, 10),
            sticky="nsew",
        )

        label = ttk.Label(control_frame, text="波长位置(nm)-I:")
        label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.w1_entry = ttk.Entry(control_frame, width=7)
        self.w1_entry.insert(0, self.position1)
        self.w1_entry.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="ew")

        label = ttk.Label(control_frame, text="波长位置(nm)-II:")
        label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.w2_entry = ttk.Entry(control_frame, width=7)
        self.w2_entry.insert(0, self.position2)
        self.w2_entry.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        label = ttk.Label(control_frame, text="波长范围(nm)-I:")
        label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.range1_entry = ttk.Entry(control_frame, width=7)
        self.range1_entry.insert(0, self.diff1)
        self.range1_entry.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="ew")

        label = ttk.Label(control_frame, text="波长范围(nm)-II:")
        label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.range2_entry = ttk.Entry(control_frame, width=7)
        self.range2_entry.insert(0, self.diff2)
        self.range2_entry.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        start_button = ttk.Button(
            control_frame,
            text="开始时序",
            command=self.start_absorb,
            style="Accent.TButton",
        )
        start_button.grid(
            row=4, column=0, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        stop_button = ttk.Button(
            control_frame,
            text="暂停时序",
            command=self.stop_absorb,
            style="Accent.TButton",
        )
        stop_button.grid(
            row=4, column=1, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        clean_button = ttk.Button(
            control_frame,
            text="清除时序",
            command=self.clean_plots,
            style="Accent.TButton",
        )
        clean_button.grid(
            row=5, column=0, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

        save_button = ttk.Button(
            control_frame,
            text="保存数据",
            command=lambda: self.save_data(),
            style="Accent.TButton",
        )
        save_button.grid(
            row=5, column=1, padx=10, pady=(10, 10), columnspan=1, sticky="ew"
        )

    def start_absorb(self):
        self.sample_time = int(self.sample_entry.get())
        self.read_inputs()
        self.get_idx()
        self.update_plots()

    def read_inputs(self):
        self.position1 = int(self.w1_entry.get())
        self.diff1 = int(self.range1_entry.get())

        self.position2 = int(self.w2_entry.get())
        self.diff2 = int(self.range2_entry.get())

    def get_idx(self):
        closest_x1 = self.find_interval(self.x, self.position1)
        x1_min = self.find_interval(self.x, self.position1 - self.diff1)
        x1_max = self.find_interval(self.x, self.position1 + self.diff1)

        self.idx_y1 = list(self.x).index(closest_x1)
        self.idx_y1_min = list(self.x).index(x1_min)
        self.idx_y1_max = list(self.x).index(x1_max)

        closest_x2 = self.find_interval(self.x, self.position2)
        x2_min = self.find_interval(self.x, self.position2 - self.diff2)
        x2_max = self.find_interval(self.x, self.position2 + self.diff2)

        self.idx_y2 = list(self.x).index(closest_x2)
        self.idx_y2_min = list(self.x).index(x2_min)
        self.idx_y2_max = list(self.x).index(x2_max)

    def clean_plots(self):
        self.intensity_ratios, self.area_ratios = [], []
        self.intensity_ratio_plot.set_data([], [])
        self.canvas2.draw()
        self.area_ratio_plot.set_data([], [])
        self.canvas3.draw()

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

        self.notebook = ttk.Notebook(self.paned, width=1600)
        self.notebook.pack(fill="both", expand=True)

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()

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

        (self.realtime,) = self.ax1.plot([], [], "-")

    def build_tab2(self):
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="强度比")

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
        self.ax2.set_ylabel("Intensity Ratio(%)")

        self.canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas2, tab2, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=100, pady=0, sticky="w")

        self.canvas2.mpl_connect("scroll_event", self.on_scroll)

        (self.intensity_ratio_plot,) = self.ax2.plot([], [], "-")

        auto_button = ttk.Button(
            tab2,
            text="自适应",
            command=self.auto_rescale2,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=0, pady=0, sticky="w")

    def build_tab3(self):
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="强度面积比")

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
        self.ax3.set_ylabel("Area Ratio(%)")

        self.canvas3 = FigureCanvasTkAgg(fig3, master=plot_frame)
        self.canvas3.draw()
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas3, tab3, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=3, column=0, padx=100, pady=0, sticky="w")

        self.canvas3.mpl_connect("scroll_event", self.on_scroll)

        (self.area_ratio_plot,) = self.ax3.plot([], [], "-")

        auto_button = ttk.Button(
            tab3,
            text="自适应",
            command=self.auto_rescale3,
            style="Accent.TButton",
            width=10,
        )
        auto_button.grid(row=3, column=0, padx=0, pady=0, sticky="w")

    def auto_rescale2(self):
        xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
        self.ax2.set_xlim(0, xmax)
        delta = max(self.intensity_ratios) - min(self.intensity_ratios)
        self.ax2.set_ylim(
            min(self.intensity_ratios) - 0.1 * delta,
            max(self.intensity_ratios) + 0.1 * delta,
        )
        self.canvas2.draw()

    def auto_rescale3(self):
        xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
        self.ax3.set_xlim(0, xmax)
        delta = max(self.area_ratios) - min(self.area_ratios)
        self.ax3.set_ylim(
            min(self.area_ratios) - 0.1 * delta, max(self.area_ratios) + 0.1 * delta
        )
        self.canvas3.draw()

    def update_plots(self):
        if self.ts_running == True:
            new_intensity = self.y_s[self.idx_y1] / self.y_s[self.idx_y2] * 100
            self.intensity_ratios.append(new_intensity)

            area1 = sum(self.y_s[self.idx_y1_min : self.idx_y1_max])
            area2 = sum(self.y_s[self.idx_y2_min : self.idx_y2_max])
            new_area = area1 / area2 * 100
            self.area_ratios.append(new_area)

            self.times = list(range(len(self.intensity_ratios)))

            if not self.init_plots:
                self.init_plot2()
                self.init_plot3()
                self.init_plots = True

            self.update_plot2()
            self.update_plot3()
            self.after(self.sample_time, self.update_plots)
        else:
            self.ts_running = True

    def init_plot2(self):
        self.intensity_ratio_plot.set_data(self.times, self.intensity_ratios)
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas2.draw()

    def init_plot3(self):
        self.area_ratio_plot.set_data(self.times, self.area_ratios)
        self.ax3.relim()
        self.ax3.autoscale_view()
        self.canvas3.draw()

    def update_plot2(self):
        xmin, xmax = self.ax2.get_xlim()
        if self.times[-1] % self.scale_factor_x == 0:
            new_xmax = self.times[-1] + self.scale_factor_x
            if new_xmax > xmax:
                self.ax2.set_xlim(xmin, new_xmax)

        self.intensity_ratio_plot.set_data(self.times, self.intensity_ratios)
        self.canvas2.draw()

    def update_plot3(self):
        xmin, xmax = self.ax3.get_xlim()
        if self.times[-1] % self.scale_factor_x == 0:
            new_xmax = self.times[-1] + self.scale_factor_x
            if new_xmax > xmax:
                self.ax3.set_xlim(xmin, new_xmax)

        self.area_ratio_plot.set_data(self.times, self.area_ratios)
        self.canvas3.draw()

    def stop_absorb(self):
        self.ts_running = False

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

    def save_data(self):
        ininame = make_results_file()
        file_path = filedialog.asksaveasfile(
            initialfile=ininame, defaultextension=".xlsx"
        )
        self.save_to_excel(file_path.name)

    def save_to_excel(self, file_path):
        df1 = pd.DataFrame(
            {"Wave Length": self.x, "Intensity": self.y, "Intensity(smooth)": self.y_s}
        )
        df2 = pd.DataFrame({"Intensity Ratio": self.intensity_ratios})
        df3 = pd.DataFrame({"Area Ratio": self.area_ratios})
        df4 = pd.DataFrame(
            {
                "积分时间(ms)": self.int_time,
                "采样时间(ms)": self.sample_time,
                "波长位置1": self.position1,
                "波长位置2": self.position2,
                "波长范围1": self.diff1,
                "波长范围2": self.diff2,
                "数据文件路径": file_path,
            }.items()
        )

        with pd.ExcelWriter(path=file_path) as writer:
            df1.to_excel(writer, sheet_name="光谱", index=False)
            df2.to_excel(writer, sheet_name="强度比", index=False)
            df3.to_excel(writer, sheet_name="面积比", index=False)
            df4.to_excel(writer, sheet_name="参数", index=False)

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
    root.title("FiberX-II")
    root.state("zoomed")

    azure_path = resource_path("azure/azure.tcl")
    root.tk.call("source", azure_path)
    root.tk.call("set_theme", "light")

    app = App(root)
    app.pack(fill="both", expand=True)

    root.mainloop()
