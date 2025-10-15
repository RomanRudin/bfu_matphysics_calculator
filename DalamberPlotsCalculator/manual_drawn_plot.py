from __future__ import annotations
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import path
from matplotlib import ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtCore import pyqtSignal, QObject, Qt
matplotlib.use('Qt5Agg')
from dataclasses import dataclass
from typing import Callable

def create_functions(x_current, x_next, y_current, y_next) -> Callable[..., float]:
    def _(x) -> float:
        # print(x_current, x_next, y_current, y_next, ((y_next - y_current) / abs(x_next - x_current)), ((y_next - y_current) / abs(x_next - x_current)) + y_current, )
        return ((y_next - y_current) / abs(x_next - x_current)) * (x - x_current) + y_current
    return _


@dataclass
class Segment:
    x0: float
    x1: float
    function: Callable
    
    def __add__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, other.x1, lambda x: self(x) + other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) + other)
    def __sub__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, self.x1, lambda x: self(x) - other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) - other)
    def __mul__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, other.x1, lambda x: self(x) * other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) * other)
    def __div__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, self.x1, lambda x: self(x) / other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) / other)
    def __radd__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other + self
        return Segment(self.x0, self.x1, lambda x: self(x) + other)
    def __rsub__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other - self
        return Segment(self.x0, self.x1, lambda x: other - self(x))
    def __rmul__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other * self
        return Segment(self.x0, self.x1, lambda x: self(x) * other)
    def __rdiv__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other / self
        return Segment(self.x0, self.x1, lambda x: other / self(x))
    
    def integrate(self, previous_sum: float) -> Plot:
        result = []
        sums = [previous_sum]
        if self.x0 < 0:
            if self.x1 <= 0:
                result.append(Segment(self.x0, self.x1, lambda x: sums[0] - 1/2 * (self(x)) * (x - self.x0)))
                sums.append(sums[0] - (self.x1 - self.x0) * self(self.x0) - 1/2 * (self(self.x1)) * (self.x1 - self.x0))
            else:
                result.append(Segment(self.x0, 0, lambda x: sums[0] - 1/2 * (self(x)) * (x - self.x0)))
                sums.append(sums[0] - 1/2 * (self(0)) * (0 - self.x0))
                result.append(Segment(0, self.x1, lambda x: sums[1] + 1/2 * (self(x)) * (x - 0)))
                sums.append(sums[1] + 1/2 * (self(self.x1)) * (self.x1 - 0))
        else:
            result.append(Segment(self.x0, self.x1, lambda x: sums[0] + 1/2 * (self(x)) * (x - self.x0)))
            sums.append(sums[0] + 1/2 * (self(self.x1)) * (self.x1 - self.x0))
        return Plot(result), sums[-1]
    
    def __call__(self, x: float) -> float:
        return self.function(x)
    def __str__(self) -> str:
        return f"Segment(start = {self.x0}, end = {self.x1}, function({self.x0}) = {self(self.x0)}, function({self.x1}) = {self(self.x1)})"''
    

class Plot:
    def __init__(self, segments: list[Segment]) -> None:
        self.segments = segments

    def __add__(self, other: float | Plot) -> Plot:
        if type(other) == Plot:
            if not self.segments: return other
            if not other.segments: return self
            result = []
            all_segments = self.__split__(other)
            print(all_segments, self.segments[0], other.segments[-1])
            for i in range(len(all_segments) - 1):
                current = Segment(all_segments[i], all_segments[i + 1], lambda x: 0)
                if all_segments[i] >= self.segments[0].x0 and all_segments[i + 1] <= self.segments[-1].x1:
                    current += Segment(all_segments[i], all_segments[i + 1], lambda x: self(x))
                if all_segments[i] >= other.segments[0].x0 and all_segments[i + 1] <= other.segments[-1].x1:
                    current += Segment(all_segments[i], all_segments[i + 1], lambda x: other(x))
                result.append(current)
            return Plot(result)
        return Plot([segment + other for segment in self.segments])
    def __sub__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return self + other * (-1)
        return Plot([segment - other for segment in self.segments])
    def __mul__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            result = []
            all_segments = self.__split__(other)
            for i in  range(len(all_segments) - 1):
                current = Segment(all_segments[i], all_segments[i + 1], lambda x: 1)
                if all_segments[i] >= self.segments[0].x0 and all_segments[i + 1] <= self.segments[-1].x1:
                    current *= Segment(all_segments[i], all_segments[i + 1], lambda x: self(x))
                if all_segments[i] >= other.segments[0].x0 and all_segments[i + 1] <= other.segments[-1].x1:
                    current *= Segment(all_segments[i], all_segments[i + 1], lambda x: other(x))
                result.append(current)
            return Plot(result)
        return Plot([segment * other for segment in self.segments])
    def __div__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            result = []
            all_segments = self.__split__(other)
            for i in  range(len(all_segments) - 1):
                current = Segment(all_segments[i], all_segments[i + 1], lambda x: 1)
                if all_segments[i] >= self.segments[0].x0 and all_segments[i + 1] <= self.segments[-1].x1:
                    current *= Segment(all_segments[i], all_segments[i + 1], lambda x: self(x))
                if all_segments[i] >= other.segments[0].x0 and all_segments[i + 1] <= other.segments[-1].x1:
                    current /= Segment(all_segments[i], all_segments[i + 1], lambda x: other(x))
                result.append(current)
            return Plot(result)
        return Plot([segment / other for segment in self.segments])
    def __radd__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: \
            return other + self
        return Plot([segment + other for segment in self.segments])
    def __rsub__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return other - self
        return Plot([segment - other for segment in self.segments])
    def __rmul__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return other * self
        return Plot([segment * other for segment in self.segments])
    def __rdiv__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return other / self
        return Plot([segment / other for segment in self.segments])
    
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

    def integrate(self) -> Plot:
        result = []
        previous_sum = 0
        for segment in self.segments:
            integrated, previous_sum = segment.integrate(previous_sum)
            for segment in integrated.segments:
                result.append(segment)
        return Plot(result)
    
    def __call__(self, x: float) -> float:
        if not self.segments: return 0
        if x < self.segments[0].x0 or x > self.segments[-1].x1: return 0
        i = 0
        while not self.segments[i].x0 <= x <= self.segments[i].x1: i += 1
        # print(i, x, self.segments[i])
        return self.segments[i](x)

    def shift(self, shift_amount: float) -> Plot:
        new_segments = []
        for segment in self.segments:
            new_segment = Segment(
                segment.x0 + shift_amount,
                segment.x1 + shift_amount,
                lambda x, seg=segment, shift=shift_amount: seg(x - shift)
            )
            new_segments.append(new_segment)
        return Plot(new_segments)
    def __str__(self) -> str:
        return f"Plot(length = {len(self.segments)},\n{'\n'.join(str(segment) for segment in self.segments)}\n)"
    def __len__(self) -> Plot:
        return self.segments[-1].x1 - self.segments[0].x0


