from ctypes import *
import time

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

error_code = 0
lib = cdll.LoadLibrary(
    r"C:\Users\ruihq\Desktop\ProfZ\sdk4.1\[4] USB Dome\[3] python demo for windows\SeaBreeze.dll"
)
devcount = lib.seabreeze_open_all_spectrometers(error_code)  # 打开所有光谱仪


if devcount == 0:
    print("请打开光谱仪。")

if devcount > 0:
    index = 0
    n = 0
    wavelengths = (c_double * 2048)()
    lightspec = (c_double * 2048)()

    # 设置积分时间
    lib.seabreeze_set_integration_time_microsec(index, error_code, 1000 * 1000)

    # 获取波长
    lib.seabreeze_get_wavelengths(index, error_code, wavelengths, 2048)
    x = list(wavelengths)

    lib.seabreeze_set_laser_power(index, error_code, 0)
    while n < 5:
        lib.seabreeze_get_formatted_spectrum(
            index, error_code, lightspec, 2048
        )  # 获取亮光谱
        y = list(lightspec)
        print(y[:5])
        n = n + 1

    lib.seabreeze_set_laser_switch(index, error_code, 0)  # 关闭激光器

lib.seabreeze_close_all_spectrometers(error_code)  # 关闭所有光谱仪


# # Create figure and plot
# fig, ax = plt.subplots()
# ax.plot(x, y, marker='o', linestyle='-')
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_title('X-Y Plot')

# # Create tkinter window
# root = tk.Tk()
# root.title("X-Y Plot")

# # Embed the matplotlib plot into tkinter window
# canvas = FigureCanvasTkAgg(fig, master=root)
# canvas.draw()
# canvas.get_tk_widget().pack()

# # Start tkinter event loop
# root.mainloop()
