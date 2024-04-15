from ctypes import *
import time

source_path = r"C:\Users\ruihq\Desktop\ProfZ\sdk4.1\[4] USB Dome\[3] python demo for windows\SeaBreeze.dll"


class SignalGenerator:
    def __init__(self, int_time: int = 1000):
        self.index = 0
        self.n_length = 2048
        self.int_time = int_time
        self.lib = cdll.LoadLibrary(source_path)
        self.devcount = self.lib.seabreeze_open_all_spectrometers(0)
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
            self.x = list(self.wavelength)

    def stop_laser(self):
        # 关闭激光器
        self.lib.seabreeze_set_laser_switch(self.index, 0, 0)

    def generate_x(self):
        return self.x

    def generate_y(self):
        self.lib.seabreeze_get_formatted_spectrum(
            self.index, 0, self.lightspec, self.n_length
        )
        return list(self.lightspec)


if __name__ == "__main__":
    sg = SignalGenerator()
    sg.start()
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5])
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5])
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5])
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5])
    x = sg.generate_x()
    y = sg.generate_y()
    print(x[:5], y[:5])
