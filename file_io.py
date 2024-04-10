import pandas as pd
import time


dark_folder = "../data/dark"
ref_folder = "../data/ref"


def save_file(x, y, file_path):
    df = pd.DataFrame({"wavelength": x, "intensity": y})
    df.to_csv(file_path)


def load_file(file_path):
    df = pd.read_csv(file_path)
    x, y = df["wavelength"].values, df["intensity"].values
    return x, y


def save_dark_file(x, y):
    timestr = time.strftime("%y%m%d-%H%M%S")
    path = dark_folder + "dark-" + timestr + ".csv"
    save_file(x, y, file_path=path)


def save_ref_file(x, y):
    timestr = time.strftime("%y%m%d-%H%M%S")
    path = ref_folder + "ref-" + timestr + ".csv"
    save_file(x, y, file_path=path)
