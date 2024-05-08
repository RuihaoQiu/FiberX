import matplotlib.pyplot as plt
import numpy as np


def on_scroll(event):
    ax = event.inaxes
    if ax is None:
        return

    xdata, ydata = event.xdata, event.ydata  # Mouse position in data coords
    if xdata is None or ydata is None:
        return  # Ignore scroll events outside the axes

    base_scale = 1.1  # Determines the zoom speed
    if event.button == "up":
        # Zoom in
        scale_factor = 1 / base_scale
    elif event.button == "down":
        # Zoom out
        scale_factor = base_scale
    else:
        # Unhandled button
        return

    # Set new limits
    ax.set_xlim(
        [
            xdata - (xdata - ax.get_xlim()[0]) * scale_factor,
            xdata + (ax.get_xlim()[1] - xdata) * scale_factor,
        ]
    )
    ax.set_ylim(
        [
            ydata - (ydata - ax.get_ylim()[0]) * scale_factor,
            ydata + (ax.get_ylim()[1] - ydata) * scale_factor,
        ]
    )
    plt.draw()  # Redraw the current figure


fig, ax = plt.subplots()
x = np.linspace(0, 10, 400)
y = np.sin(x)
ax.plot(x, y, label="Sine wave")
ax.legend()

# Connect the scroll event to the zoom handler
fig.canvas.mpl_connect("scroll_event", on_scroll)

plt.show()
