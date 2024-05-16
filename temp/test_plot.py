import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        # Set up a grid and configure the column/row in the container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a canvas and a scrollbar inside this frame
        self.canvas = tk.Canvas(self, bg="lightgrey")
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Create a frame inside the canvas to hold the checkboxes
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Configure the scroll region to update on inner frame configuration changes
        self.inner_frame.bind("<Configure>", self.on_frame_configure)

        # Bind mouse wheel event for scrolling
        self.bind("<Enter>", self._bind_mousewheel)
        self.bind("<Leave>", self._unbind_mousewheel)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mousewheel(self, event):
        """Bind the mousewheel scroll to the frame"""
        self.bind_all("<MouseWheel>", self.on_mousewheel)  # Windows and OS X
        self.bind_all("<Button-4>", self.on_mousewheel)  # Linux (wheel up)
        self.bind_all("<Button-5>", self.on_mousehole)  # Linux (wheel down)

    def _unbind_mousewheel(self, event):
        """Unbind the mousewheel scroll"""
        self.unbind_all("<MouseWheel>")  # Windows and OS X
        self.unbind_all("<Button-4>")  # Linux (wheel up)
        self.unbind_all("<Button-5>")  # Linux (wheel down)

    def on_mousewheel(self, event):
        """Mouse wheel handler"""
        if event.num == 4:  # Linux wheel up
            delta = -1
        elif event.num == 5:  # Linux wheel down
            delta = 1
        else:
            delta = -1 * event.delta // 120  # Convert from MS units to common value

        self.canvas.yview_scroll(delta, "units")


def main():
    root = tk.Tk()
    root.title("Scrollable Frame with Checkboxes")
    root.geometry("300x400")

    scrollable_frame = ScrollableFrame(root)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Adding checkboxes to the inner frame
    for i in range(50):  # Generate 50 checkboxes as an example
        var = tk.BooleanVar(value=False)
        checkbox = ttk.Checkbutton(
            scrollable_frame.inner_frame, text=f"Option {i + 1}", variable=var
        )
        checkbox.pack(anchor="w", padx=5, pady=2)

    root.mainloop()


if __name__ == "__main__":
    main()
