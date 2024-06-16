import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PlotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resizable Plot")

        # Create a frame for the plot
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

        # Create a figure and axes for the plot
        self.fig, self.ax = plt.subplots()
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize data
        self.x = np.linspace(0, 10, 100)
        self.y = np.sin(self.x)

        # Plot initial data
        self.plot_data()

        # Bind the <Configure> event to a callback function
        self.bind("<Configure>", self.on_window_resize)

    def plot_data(self):
        self.ax.clear()
        self.ax.plot(self.x, self.y)
        self.plot_canvas.draw()

    def on_window_resize(self, event):
        # Get the new size of the window
        width = self.winfo_width()
        height = self.winfo_height()
        print(width, height)

        # Update the plot size
        self.fig.set_size_inches(
            width / self.plot_canvas.figure.dpi, height / self.plot_canvas.figure.dpi
        )

        # Update the font size
        font_size = min(width, height) // 50
        for item in (
            [self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label]
            + self.ax.get_xticklabels()
            + self.ax.get_yticklabels()
        ):
            item.set_fontsize(font_size)

        # Redraw the plot
        self.plot_canvas.draw()


if __name__ == "__main__":
    app = PlotApp()
    app.mainloop()
