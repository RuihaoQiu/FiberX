from ctypes import *
import numpy as np
import sys
import os

import time


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class SignalGenerator:
    def __init__(self, int_time: int = 100):
        self.index = 0
        self.n_length = 4096
        self.int_time = int_time
        source_path = ".\SeaBreeze.dll"
        self.lib = cdll.LoadLibrary(source_path)
        self.devcount = self.open_spectrometers()
        self.lib.seabreeze_set_laser_power(0, 0, 500)
        self.wavelength = (c_double * self.n_length)()
        self.lightspec = (c_double * self.n_length)()

    def start(self):
        if self.devcount == 0:
            print("请打开光谱仪。")
        else:
            # 设置积分时间
            self.lib.seabreeze_set_integration_time_microsec(
                self.index, 0, self.int_time * self.int_time
            )

            # 获取波长
            self.lib.seabreeze_get_wavelengths(
                self.index, 0, self.wavelength, self.n_length
            )
            self.lib.seabreeze_set_laser_power(self.index, 0, 0)

    def open_spectrometers(self):
        self.lib.seabreeze_open_all_spectrometers(0)

    def close_spectrometers(self):
        # 关闭光谱仪
        # self.lib.seabreeze_set_laser_switch(self.index, 0, 0)
        self.lib.seabreeze_close_all_spectrometers(0)

    def generate_x(self):
        return np.array(self.wavelength)

    def generate_y(self):
        self.lib.seabreeze_get_formatted_spectrum(
            self.index, 0, self.lightspec, self.n_length
        )
        return np.array(self.lightspec)


if __name__ == "__main__":
    sg = SignalGenerator(int_time=100)
    sg.start()
    current = time.time()
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5], time.time() - current)
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5], time.time() - current)
    sg.close_spectrometers()
    sg = SignalGenerator(int_time=1000)
    sg.start()
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5], time.time() - current)
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5], time.time() - current)
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5], time.time() - current)
