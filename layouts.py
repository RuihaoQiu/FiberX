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

        # Create a button to load data
        self.load_button = tk.Button(
            self.tab1,
            text="Load Data",
            command=self.load_data,
        )
        self.load_button.pack()

        # Initialize variables
        self.x = []
        self.y = []
        self.fig, self.ax = plt.subplots()
        (self.dot_line,) = self.ax.plot([], [], "-", label="data")

    def load_data(self):
        # Open file dialog to select data file
        file_path = "../data/dark-240404-115932.csv"
        self.x, self.y = load_file(file_path)

        # Plot the data
        self.update_plot()

    def update_plot(self):

        # ax.plot(self.x, self.y, marker=".", linestyle="-")

        self.dot_line.set_data(self.x, self.y)
        self.ax.relim()
        self.ax.autoscale_view()
        # ax.plot(x_wavelength, y_ref, marker=".", linestyle="-")
        # ax.plot(x_wavelength, y_realtime, marker=".", linestyle="-")
        self.ax.set_xlabel("Wave Length")
        self.ax.set_ylabel("Intensity")

        canvas = FigureCanvasTkAgg(self.fig, master=self.tab1)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=(20, 10), font=(14))
        self.root.mainloop()


# def main():
#     root = tk.Tk()
#     root.title("FiberX")

#     # Sample data
#     x_values = [1, 2, 3, 4, 5]
#     y_values = [2, 3, 5, 7, 11]
#     y_dark = [2, 3, 5, 7, 11]
#     y_ref = [12, 13, 15, 17, 21]
#     y_real = [7, 8, 10, 12, 16]

#     # Create a Notebook widget
#     notebook = ttk.Notebook(root)
#     notebook.pack(fill="both", expand=True, padx=20, pady=20)

#     # Create tabs with plots
#     create_tab_intensity(notebook, x_values, y_dark, y_ref, y_real)
#     create_tab_ration(notebook, x_values, [y + 1 for y in y_values])

#     style = ttk.Style()
#     style.configure("TNotebook.Tab", padding=(20, 10), font=(14))
#     root.mainloop()


def main():
    root = tk.Tk()
    app = FiberXApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
