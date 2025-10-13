from __future__ import annotations
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import path
from matplotlib import ticker
from PyQt5.QtCore import pyqtSignal
matplotlib.use('Qt5Agg')
from dataclasses import dataclass
from typing import Callable

def create_functions(x_current, x_next, y_current, y_next) -> Callable[..., float]:
    def _(x) -> float:
        return (y_next - y_current) / abs(x_next - x_current) * x + y_current
    return _


@dataclass
class Segment:
    x0: float
    x1: float
    function: callable
    
    def __add__(self, value: float) -> Segment:
        return Segment(self.x0, self.x1, lambda x: self.function(x) + value)
    def __sub__(self, value: float) -> Segment:
        return Segment(self.x0, self.x1, lambda x: self.function(x) - value)
    def __mul__(self, value: float) -> Segment:
        return Segment(self.x0, self.x1, lambda x: self.function(x) * value)
    def __div__(self, value: float) -> Segment:
        return Segment(self.x0, self.x1, lambda x: self.function(x) / value)
    
    def __add__(self, other: Segment) -> list[Segment]:
        assert self.x0 == other.x0 and self.x1 == other.x1
        return Segment(self.x0, other.x1, lambda x: self.function(x) + other.function(x))
    def __sub__(self, other: Segment) -> list[Segment]:
        assert self.x0 == other.x0 and self.x1 == other.x1
        return Segment(self.x0, self.x1, lambda x: self.function(x) - other)
    def __mul__(self, other: Segment) -> list[Segment]:
        assert self.x0 == other.x0 and self.x1 == other.x1
        return Segment(self.x0, other.x1, lambda x: self.function(x) * other.function(x))
    def __div__(self, other: Segment) -> list[Segment]:
        assert self.x0 == other.x0 and self.x1 == other.x1
        return Segment(self.x0, self.x1, lambda x: self.function(x) / other)
    
    def integrate(self, previous_sum: float) -> Segment:
        return Segment(self.x0, self.x1, lambda x: previous_sum + (x - self.x0) * self.function(self.x0) + 1/2 * (self.function(x)) * (x - self.x0))
    

class Plot:
    def __init__(self, segments: list[Segment]) -> None:
        self.segments = segments

    def __add__(self, value: float) -> Plot:
        return Plot([segment + value for segment in self.segments])
    def __sub__(self, value: float) -> None:
        return Plot([segment - value for segment in self.segments])
    def __mul__(self, value: float) -> Plot:
        return Plot([segment * value for segment in self.segments])
    def __div__(self, value: float) -> None:
        return Plot([segment / value for segment in self.segments])
    
    def __split__(self, other: Plot) -> list[float]:
        all_segments = []
        for segment in self.segments:
            if segment.x0 not in all_segments:
                all_segments.append(segment.x0)
            if segment.x0 not in all_segments:
                all_segments.append(segment.x1)
        for segment in other.segments:
            if segment.x0 not in all_segments:
                all_segments.append(segment.x0)
            if segment.x0 not in all_segments:
                all_segments.append(segment.x1)
        return all_segments
    
    def __add__(self, other: Plot) -> Plot:
        result = []
        all_segments = self.__split__(other)
        for start in  range(len(all_segments) - 1):
            current = Segment(all_segments[start], all_segments[start + 1], lambda x: 0)
            if all_segments[start] >= self.segments[0].x0 and all_segments[start + 1] <= self.segments[-1].x1:
                current += Segment(all_segments[start], all_segments[start + 1], lambda x: self.segments[0].function(x))
            if all_segments[start] >= other.segments[0].x0 and all_segments[start + 1] <= other.segments[-1].x1:
                current += Segment(all_segments[start], all_segments[start + 1], lambda x: other.segments[0].function(x))
            result.append(current)
        return Plot(result)
    def __sub__(self, other: Plot) -> Plot:
        return self + (-1) * other
    def __mul__(self, other: Plot) -> Plot:
        result = []
        all_segments = self.__split__(other)
        for start in  range(len(all_segments) - 1):
            current = Segment(all_segments[start], all_segments[start + 1], lambda x: 1)
            if all_segments[start] >= self.segments[0].x0 and all_segments[start + 1] <= self.segments[-1].x1:
                current *= Segment(all_segments[start], all_segments[start + 1], lambda x: self.segments[0].function(x))
            if all_segments[start] >= other.segments[0].x0 and all_segments[start + 1] <= other.segments[-1].x1:
                current *= Segment(all_segments[start], all_segments[start + 1], lambda x: other.segments[0].function(x))
            result.append(current)
        return Plot(result)
    def __div__(self, other: Plot) -> Plot:
        result = []
        all_segments = self.__split__(other)
        for start in  range(len(all_segments) - 1):
            current = Segment(all_segments[start], all_segments[start + 1], lambda x: 1)
            if all_segments[start] >= self.segments[0].x0 and all_segments[start + 1] <= self.segments[-1].x1:
                current *= Segment(all_segments[start], all_segments[start + 1], lambda x: self.segments[0].function(x))
            if all_segments[start] >= other.segments[0].x0 and all_segments[start + 1] <= other.segments[-1].x1:
                current /= Segment(all_segments[start], all_segments[start + 1], lambda x: other.segments[0].function(x))
            result.append(current)
        return Plot(result)

    def integrate(self) -> Plot:
        result = []
        previous_sum = 0
        for segment in self.segments:
            result.append(segment.integrate(previous_sum))
            previous_sum = result[-1].function(result[-1].x1)
        return Plot(result)



class PlotInput():
    finishedDrawing = pyqtSignal(bool)

    # def __init__(self, figure:plt.Figure, xlim: list[int, int],  ylim: list[int, int] = [-2, 2]) -> None:
    def __init__(self, xlim: list[int, int] = [-5, 5],  ylim: list[int, int] = [-2, 2]) -> None:
        # self.figure = figure
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
            self.verts = sorted(self.verts, key=lambda p: p[0])
            path_plot = matplotlib.path.Path(self.verts, self.codes)
            patch = patches.PathPatch(path_plot, facecolor='none')
            self.ax.add_patch(patch)
            self.fig.canvas.draw()
    
    def on_key_press(self, event) -> None:
        if event.key == 'enter' or event.key == 'space':
            # self.finishedDrawing.emit(True)
            print("Finished collecting points.")
            print(f"Total points collected: {len(self.verts)}")
            return self.get_points()
    
    def get_points(self) -> list[Segment] | list:
        if len(self.verts) <= 0:
            return []
        array =  [Segment(self.verts[i][0], self.verts[i + 1][0],\
                    create_functions(self.verts[i][0], self.verts[i + 1][0], \
                    self.verts[i][1], self.verts[i + 1][1])) for i in range(len(self.verts) - 1) \
                    if self.verts[i][0] != self.verts[i + 1][0]]
        print('functions:')
        print([(element * 2).function(1) for element in array])
        print('x0:')
        print([element.x0 for element in array])
        print('x1:')
        print([element.x1 for element in array])
        
    
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
