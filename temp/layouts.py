import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from tabs import create_tab_ration
from intensity import create_tab_intensity
from file_io import load_file

import matplotlib.pyplot as plt


class FiberXApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FiberX")

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # First tab: Load data and plot
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="光谱")

        # Create a frame to contain the plot
        self.plot_frame = tk.Frame(self.tab1)
        self.plot_frame.pack()

        plt.style.use("ggplot")

        self.fig, self.ax = plt.subplots()
        # Set x and y labels
        self.ax.set_xlabel("Wavelength")
        self.ax.set_ylabel("Ration")

        plt.subplots_adjust(
            top=0.925, bottom=0.16, left=0.11, right=0.90, hspace=0.2, wspace=0.2
        )

        file_path = "../data/dark-240404-115932.csv"
        self.x, self.y = load_file(file_path)
        # Initialize variables
        (self.dot_line,) = self.ax.plot(self.x, self.y, "-", label="data")

        # Create a button to load data
        self.load_button = tk.Button(
            self.tab1,
            text="Load Data",
            command=self.update_plot,
        )
        self.load_button.pack(side=tk.LEFT)

    def update_plot(self):

        # ax.plot(self.x, self.y, marker=".", linestyle="-")

        self.dot_line.set_data(self.x, self.y)
        self.ax.relim()
        self.ax.autoscale_view()

        self.ax.set_xlabel("Wave Length")
        self.ax.set_ylabel("Intensity")

        canvas = FigureCanvasTkAgg(self.fig, master=self.tab1)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=(20, 10), font=(14))
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = FiberXApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
