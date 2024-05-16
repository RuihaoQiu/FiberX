import pandas as pd
import time
import os


def save_file(x, y, file_path):
    df = pd.DataFrame({"wavelength": x, "intensity": y})
    df.to_csv(file_path, lineterminator="\n")


def load_file(file_path):
    df = pd.read_csv(file_path)
    x, y = df["wavelength"].values, df["intensity"].values
    return x, y


def make_dark_file():
    timestr = time.strftime("%y%m%d-%H%M%S")
    filename = "dark-" + timestr + ".csv"
    return filename


def save_dark_file(x, y, folder):
    filename = make_dark_file()
    path = os.path.join(folder, filename)
    save_file(x, y, file_path=path)


def make_bright_file():
    timestr = time.strftime("%y%m%d-%H%M%S")
    filename = "bright-" + timestr + ".csv"
    return filename


def save_bright_file(x, y, folder):
    filename = make_bright_file()
    path = os.path.join(folder, filename)
    save_file(x, y, file_path=path)


def make_results_file():
    timestr = time.strftime("%y%m%d-%H%M%S")
    filename = "result-" + timestr + ".xlsx"
    return filename


def make_results_path(folder):
    filename = make_results_file()
    path = os.path.join(folder, filename)
    return path
