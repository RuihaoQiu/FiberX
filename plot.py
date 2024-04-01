import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def plot_xy(x_values, y_values):
    # Create a tkinter window
    root = tk.Tk()
    root.title("X-Y Plot")

    # Create a figure and plot
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker="o", linestyle="-")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("X-Y Plot")

    # Embed the matplotlib plot into tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Start tkinter event loop
    root.mainloop()


# Example usage
x_values = [1, 2, 3, 4, 5]
y_values = [2, 3, 5, 7, 11]
plot_xy(x_values, y_values)
