import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from ctypes import *

error_code = 0
lib = cdll.LoadLibrary(
    r"C:\Users\ruihq\Desktop\ProfZ\sdk4.1\[4] USB Dome\[3] python demo for windows\SeaBreeze.dll"
)

# 打开所有光谱仪
devcount = lib.seabreeze_open_all_spectrometers(error_code)


class RealTimePlotApp:
    def __init__(self, root):
        self.root = root
        # self.root.title("Real-Time Plot")

        # plt.style.use("ggplot")

        self.figure, self.ax = plt.subplots()
        # Set x and y labels
        self.ax.set_xlabel("Wavelength")
        self.ax.set_ylabel("Ration")

        # plt.subplots_adjust(
        #     top=0.925, bottom=0.16, left=0.11, right=0.90, hspace=0.2, wspace=0.2
        # )

        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        if devcount == 0:
            print("请打开光谱仪。")

        if devcount > 0:
            self.index = 0
            self.wavelengths = (c_double * 2048)()
            self.lightspec = (c_double * 2048)()

            # 设置积分时间
            lib.seabreeze_set_integration_time_microsec(
                self.index, error_code, 1000 * 1000
            )

            # 获取波长
            lib.seabreeze_get_wavelengths(
                self.index, error_code, self.wavelengths, 2048
            )
            self.x_data = list(self.wavelengths)

            lib.seabreeze_set_laser_power(self.index, error_code, 0)

        (self.dot_line,) = self.ax.plot(
            [], [], "-", label="Raw Data"
        )  # Dot-line for raw data with custom color

        self.running = False

        # Create start button
        self.start_button = tk.Button(root, text="Start", command=self.start_plot)
        self.start_button.pack(side=tk.LEFT)

        # Create stop button
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_plot)
        self.stop_button.pack(side=tk.LEFT)

    def update_plot(self):
        if self.running:
            lib.seabreeze_get_formatted_spectrum(
                self.index, error_code, self.lightspec, 2048
            )
            y = list(self.lightspec)

            self.dot_line.set_data(self.x_data, y)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
            self.root.after(1000, self.update_plot)

    def start_plot(self):
        if not self.running:
            self.running = True
            self.update_plot()

    def stop_plot(self):
        self.running = False


def main():
    root = tk.Tk()
    app = RealTimePlotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
