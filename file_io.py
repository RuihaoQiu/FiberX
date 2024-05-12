import pandas as pd
import time
import os


dark_folder = "../data/dark/"
bright_folder = "../data/bright/"
results_folder = "../data/results/"


def save_file(x, y, file_path):
    df = pd.DataFrame({"wavelength": x, "intensity": y})
    df.to_csv(file_path)


def load_file(file_path):
    df = pd.read_csv(file_path)
    x, y = df["wavelength"].values, df["intensity"].values
    return x, y


def save_dark_file(x, y, folder):
    timestr = time.strftime("%y%m%d-%H%M%S")
    filename = "dark-" + timestr + ".csv"
    path = os.path.join(folder, filename)
    save_file(x, y, file_path=path)


def save_bright_file(x, y, folder):
    timestr = time.strftime("%y%m%d-%H%M%S")
    filename = "bright-" + timestr + ".csv"
    path = os.path.join(folder, filename)
    save_file(x, y, file_path=path)


def make_results_file(folder):
    timestr = time.strftime("%y%m%d-%H%M%S")
    filename = "result-" + timestr + ".xlsx"
    path = os.path.join(folder, filename)
    return path
