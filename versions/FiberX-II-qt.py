import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QGroupBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTabWidget,
    QFrame,
    QVBoxLayout,
    QFileDialog,
    QApplication,
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt
import ctypes
import pandas as pd
import numpy as np
import openpyxl
from scipy.ndimage import gaussian_filter1d
from device_io import SignalGenerator
from file_io import make_results_file
import qdarktheme

ctypes.windll.shcore.SetProcessDpiAwareness(2)
ctypes.windll.kernel32.SetDllDirectoryW(None)

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.figsize": (16, 9),
        "figure.autolayout": True,
        "lines.linewidth": 3.0,
        "lines.markersize": 10.0,
        "font.size": 14,
    }
)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.running = True
        self.ts_running = True
        self.int_time = 200
        self.sample_time = 1000
        self.position1 = 600
        self.position2 = 900
        self.diff1 = 25
        self.diff2 = 25
        self.scale_factor_x = 50
        self.idx_y1, self.idx_y2 = None, None
        self.area_ratios = []
        self.intensity_ratios = []
        self.init_absorb = False
        self.init_plots = False
        self.results_folder = None

        self.x = []
        self.times = []


        self.build_input_block()
        self.build_control_block()
        self.build_plot_block()

    def init_ui(self):
        self.setWindowTitle("App")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

    def build_input_block(self):
        input_frame = QGroupBox("设置")
        input_frame.setFixedHeight(120)
        input_layout = QGridLayout(input_frame)
        self.layout.addWidget(input_frame, 0, 0)

        label = QLabel("积分时间(ms):")
        label.setFixedWidth(110)
        input_layout.addWidget(label, 0, 0)
        self.int_entry = QLineEdit()
        self.int_entry.setText(str(self.int_time))
        input_layout.addWidget(self.int_entry, 0, 1)

        label = QLabel("采样时间(ms):")
        input_layout.addWidget(label, 1, 0)
        self.sample_entry = QLineEdit()
        self.sample_entry.setText(str(self.sample_time))
        input_layout.addWidget(self.sample_entry, 1, 1)

        start_button = QPushButton("开始")
        start_button.clicked.connect(self.start_real)
        input_layout.addWidget(start_button, 2, 0)

        self.stop_button = QPushButton("暂停")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_real)
        input_layout.addWidget(self.stop_button, 2, 1)

    def build_control_block(self):
        control_frame = QGroupBox("时序")
        control_layout = QGridLayout(control_frame)
        self.layout.addWidget(control_frame, 1, 0)

        label = QLabel("波长位置(nm)-I:")
        label.setFixedWidth(110)
        control_layout.addWidget(label, 0, 0)
        self.w1_entry = QLineEdit()
        self.w1_entry.setText(str(self.position1))
        control_layout.addWidget(self.w1_entry, 0, 1)

        label = QLabel("波长位置(nm)-II:")
        control_layout.addWidget(label, 1, 0)
        self.w2_entry = QLineEdit()
        self.w2_entry.setText(str(self.position2))
        control_layout.addWidget(self.w2_entry, 1, 1)

        label = QLabel("波长范围(nm)-I:")
        control_layout.addWidget(label, 2, 0)
        self.range1_entry = QLineEdit()
        self.range1_entry.setText(str(self.diff1))
        control_layout.addWidget(self.range1_entry, 2, 1)

        label = QLabel("波长范围(nm)-II:")
        control_layout.addWidget(label, 3, 0)
        self.range2_entry = QLineEdit()
        self.range2_entry.setText(str(self.diff2))
        control_layout.addWidget(self.range2_entry, 3, 1)

        start_button = QPushButton("开始时序")
        start_button.clicked.connect(self.start_absorb)
        control_layout.addWidget(start_button, 4, 0)

        self.stop_ts_button = QPushButton("暂停时序")
        self.stop_ts_button.setEnabled(False)
        self.stop_ts_button.clicked.connect(self.stop_absorb)
        control_layout.addWidget(self.stop_ts_button, 4, 1)

        clean_button = QPushButton("清除时序")
        clean_button.clicked.connect(self.clean_plots)
        control_layout.addWidget(clean_button, 5, 0)

        save_button = QPushButton("保存数据")
        save_button.clicked.connect(self.save_data)
        control_layout.addWidget(save_button, 5, 1)

    def build_plot_block(self):
        self.splitter = QSplitter()
        self.layout.addWidget(self.splitter, 0, 1, 6, 1)
        self.notebook = QTabWidget(self.splitter)

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()

    def build_tab1(self):
        tab1 = QWidget()
        self.notebook.addTab(tab1, "光谱")

        tab1_layout = QGridLayout(tab1)

        plot_frame = QFrame(tab1)
        plot_frame_layout = QVBoxLayout(plot_frame)
        tab1_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")

        self.canvas1 = FigureCanvas(fig1)
        plot_frame_layout.addWidget(self.canvas1)

        toolbar = NavigationToolbar(self.canvas1, plot_frame)
        toolbar.setFixedHeight(50)
        tab1_layout.addWidget(toolbar, 3, 1, 1, 3)

        (self.realtime,) = self.ax1.plot([], [], "-")

        auto_button = QPushButton("自适应")
        auto_button.clicked.connect(self.auto_rescale1)
        auto_button.setFixedWidth(100)
        tab1_layout.addWidget(auto_button, 3, 0)

    def build_tab2(self):
        tab2 = QWidget()
        self.notebook.addTab(tab2, "强度比")

        tab2_layout = QGridLayout(tab2)

        plot_frame = QFrame(tab2)
        plot_frame_layout = QVBoxLayout(plot_frame)
        tab2_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlabel("Wavelength")
        self.ax2.set_ylabel("Intensity Ratio(%)")

        self.canvas2 = FigureCanvas(fig2)
        plot_frame_layout.addWidget(self.canvas2)

        toolbar = NavigationToolbar(self.canvas2, tab2)
        toolbar.setFixedHeight(50)
        tab2_layout.addWidget(toolbar, 3, 1, 1, 3)

        self.canvas2.mpl_connect("scroll_event", self.on_scroll)
        (self.intensity_ratio_plot,) = self.ax2.plot([], [], "-")

        auto_button = QPushButton("自适应")
        auto_button.clicked.connect(self.auto_rescale2)
        auto_button.setFixedWidth(100)
        tab2_layout.addWidget(auto_button, 3, 0)

    def build_tab3(self):
        tab3 = QWidget()
        self.notebook.addTab(tab3, "强度面积比")

        tab3_layout = QGridLayout(tab3)

        plot_frame = QFrame(tab3)
        plot_frame_layout = QVBoxLayout(plot_frame)
        tab3_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig3, self.ax3 = plt.subplots()
        self.ax3.set_xlabel("Time")
        self.ax3.set_ylabel("Area Ratio(%)")

        self.canvas3 = FigureCanvas(fig3)
        plot_frame_layout.addWidget(self.canvas3)

        toolbar = NavigationToolbar(self.canvas3, tab3)
        toolbar.setFixedHeight(50)
        tab3_layout.addWidget(toolbar, 3, 1, 1, 3)

        self.canvas3.mpl_connect("scroll_event", self.on_scroll)
        (self.area_ratio_plot,) = self.ax3.plot([], [], "-")

        auto_button = QPushButton("自适应")
        auto_button.clicked.connect(self.auto_rescale3)
        auto_button.setFixedWidth(100)
        tab3_layout.addWidget(auto_button, 3, 0)

    def init_real(self):
        self.int_time = int(self.int_entry.text())
        self.signal_generator = SignalGenerator(int_time=self.int_time)
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
        self.stop_button.setEnabled(True)
        if not self.init_absorb:
            self.init_real()
            self.update_real()
        else:
            self.update_real()

    def update_real(self):
        if self.running:
            self.x = self.signal_generator.generate_x()
            self.y = self.signal_generator.generate_y()
            self.y_s = gaussian_filter1d(self.y, sigma=100)
            self.realtime.set_data(self.x, self.y_s)
            self.canvas1.mpl_connect("scroll_event", self.on_scroll)
            self.canvas1.draw()
            QTimer.singleShot(self.int_time, self.update_real)
        else:
            self.running = True

    def stop_real(self):
        self.stop_button.setEnabled(False)
        self.signal_generator.close_spectrometers()
        self.init_absorb = False
        self.running = False

    def on_scroll(self, event):
        ax = event.inaxes
        if ax is None:
            return

        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return

        base_scale = 1.1
        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            return

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

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

    def start_absorb(self):
        self.stop_ts_button.setEnabled(True)
        self.sample_time = int(self.sample_entry.text())
        self.timer = QTimer()
        self.read_inputs()
        self.get_idx()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(self.sample_time)

    def read_inputs(self):
        self.position1 = int(self.w1_entry.text())
        self.diff1 = int(self.range1_entry.text())

        self.position2 = int(self.w2_entry.text())
        self.diff2 = int(self.range2_entry.text())

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
        self.timer.stop()

    def save_data(self):
        ininame = make_results_file()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            ininame,
            "Excel Files (*.xlsx);;All Files (*)",
            options=options,
        )
        self.save_to_excel(file_path)

    def save_to_excel(self, file_path):
        df1 = pd.DataFrame(
            {"Wave Length": self.x, "Intensity": self.y, "Intensity(smooth)": self.y_s}
        )
        df2 = pd.DataFrame({"time": np.array(range(len(self.intensity_ratios)))*self.sample_time/1000, "Intensity Ratio": self.intensity_ratios})
        df3 = pd.DataFrame({"time": np.array(range(len(self.area_ratios)))*self.sample_time/1000, "Area Ratio": self.area_ratios})
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

    def auto_rescale1(self):
        if len(self.x)>0:
            delta_x = max(self.x) - min(self.x)
            self.ax1.set_xlim(
                min(self.x) - 0.05 * delta_x,
                max(self.x) + 0.05 * delta_x,
            )
            delta_y = max(self.y_s) - min(self.y_s)
            self.ax1.set_ylim(
                min(self.y_s) - 0.1 * delta_y,
                max(self.y_s) + 0.1 * delta_y,
            )
            self.canvas1.draw()

    def auto_rescale2(self):
        if len(self.times)>0:
            xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
            self.ax2.set_xlim(0, xmax)
            delta = max(self.intensity_ratios) - min(self.intensity_ratios)
            self.ax2.set_ylim(
                min(self.intensity_ratios) - 0.1 * delta,
                max(self.intensity_ratios) + 0.1 * delta,
            )
            self.canvas2.draw()

    def auto_rescale3(self):
        if len(self.times)>0:
            xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
            self.ax3.set_xlim(0, xmax)
            delta = max(self.area_ratios) - min(self.area_ratios)
            self.ax3.set_ylim(
                min(self.area_ratios) - 0.1 * delta, max(self.area_ratios) + 0.1 * delta
            )
            self.canvas3.draw()

    def update_plots(self):
        new_intensity = self.y_s[self.idx_y1] / self.y_s[self.idx_y2] * 100
        self.intensity_ratios.append(new_intensity)

        area1 = sum(self.y_s[self.idx_y1_min : self.idx_y1_max])
        area2 = sum(self.y_s[self.idx_y2_min : self.idx_y2_max])
        new_area = area1 / area2 * 100
        self.area_ratios.append(new_area)

        self.times = list(range(len(self.intensity_ratios)))

        current_idx = int(self.notebook.currentIndex()) + 1

        if not self.init_plots:
            self.init_plot2()
            self.init_plot3()
            self.init_plots = True

        if current_idx == 2:
            self.update_plot2()

        if current_idx == 3:
            self.update_plot3()


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
        self.timer.stop()
        self.stop_ts_button.setEnabled(False)

    @staticmethod
    def find_interval(arr, value):
        if value < arr[0]:
            return arr[0]
        elif value >= arr[-1]:
            return arr[-1]

        low, high = 0, len(arr) - 1
        while low <= high:
            mid = (low + high) // 2
            if arr[mid] <= value < arr[mid + 1]:
                return arr[mid]
            elif value < arr[mid]:
                high = mid - 1
            else:
                low = mid + 1


if __name__ == "__main__":
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = App()
    window.setWindowTitle("FiberX-II")
    window.showMaximized()
    sys.exit(app.exec_())
