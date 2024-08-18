import sys
from PyQt5.QtCore import QTimer, Qt
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
    QScrollArea,
    QHBoxLayout,
    QButtonGroup,
    QRadioButton,
)
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt
import qdarktheme


import os
import ctypes
import pandas as pd
import openpyxl
import numpy as np
from shapely.geometry import Polygon
from scipy.ndimage import gaussian_filter1d

from device_io import SignalGenerator, resource_path
from file_io import (
    load_file,
    make_dark_file,
    make_ref_file,
    save_file,
    make_results_file,
)
from license_io import load_license_keys, load_device_keys, generate_device_id, store_device_key

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

import time
from functools import wraps


def timeit(func):
    @wraps(func)
    def timed(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.6f} seconds")
        return result

    return timed


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
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

        self.inited_absorb = False
        self.inited_plots = False

        self.x = []

        self.x_dark = []
        self.y_dark = []
        self.x_ref = []
        self.y_ref = []
        self.y_refs = []
        self.y_darks = []

        self.y_s = []

        self.x_ab = []
        self.y_abs = []

        self.times = []

        self.dark_file, self.ref_file = None, None

        if os.path.exists("data"):
            self.folder_path = "data"
            self.dark_folder = os.path.join(self.folder_path, "dark")
            self.ref_folder = os.path.join(self.folder_path, "bright")
            self.results_folder = os.path.join(self.folder_path, "results")
        else:
            self.folder_path = "."
            self.dark_folder = None
            self.ref_folder = None
            self.results_folder = None

        self.init_ui()
        self.build_input_block()
        self.build_dark_block()
        self.build_ref_block()
        self.build_range_block()
        self.build_control_block()
        self.build_display_block()
        self.build_plot_block()

    def init_ui(self):
        self.setWindowTitle("App")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

    def build_input_block(self):
        setup_frame = QGroupBox("设置")
        setup_frame.setFixedHeight(140)
        setup_layout = QGridLayout(setup_frame)

        input_frame = QWidget()
        input_layout = QGridLayout(input_frame)

        label_int_time = QLabel("积分时间(ms):")
        label_int_time.setFixedWidth(150)
        input_layout.addWidget(label_int_time, 0, 0)

        self.int_entry = QLineEdit()
        self.int_entry.setText(str(self.int_time))
        input_layout.addWidget(self.int_entry, 0, 1)

        label_sample_time = QLabel("采样时间(ms):")
        input_layout.addWidget(label_sample_time, 1, 0)

        self.sample_entry = QLineEdit()
        self.sample_entry.setText(str(self.sample_time))
        input_layout.addWidget(self.sample_entry, 1, 1)

        button_frame = QWidget()
        button_layout = QGridLayout(button_frame)

        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_real)
        button_layout.addWidget(self.start_button, 0, 0)

        self.stop_button = QPushButton("暂停")
        self.stop_button.clicked.connect(self.stop_real)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button, 0, 1)

        setup_layout.addWidget(input_frame)
        setup_layout.addWidget(button_frame)

        self.layout.addWidget(setup_frame, 0, 0)

    def build_dark_block(self):
        dark_frame = QGroupBox("暗光谱")
        dark_frame.setFixedHeight(200)
        dark_layout = QVBoxLayout(dark_frame)

        buttons_frame = QWidget()
        buttons_layout = QHBoxLayout(buttons_frame)
        select_button = QPushButton("选择路径")
        select_button.clicked.connect(self.select_dark_folder)
        buttons_layout.addWidget(select_button)
        save_dark_button = QPushButton("保存暗光谱")
        save_dark_button.clicked.connect(self.save_dark)
        buttons_layout.addWidget(save_dark_button)
        dark_layout.addWidget(buttons_frame)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scrollable_frame = QWidget()
        self.scrollable_layout = QVBoxLayout(self.scrollable_frame)
        scroll_area.setWidget(self.scrollable_frame)
        dark_layout.addWidget(scroll_area)

        self.update_dark_files()
        self.layout.addWidget(dark_frame, 1, 0)

    def build_ref_block(self):
        ref_frame = QGroupBox("参考光谱")
        ref_frame.setFixedHeight(300)
        ref_layout = QVBoxLayout(ref_frame)

        buttons_frame = QWidget()
        buttons_layout = QHBoxLayout(buttons_frame)
        select_button = QPushButton("选择路径")
        select_button.clicked.connect(self.select_ref_folder)
        buttons_layout.addWidget(select_button)
        save_ref_button = QPushButton("保存参考光谱")
        save_ref_button.clicked.connect(self.save_ref)
        buttons_layout.addWidget(save_ref_button)

        ref_layout.addWidget(buttons_frame)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scrollable_frame_2 = QWidget()
        self.scrollable_layout_2 = QVBoxLayout(self.scrollable_frame_2)
        scroll_area.setWidget(self.scrollable_frame_2)

        ref_layout.addWidget(scroll_area)

        self.update_ref_files()
        self.layout.addWidget(ref_frame, 2, 0)

    def build_range_block(self):
        range_frame = QGroupBox("面积范围")
        range_frame.setFixedHeight(80)
        range_layout = QGridLayout(range_frame)

        label = QLabel("范围(nm):")
        range_layout.addWidget(label, 0, 0, 1, 1)

        self.range1 = QLineEdit()
        self.range1.setText(str(self.range_low))
        range_layout.addWidget(self.range1, 0, 1, 1, 1)

        dash_label = QLabel("-")
        range_layout.addWidget(dash_label, 0, 2, 1, 1)

        self.range2 = QLineEdit()
        self.range2.setText(str(self.range_high))
        range_layout.addWidget(self.range2, 0, 3, 1, 1)

        self.layout.addWidget(range_frame, 3, 0)

    def build_control_block(self):
        control_frame = QGroupBox("控制")
        control_layout = QGridLayout(control_frame)

        input_frame = QWidget()
        input_layout = QGridLayout(input_frame)

        label = QLabel("质心范围(+/-):")
        label.setFixedWidth(135)
        input_layout.addWidget(label, 0, 0)
        self.diff_entry = QLineEdit()
        self.diff_entry.setText(str(self.diff))
        input_layout.addWidget(self.diff_entry, 0, 1)

        label = QLabel("强度位置(nm):")
        input_layout.addWidget(label, 1, 0)
        self.position_entry = QLineEdit()
        self.position_entry.setText(str(self.ini_position))
        input_layout.addWidget(self.position_entry, 1, 1)

        buttons_frame = QWidget()
        buttons_layout = QGridLayout(buttons_frame)

        start_ts_button = QPushButton("开始时序")
        start_ts_button.clicked.connect(self.start_absorb)
        buttons_layout.addWidget(start_ts_button, 0, 0)

        self.stop_ts_button = QPushButton("暂停时序")
        self.stop_ts_button.clicked.connect(self.stop_absorb)
        self.stop_ts_button.setEnabled(False)
        buttons_layout.addWidget(self.stop_ts_button, 0, 1)

        clean_button = QPushButton("清除时序")
        clean_button.clicked.connect(self.clean_plots)
        buttons_layout.addWidget(clean_button, 1, 0)

        save_button = QPushButton("保存数据")
        save_button.clicked.connect(self.save_data)
        buttons_layout.addWidget(save_button, 1, 1)

        control_layout.addWidget(input_frame)
        control_layout.addWidget(buttons_frame)

        self.layout.addWidget(control_frame, 4, 0)

    def build_display_block(self):
        real_frame = QGroupBox("实时数据")
        real_layout = QGridLayout(real_frame)

        self.toggle_button = QPushButton("最低点")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.toggle_switch)
        real_layout.addWidget(self.toggle_button, 1, 0)

        self.min_label = QLabel("")
        self.min_label.setFont(QFont('Arial', 12, QFont.Bold)) 
        real_layout.addWidget(self.min_label, 1, 1)

        label = QLabel("质心:")
        real_layout.addWidget(label, 2, 0)

        self.centroid_label = QLabel("")
        self.centroid_label.setFont(QFont('Arial', 12, QFont.Bold)) 
        real_layout.addWidget(self.centroid_label, 2, 1)

        self.layout.addWidget(real_frame, 5, 0, 1, 1, Qt.AlignTop)

    def build_plot_block(self):
        self.paned = QSplitter(self)
        self.layout.addWidget(self.paned, 0, 1, 6, 1)

        self.notebook = QTabWidget(self.paned)
        self.paned.addWidget(self.notebook)

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()
        self.build_tab4()
        self.build_tab5()
        self.build_tab6()

    def start_real(self):
        self.stop_button.setEnabled(True)

        self.int_timer = QTimer()
        self.int_time = int(self.int_entry.text())

        if self.inited_absorb == False:
            self.init_real()

        self.int_timer.timeout.connect(self.update_real)
        self.int_timer.start(self.int_time)

    def init_real(self):
        self.signal_generator = SignalGenerator(int_time=self.int_time)
        self.signal_generator.start()
        self.x = self.signal_generator.generate_x()
        self.y = self.signal_generator.generate_y()
        self.y_s = gaussian_filter1d(self.y, sigma=100)
        self.plot1_real.set_data(self.x, self.y_s)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.inited_absorb = True
        self.init_ratio()

    def update_real(self):
        self.x = self.signal_generator.generate_x()
        self.y = self.signal_generator.generate_y()
        self.y_s = gaussian_filter1d(self.y, sigma=100)
        self.plot1_real.set_data(self.x, self.y_s)
        self.canvas1.mpl_connect("scroll_event", self.on_scroll)
        self.canvas1.draw()
        self.update_ratio()

    def select_dark_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择暗光谱文件夹")
        if folder:
            self.dark_folder = folder
            self.build_dark_block()

    def save_dark(self):
        ininame = make_dark_file()
        full_path = os.path.join(self.dark_folder, ininame)
        dark_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            full_path,
            'CSV(*.csv)'
        )
        if dark_path:
            save_file(self.x, self.y, dark_path)
            self.build_dark_block()

    def update_dark_files(self):
        if self.dark_folder:
            self.radio_buttons_group = QButtonGroup(self.scrollable_frame)
            filenames = os.listdir(self.dark_folder)
            for filename in filenames:
                radio_button = QRadioButton(filename)
                radio_button.toggled.connect(
                    lambda checked, file=filename: self.load_dark(checked, file)
                )
                self.scrollable_layout.addWidget(radio_button)
                self.radio_buttons_group.addButton(radio_button)
        else:
            label = QLabel("请选择暗光谱文件夹。")

    def select_ref_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择参考光谱文件夹")
        if folder:
            self.ref_folder = folder
            self.build_ref_block()

    def save_ref(self):
        ininame = make_ref_file()
        full_path = os.path.join(self.ref_folder, ininame)
        ref_path, _ = QFileDialog.getSaveFileName(self, "Save As", full_path, 'CSV(*.csv)')
        if ref_path:
            save_file(self.x, self.y, ref_path)
            self.build_ref_block()

    def update_ref_files(self):
        if self.ref_folder:
            self.radio_buttons_group = QButtonGroup(self.scrollable_frame_2)
            filenames = os.listdir(self.ref_folder)
            for filename in filenames:
                radio_button = QRadioButton(filename)
                radio_button.toggled.connect(
                    lambda checked, file=filename: self.load_ref(checked, file)
                )
                self.scrollable_layout_2.addWidget(radio_button)
                self.radio_buttons_group.addButton(radio_button)
        # else:
        #     label = QLabel("请选择暗光谱文件夹。")

    def start_absorb(self):
        self.stop_ts_button.setEnabled(True)
        self.sample_time = int(self.sample_entry.text())
        self.diff = int(self.diff_entry.text())
        self.position = int(self.position_entry.text())
        closest_x = self.find_interval(self.x, self.position)
        self.idx_y = list(self.x).index(closest_x)

        self.calculate_ref_area()

        self.sample_timer = QTimer()
        self.sample_time = int(self.sample_entry.text())
        self.sample_timer.timeout.connect(self.update_plots)
        self.sample_timer.start(self.sample_time)

    def calculate_ref_area(self):
        self.range_low = int(self.range1.text())
        closest_range1 = self.find_interval(self.x, self.range_low)
        self.range1_idx = list(self.x).index(closest_range1)

        self.range_high = int(self.range2.text())
        closest_range2 = self.find_interval(self.x, self.range_high)
        self.range2_idx = list(self.x).index(closest_range2)

        self.area_ref = np.dot(
            self.x_ref[self.range1_idx : self.range2_idx],
            self.y_refs[self.range1_idx : self.range2_idx],
        )

    def update_plots(self):
        try:
            self.make_absorb()
            self.min_idx = self.find_minimum(self.y_abs)

            if self.fix_minimum == False:
                self.min_idx_display = self.min_idx
                self.update_min_value()

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

            if not self.inited_plots:
                self.auto_rescale3()
                self.auto_rescale4()
                self.auto_rescale5()
                self.auto_rescale6()
                self.inited_plots = True

            current_idx = int(self.notebook.currentIndex()) + 1

            if current_idx == 3:
                self.update_plot3()

            if current_idx == 4:
                self.update_plot4()

            if current_idx == 5:
                self.update_plot5()

            if current_idx == 6:
                self.update_plot6()

        except ValueError:
            pass
        except IndexError:
            pass

    def toggle_switch(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setText("固定最低点")
        else:
            self.toggle_button.setText("最低点")
        self.fix_minimum = not self.fix_minimum

    def stop_absorb(self):
        self.stop_ts_button.setEnabled(False)
        self.sample_timer.stop()

    def load_dark(self, checked, file):
        if checked:
            self.dark_file = os.path.join(self.dark_folder, file)
            self.x_dark, self.y_dark = load_file(self.dark_file)
            self.y_darks = gaussian_filter1d(self.y_dark, sigma=100)
            self.plot1_dark.set_data(self.x_dark, self.y_darks)
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas1.draw()

            if len(self.y_s) > 0:
                self.init_ratio()
                self.update_ratio()

    def load_ref(self, checked, file):
        if checked:
            self.ref_file = os.path.join(self.ref_folder, file)
            self.x_ref, self.y_ref = load_file(self.ref_file)
            self.y_refs = gaussian_filter1d(self.y_ref, sigma=100)
            self.plot1_ref.set_data(self.x_ref, self.y_refs)
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.canvas1.draw()

            if len(self.y_s) > 0:
                self.init_ratio()
                self.update_ratio()

    def init_ratio(self):
        if (len(self.y_refs) > 0) and (len(self.y_darks) > 0):
            self.make_absorb()
            self.init_plot2()
        else:
            pass

    def stop_real(self):
        self.stop_button.setEnabled(False)
        self.signal_generator.close_spectrometers()
        self.inited_absorb = False
        self.int_timer.stop()

    def clean_plots(self):
        self.times, self.centroids, self.centroids_sm, self.intensities, self.mins, self.area_ratios = (
            [],
            [],
            [],
            [],
            [],
            [],
        )
        self.plot3_time.set_data([], [])
        self.plot3_smooth.set_data([], [])
        self.canvas3.draw()
        self.plot4_intensity.set_data([], [])
        self.canvas4.draw()
        self.plot5_lowest.set_data([], [])
        self.canvas5.draw()
        self.plot6_area.set_data([], [])
        self.canvas6.draw()
        self.sample_timer.stop()

    def build_tab1(self):
        tab1 = QWidget()
        self.notebook.addTab(tab1, "光谱")
        tab1_layout = QGridLayout(tab1)

        plot_frame = QFrame(tab1)
        plot_frame_layout = QVBoxLayout(plot_frame)
        plot_frame.setLayout(plot_frame_layout)
        tab1_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig1, self.ax1 = plt.subplots()
        self.ax1.set_xlabel("Wavelength")
        self.ax1.set_ylabel("Intensity")
        (self.plot1_real,) = self.ax1.plot([], [], "-", label="Real time")
        (self.plot1_ref,) = self.ax1.plot([], [], "-", label="Reference")
        (self.plot1_dark,) = self.ax1.plot([], [], "-", label="Dark")
        self.ax1.legend()

        self.canvas1 = FigureCanvas(fig1)
        plot_frame_layout.addWidget(self.canvas1)
        self.canvas1.mpl_connect("scroll_event", self.on_scroll)

        auto_button = QPushButton("自适应")
        auto_button.setFixedWidth(100)
        auto_button.clicked.connect(self.auto_rescale1)
        tab1_layout.addWidget(auto_button, 3, 0)

        toolbar = NavigationToolbar(self.canvas1, plot_frame)
        toolbar.setFixedHeight(50)
        tab1_layout.addWidget(toolbar, 3, 1, 1, 1)

    def build_tab2(self):
        tab2 = QWidget()
        self.notebook.addTab(tab2, "透射")
        tab2_layout = QGridLayout(tab2)

        plot_frame = QFrame(tab2)
        plot_frame_layout = QVBoxLayout(plot_frame)
        plot_frame.setLayout(plot_frame_layout)
        tab2_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig2, self.ax2 = plt.subplots()
        self.ax2.set_xlabel("Wavelength")
        self.ax2.set_ylabel("Ratio")
        (self.plot2_absorb,) = self.ax2.plot([], [], "-", label="Real time")
        (self.plot2_center,) = self.ax2.plot([], [], ".", label="Centroid")

        self.canvas2 = FigureCanvas(fig2)
        plot_frame_layout.addWidget(self.canvas2)
        self.canvas2.mpl_connect("scroll_event", self.on_scroll)

        auto_button = QPushButton("自适应")
        auto_button.setFixedWidth(100)
        auto_button.clicked.connect(self.auto_rescale2)
        tab2_layout.addWidget(auto_button, 3, 0)

        toolbar = NavigationToolbar(self.canvas2, plot_frame)
        toolbar.setFixedHeight(50)
        tab2_layout.addWidget(toolbar, 3, 1, 1, 1)

    def build_tab3(self):
        tab3 = QWidget()
        self.notebook.addTab(tab3, "时序")
        tab3_layout = QGridLayout(tab3)

        plot_frame = QFrame(tab3)
        plot_frame_layout = QVBoxLayout(plot_frame)
        plot_frame.setLayout(plot_frame_layout)
        tab3_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig3, self.ax3 = plt.subplots()
        self.ax3.set_xlabel("Time")
        self.ax3.set_ylabel("Wavelength")
        (self.plot3_time,) = self.ax3.plot([], [], "-", label="Real time")
        (self.plot3_smooth,) = self.ax3.plot([], [], "-", label="Real time smooth")
        self.ax3.legend()

        self.canvas3 = FigureCanvas(fig3)
        plot_frame_layout.addWidget(self.canvas3)
        self.canvas3.mpl_connect("scroll_event", self.on_scroll)

        auto_button = QPushButton("自适应")
        auto_button.setFixedWidth(100)
        auto_button.clicked.connect(self.auto_rescale3)
        tab3_layout.addWidget(auto_button, 3, 0)

        toolbar = NavigationToolbar(self.canvas3, plot_frame)
        toolbar.setFixedHeight(50)
        tab3_layout.addWidget(toolbar, 3, 1, 1, 1)

    def build_tab4(self):
        tab4 = QWidget()
        self.notebook.addTab(tab4, "强度时序")
        tab4_layout = QGridLayout(tab4)

        plot_frame = QFrame(tab4)
        plot_frame_layout = QVBoxLayout(plot_frame)
        plot_frame.setLayout(plot_frame_layout)
        tab4_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig4, self.ax4 = plt.subplots()
        self.ax4.set_xlabel("Time")
        self.ax4.set_ylabel("Wavelength")
        (self.plot4_intensity,) = self.ax4.plot([], [], "-")

        self.canvas4 = FigureCanvas(fig4)
        plot_frame_layout.addWidget(self.canvas4)
        self.canvas4.mpl_connect("scroll_event", self.on_scroll)

        auto_button = QPushButton("自适应")
        auto_button.setFixedWidth(100)
        auto_button.clicked.connect(self.auto_rescale4)
        tab4_layout.addWidget(auto_button, 3, 0)

        toolbar = NavigationToolbar(self.canvas4, plot_frame)
        toolbar.setFixedHeight(50)
        tab4_layout.addWidget(toolbar, 3, 1, 1, 1)

    def build_tab5(self):
        tab5 = QWidget()
        self.notebook.addTab(tab5, "最低点")
        tab5_layout = QGridLayout(tab5)

        plot_frame = QFrame(tab5)
        plot_frame_layout = QVBoxLayout(plot_frame)
        plot_frame.setLayout(plot_frame_layout)
        tab5_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig5, self.ax5 = plt.subplots()
        self.ax5.set_xlabel("Time")
        self.ax5.set_ylabel("Wavelength")
        (self.plot5_lowest,) = self.ax5.plot([], [], "-")

        self.canvas5 = FigureCanvas(fig5)
        plot_frame_layout.addWidget(self.canvas5)
        self.canvas5.mpl_connect("scroll_event", self.on_scroll)

        auto_button = QPushButton("自适应")
        auto_button.setFixedWidth(100)
        auto_button.clicked.connect(self.auto_rescale5)
        tab5_layout.addWidget(auto_button, 3, 0)

        toolbar = NavigationToolbar(self.canvas5, plot_frame)
        toolbar.setFixedHeight(50)
        tab5_layout.addWidget(toolbar, 3, 1, 1, 1)

    def build_tab6(self):
        tab6 = QWidget()
        self.notebook.addTab(tab6, "波长x强度")
        tab6_layout = QGridLayout(tab6)

        plot_frame = QFrame(tab6)
        plot_frame_layout = QVBoxLayout(plot_frame)
        plot_frame.setLayout(plot_frame_layout)
        tab6_layout.addWidget(plot_frame, 0, 0, 3, 3)

        fig6, self.ax6 = plt.subplots()
        self.ax6.set_xlabel("Time")
        self.ax6.set_ylabel("Wavelength")
        (self.plot6_area,) = self.ax6.plot([], [], "-")

        self.canvas6 = FigureCanvas(fig6)
        plot_frame_layout.addWidget(self.canvas6)
        self.canvas6.mpl_connect("scroll_event", self.on_scroll)

        auto_button = QPushButton("自适应")
        auto_button.setFixedWidth(100)
        auto_button.clicked.connect(self.auto_rescale6)
        tab6_layout.addWidget(auto_button, 3, 0)

        toolbar = NavigationToolbar(self.canvas6, plot_frame)
        toolbar.setFixedHeight(50)
        tab6_layout.addWidget(toolbar, 3, 1, 1, 1)

    def auto_rescale1(self):
        if len(self.x)>0:
            self.ax1.set_xlim(min(self.x) - 50, max(self.x) + 50)
            y = list(self.y_s) + list(self.y_darks) + list(self.y_refs)
            delta = max(y) - min(y)
            self.ax1.set_ylim(
                min(y) - 0.1 * delta,
                max(y) + 0.1 * delta,
            )
            self.canvas1.draw()

    def auto_rescale2(self):
        if len(self.x)>0:
            self.ax1.set_xlim(min(self.x) - 50, max(self.x) + 50)
            delta = max(self.y_abs) - min(self.y_abs)
            self.ax2.set_ylim(
                min(self.y_abs) - 0.1 * delta,
                max(self.y_abs) + 0.1 * delta,
            )
            self.canvas2.draw()

    def auto_rescale3(self):
        if len(self.times)>0:
            xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
            self.ax3.set_xlim(0, xmax)
            delta = max(self.centroids) - min(self.centroids)
            self.ax3.set_ylim(
                min(self.centroids) - 0.1 * delta,
                max(self.centroids) + 0.1 * delta,
            )
            self.canvas3.draw()

    def auto_rescale4(self):
        if len(self.times)>0:
            xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
            self.ax4.set_xlim(0, xmax)
            delta = max(self.intensities) - min(self.intensities)
            self.ax4.set_ylim(
                min(self.intensities) - 0.1 * delta,
                max(self.intensities) + 0.1 * delta,
            )
            self.canvas4.draw()

    def auto_rescale5(self):
        if len(self.times)>0:
            xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
            self.ax5.set_xlim(0, xmax)
            delta = max(self.mins) - min(self.mins)
            self.ax5.set_ylim(
                min(self.mins) - 0.1 * delta,
                max(self.mins) + 0.1 * delta,
            )
            self.canvas5.draw()

    def auto_rescale6(self):
        if len(self.times)>0:
            xmax = (int(self.times[-1] / self.scale_factor_x) + 1) * self.scale_factor_x
            self.ax6.set_xlim(0, xmax)
            delta = max(self.area_ratios) - min(self.area_ratios)
            self.ax6.set_ylim(
                min(self.area_ratios) - 0.1 * delta,
                max(self.area_ratios) + 0.1 * delta,
            )
            self.canvas6.draw()

    def make_absorb(self):
        self.x_ab = self.x[:3000]
        self.y_abs = (
            abs(
                (self.y_s[:3000] - self.y_darks[:3000])
                / (self.y_refs[:3000] - self.y_darks[:3000])
            )
            * 100
        )

    def update_ratio(self):
        if (len(self.y_refs) > 0) and (len(self.y_darks) > 0):
            self.make_absorb()
            self.update_plot2()
        else:
            pass

    def update_min_value(self):
        self.min_label.setText(f"{self.x[self.min_idx_display]:.3f}")

    def update_center_value(self):
        self.centroid_label.setText(f"{self.centroid_x:.3f}")

    def init_plot2(self):
        self.plot2_absorb.set_data(self.x_ab, self.y_abs)
        if self.centroid_x:
            self.plot2_center.set_data([self.centroid_x], [self.centroid_y])
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas2.draw()

    def init_plot3(self):
        self.plot3_time.set_data(self.times, self.centroids)
        self.plot3_smooth.set_data(self.times, self.centroids_sm)
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
        self.canvas2.draw()

    def update_plot3(self):
        xmin, xmax = self.ax3.get_xlim()
        if self.times[-1] % self.scale_factor_x == 0:
            new_xmax = self.times[-1] + self.scale_factor_x
            if new_xmax > xmax:
                self.ax3.set_xlim(xmin, new_xmax)

        self.plot3_time.set_data(self.times, self.centroids)
        self.plot3_smooth.set_data(self.times, self.centroids_sm)
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
        result_path, _ = QFileDialog.getSaveFileName(self, "Save As", ininame, 'Excel (*.xlsx *.xls)')
        self.save_to_excel(result_path)

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
            {"time": np.array(range(len(self.centroids)))*self.sample_time/1000, "Centroid": self.centroids, "Centroid(smooth)": self.centroids_sm}
        )

        df4 = pd.DataFrame(
            {"time": np.array(range(len(self.intensities)))*self.sample_time/1000, "Intensity": self.intensities, "Intensity(smooth)": self.intensities_sm}
        )

        df5 = pd.DataFrame({"time": np.array(range(len(self.mins)))*self.sample_time/1000, "Minimal": self.mins})

        df6 = pd.DataFrame({"time": np.array(range(len(self.area_ratios)))*self.sample_time/1000, "Ratio of area": self.area_ratios})

        df7 = pd.DataFrame(
            {
                "积分时间(ms)": self.int_time,
                "采样时间(ms)": self.sample_time,
                "暗光谱": self.dark_file,
                "参考光谱": self.ref_file,
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


def start_app():
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("light")
    window = App()
    window.setWindowTitle("FiberX")
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    stored_license_keys = load_license_keys()
    stored_device_keys = load_device_keys()
    current_device_key = generate_device_id()

    if current_device_key in stored_device_keys:
        print("Already activated!")
        start_app()
    
    else:
        print("Please enter your license key:")
        input_license_key = input().strip()

        if input_license_key in stored_license_keys:
            print("Correct!")
            store_device_key(current_device_key)
            start_app()

        else:
            print("Please enter the correct key.")