# class MovedPlot: TODO
#     def __init__(self, plot: Plot, t: float) -> None:
#         self.plot = plot
#         self.move = move


class PlotInput(QObject):
    finishedDrawing = pyqtSignal(bool)

    def __init__(self, figure:plt.Figure, canvas: FigureCanvasQTAgg, xlim: list[int, int],  ylim: list[int, int] = [-2, 2]) -> None:
    # def __init__(self, xlim: list[int, int] = [-5, 5],  ylim: list[int, int] = [-2, 2]) -> None:
        super().__init__()
        self.figure = figure
        self.verts = [[xlim[0], 0], [xlim[1], 0]]
        self.codes = [path.Path.MOVETO, path.Path.LINETO]
        self.canvas = canvas
        
        self.ax = self.figure.add_subplot(111)
        self.xlim = xlim
        self.ylim = ylim
        self.redraw_axes()

        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        
    def on_click(self, event) -> None:
        if event.inaxes == self.ax:
            self.redraw_axes()
            # print(f"({event.xdata:.2f}, {event.ydata:.2f})")
            # print(f"({(float(event.xdata) * 16 + 2)}, {float(event.ydata) * 16 + 2})")
            x, y = (float(event.xdata) * 16 + 2) // 4 / 4, (float(event.ydata) * 16 + 2) // 4 / 4
            # print(f"Point added: ({x:.2f}, {y:.2f})")
            self.codes.append(matplotlib.path.Path.LINETO)
            self.verts.append([x, y])
            self.verts = sorted(self.verts, key=lambda p: p[0])
            self.refresh()
            self.canvas.setFocus()
        
    def refresh(self) -> None:
        self.redraw_axes()
        path_plot = matplotlib.path.Path(self.verts, self.codes)
        patch = patches.PathPatch(path_plot, facecolor='none')
        self.ax.add_patch(patch)
        self.canvas.draw()
    
    def on_key_press(self, event) -> None:
        if event.key in ['enter', ' ']:
            self.finishedDrawing.emit(True)
            # print("Finished collecting points.")
            # print(f"Total points collected: {len(self.verts)}")
            return self.get_plot()
        if event.key == 'backspace':
            if len(self.verts) <= 2: return
            self.verts.pop(-2)
            self.codes.pop(-2)
            self.refresh()
            return
    
    def get_plot(self) -> list[Segment] | list:
        if len(self.verts) <= 0:
            return []
        array =  Plot([Segment(self.verts[i][0], self.verts[i + 1][0],\
                    create_functions(self.verts[i][0], self.verts[i + 1][0], \
                    self.verts[i][1], self.verts[i + 1][1])) for i in range(len(self.verts) - 1) \
                    if self.verts[i][0] != self.verts[i + 1][0]])
        return array
        # print('functions:')
        # print([(element * 2).function(1) for element in array])
        # print('x0:')
        # print([element.x0 for element in array])
        # print('x1:')
        # print([element.x1 for element in array])
        
    
    def show(self) -> None:
        plt.show()

    def redraw_axes(self) -> None:
        self.ax.clear()
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
        self.ax.set_title("Click on the plot to add points. Press 'enter' to finish.")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True, alpha=0.2)
        self.ax.set_xlim(self.xlim[0]-0.1, self.xlim[1]+0.1)
        self.ax.set_ylim(self.ylim[0]-0.1, self.ylim[1]+0.1)

# if __name__ == "__main__":
    # picker = PlotInput()
    # picker.show()
    # points_array = picker.get_points()
    # 
    # if len(points_array) > 0:
        # print("All collected points with functions of lines from point to point:")
        # print(points_array)
    # else:
        # print("No points were collected.")
