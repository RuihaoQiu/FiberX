import tkinter as tk
from tkinter import ttk, filedialog
import os


class TabbedWidgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabbed Widget")

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # First tab: List files from the folder
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="List Files")

        # Listbox to display filenames
        self.file_listbox = tk.Listbox(
            self.tab1, selectmode="multiple", width=50, height=10
        )
        self.file_listbox.pack(pady=10)

        # Button to plot selected files
        self.plot_button = ttk.Button(
            self.tab1, text="Plot", command=self.plot_selected_files
        )
        self.plot_button.pack()

        # Load files button
        self.load_button = ttk.Button(
            self.tab1, text="Load Files", command=self.load_files
        )
        self.load_button.pack()

    def load_files(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.file_listbox.delete(0, tk.END)
            files = os.listdir(folder_path)
            for file in files:
                self.file_listbox.insert(tk.END, file)

    def plot_selected_files(self):
        selected_files = [
            self.file_listbox.get(idx) for idx in self.file_listbox.curselection()
        ]
        print("Selected files:", selected_files)


def main():
    root = tk.Tk()
    app = TabbedWidgetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
