import matplotlib
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import path
from matplotlib import ticker
from PyQt5.QtCore import pyqtSignal
matplotlib.use('Qt5Agg')

class PlotInput():
    finishedDrawing = pyqtSignal(bool)

    def __init__(self, figure:plt.Figure, xlim: list[int, int] = [-5, 5],  ylim: list[int, int] = [-2, 2]) -> None:
    # def __init__(self, xlim: list[int, int] = [-5, 5],  ylim: list[int, int] = [-2, 2]) -> None:
        self.figure = figure
        self.verts = [[xlim[0], 0], [xlim[1], 0]]
        self.codes = [path.Path.MOVETO, path.Path.LINETO]
        
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.xlim = xlim
        self.ylim = ylim
        self.redraw_axes()
        self.fig.canvas.draw()
        
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
    def on_click(self, event) -> None:
        if event.inaxes == self.ax:
            self.redraw_axes()
            print(f"({event.xdata:.2f}, {event.ydata:.2f})")
            print(f"({(float(event.xdata) * 16 + 2)}, {float(event.ydata) * 16 + 2})")
            x, y = (float(event.xdata) * 16 + 2) // 4 / 4, (float(event.ydata) * 16 + 2) // 4 / 4
            print(f"Point added: ({x:.2f}, {y:.2f})")
            self.codes.append(matplotlib.path.Path.LINETO)
            self.verts.append([x, y])
            self.verts =sorted(self.verts, key=lambda p: p[0])
            path_plot = matplotlib.path.Path(self.verts, self.codes)
            patch = patches.PathPatch(path_plot, facecolor='none')
            self.ax.add_patch(patch)
            self.fig.canvas.draw()
    
    def on_key_press(self, event) -> None:
        if event.key == 'enter' or event.key == 'space':
            self.finishedDrawing.emit(True)
            print("Finished collecting points.")
            print(f"Total points collected: {len(self.verts)}")
            return self.get_points()
    
    def get_points(self) -> list[list[int, callable]] | list:
        if len(self.verts) <= 0:
            return []
        return [[self.verts[i][0], \
                    lambda x: (self.verts[i + 1][1] - self.verts[i][1]) / \
                    abs(self.verts[i + 1][0] - self.verts[i][0]) * x + \
                    self.verts[i + 1][1]] for i in range(len(self.verts))]
        
    
    def show(self) -> None:
        plt.show()

    def redraw_axes(self) -> None:
        self.ax.clear()
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(0.25))
        self.ax.set_title("Click on the plot to add points. Press 'enter' to finish.")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(self.xlim[0]-0.1, self.xlim[1]+0.1)
        self.ax.set_ylim(self.ylim[0]-0.1, self.ylim[1]+0.1)

if __name__ == "__main__":
    picker = PlotInput()
    picker.show()
    points_array = picker.get_points()
    
    if len(points_array) > 0:
        print("All collected points with functions of lines from point to point:")
        print(points_array)
    else:
        print("No points were collected.")
