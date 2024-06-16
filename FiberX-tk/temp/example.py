import tkinter as tk
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
from tkinter import ttk


def plot_selected_file(var):
    selected_file = var.get()  # Get the selected filename
    if selected_file:  # Check if a file is selected
        # Load data from the selected file (you need to implement this)
        # Example:
        x, y = load_data(selected_file)

        # Plot the data
        plt.plot(x, y)
        plt.xlabel("X Label")
        plt.ylabel("Y Label")
        plt.title(selected_file)
        plt.show()


def load_data(selected_file):
    # Dummy function to simulate loading data from a file
    # Replace this with your actual data loading code
    # Here, we just return some sample data
    return [1, 2, 3, 4], [1, 4, 9, 16]


def browse_files():
    directory = filedialog.askdirectory()
    if directory:
        # Get all filenames in the selected directory
        filenames = os.listdir(directory)

        # Clear the existing Checkbuttons and var_list
        for widget in frame.winfo_children():
            widget.destroy()
        var_list.clear()

        # Create a Checkbutton for each filename
        for filename in filenames:
            var = tk.StringVar()
            var_list.append(var)
            checkbox = tk.Checkbutton(
                frame, text=filename, variable=var, onvalue=filename
            )
            checkbox.config(command=lambda var=var: plot_selected_file(var))
            checkbox.pack(anchor=tk.W)


# Function to handle deselection of check boxes
def handle_deselect(var):
    # Unset the value of the variable
    var.set("")


# Create a Tkinter window
window = tk.Tk()
window.title("File Selection and Plotting")

# Create a list to store the selected filenames
var_list = []

# Create a notebook
notebook = ttk.Notebook(window)
notebook.pack(fill=tk.BOTH, expand=True)

# Create a frame for the first tab
tab1_frame = tk.Frame(notebook)
notebook.add(tab1_frame, text="Tab 1")

# Create a frame to hold the list of filenames
frame = tk.Frame(tab1_frame)
frame.pack(side=tk.LEFT)

# Create a button frame
button_frame = tk.Frame(window)
button_frame.pack(side=tk.LEFT, padx=10)

# Create a button to browse files
browse_button = tk.Button(button_frame, text="Browse Directory", command=browse_files)
browse_button.pack(pady=5)

# Bind the handle_deselect function to all variables in var_list
for var in var_list:
    var.trace_add("write", lambda *args, var=var: handle_deselect(var))

window.mainloop()
