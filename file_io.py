import pandas as pd
import time


data_folder = "../data/"


def save_file(x, y, file_path):
    df = pd.DataFrame({"wavelength": x, "intensity": y})
    df.to_csv(file_path)


def load_file(file_path):
    df = pd.read_csv(file_path)
    x, y = df["wavelength"].values, df["intensity"].values
    return x, y


def save_file_dark(x, y):
    timestr = time.strftime("%y%m%d-%H%M%S")
    path = data_folder + "dark-" + timestr + ".csv"
    save_file(x, y, file_path=path)


def save_file_bright(x, y):
    timestr = time.strftime("%y%m%d-%H%M%S")
    path = data_folder + "bright-" + timestr + ".csv"
    save_file(x, y, file_path=path)
