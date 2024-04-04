from ctypes import *
import matplotlib.pyplot as plt

error_code = 0
lib = cdll.LoadLibrary(
    r"C:\Users\ruihq\Desktop\ProfZ\sdk4.1\[4] USB Dome\[3] python demo for windows\SeaBreeze.dll"
)

# 打开所有光谱仪
devcount = lib.seabreeze_open_all_spectrometers(error_code)

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
        lib.seabreeze_get_formatted_spectrum(index, error_code, lightspec, 2048)
        y = list(lightspec)

        n = n + 1

    # 关闭激光器
    lib.seabreeze_set_laser_switch(index, error_code, 0)

# 关闭所有光谱仪
lib.seabreeze_close_all_spectrometers(error_code)
