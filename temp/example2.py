import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def plot_data():
    # Example data
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]

    # Clear existing plot
    ax.clear()

    # Plot new data
    ax.plot(x, y)
    ax.set_xlabel("X Label")
    ax.set_ylabel("Y Label")
    ax.set_title("Plot Title")

    # Update canvas
    canvas.draw()


# Create the main window
root = tk.Tk()
root.title("Notebook with Fixed Frame Ratio")

# Create a Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create frames for the tabs
tab1_frame = ttk.Frame(notebook)
tab2_frame = ttk.Frame(notebook)

# Add frames to the notebook
notebook.add(tab1_frame, text="Tab 1")
notebook.add(tab2_frame, text="Tab 2")

# Set fixed ratio for each frame
notebook.rowconfigure(0, weight=1)  # Ratio 1
notebook.rowconfigure(1, weight=3)  # Ratio 3

# Add buttons to the first frame in the first tab
button1 = ttk.Button(tab1_frame, text="Button 1")
button1.grid(row=0, column=0, padx=10, pady=10)
button2 = ttk.Button(tab1_frame, text="Button 2")
button2.grid(row=1, column=0, padx=10, pady=10)

# Create a Figure and Axes for plotting
fig, ax = plt.subplots()
ax.plot([], [])  # Empty plot for initialization

# Create a canvas to display the plot
canvas = FigureCanvasTkAgg(fig, master=tab1_frame)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

# Add a button to plot data
plot_button = ttk.Button(tab1_frame, text="Plot Data", command=plot_data)
plot_button.grid(row=2, column=1, padx=10, pady=10)

root.mainloop()
