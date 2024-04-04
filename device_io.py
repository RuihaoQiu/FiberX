from ctypes import *
import time

source_path = r"C:\Users\ruihq\Desktop\ProfZ\sdk4.1\[4] USB Dome\[3] python demo for windows\SeaBreeze.dll"


class signal_generator:
    def __init__(self):
        self.index = 0
        self.n_x = 2084
        self.n_time = 1000
        self.lib = cdll.LoadLibrary(source_path)
        self.devcount = self.lib.seabreeze_open_all_spectrometers(0)

        self.wavelength = (c_double * self.n_x)()
        self.lightspec = (c_double * self.n_x)()

    def start(self):
        if self.devcount == 0:
            print("请打开光谱仪。")
        else:
            # 设置积分时间
            self.lib.seabreeze_set_integration_time_microsec(
                self.index, 0, self.n_time * self.n_time
            )

            # 获取波长
            self.lib.seabreeze_get_wavelengths(self.index, 0, self.wavelength, self.n_x)
            self.lib.seabreeze_set_laser_power(self.index, 0, 0)
            self.x = list(self.wavelength)

    def generate_x(self):
        return self.x

    def generate_y(self):
        self.lib.seabreeze_get_formatted_spectrum(
            self.index, 0, self.lightspec, self.n_x
        )
        return list(self.lightspec)


if __name__ == "__main__":
    sg = signal_generator()
    sg.start()
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5])
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5])
