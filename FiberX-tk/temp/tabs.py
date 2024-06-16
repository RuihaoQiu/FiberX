# from tkinter import ttk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt


# def create_tab_ration(parent, x_values, y_values):
#     tab = ttk.Frame(parent)
#     parent.add(tab, text="吸收")

#     fig, ax = plt.subplots()
#     ax.plot(x_values, y_values, marker=".", linestyle="-")
#     ax.set_xlabel("Wave Length")
#     ax.set_ylabel("Ration")

#     canvas = FigureCanvasTkAgg(fig, master=tab)
#     canvas.draw()
#     canvas.get_tk_widget().pack(fill="both", expand=True)

#     window_size = (1280, 960)
#     tab.winfo_toplevel().geometry(f"{window_size[0]}x{window_size[1]}")


import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd


class DataPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # First tab: Load data and plot
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Load Data")

        # Create a frame to contain the plot
        self.plot_frame = tk.Frame(self.tab1)
        self.plot_frame.pack()

        # Create a button to load data
        self.load_button = tk.Button(
            self.tab1, text="Load Data", command=self.load_data
        )
        self.load_button.pack()

        # Initialize variables
        self.data = None

        # Second tab: Other functionality
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Other Functionality")

        # Create a button for other functionality
        self.other_button = tk.Button(self.tab2, text="Other Button")
        self.other_button.pack()

    def load_data(self):
        # Open file dialog to select data file
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            # Read data from CSV file
            self.data = pd.read_csv(file_path)

            # Plot the data
            self.plot_data()

    def plot_data(self):
        # Clear any existing plots
        plt.close("all")

        # Create a new plot
        self.fig, self.ax = plt.subplots()
        self.ax.plot(self.data["X"], self.data["Y"], marker="o", linestyle="-")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_title("Data Plot")

        # Embed the plot in the Tkinter GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()


def main():
    root = tk.Tk()
    app = DataPlotterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
