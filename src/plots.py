from __future__ import annotations
import matplotlib.pyplot as plt
from typing import Optional
from matplotlib import ticker
from matplotlib import patches
from matplotlib import path
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from src.datastructures import Plot, Range, Segment
from typing import Callable, List
import numpy as np
# matplotlib.use('Qt5Agg')


def create_functions(x_current, x_next, y_current, y_next) -> Callable[..., float]:
    def _(x) -> float:
        return ((y_next - y_current) / abs(x_next - x_current)) * (x - x_current) + y_current
    return _




class DynamicPlot():
    def __init__(self, ax, plot: Plot, color: str = 'black') -> None:
        self.x = np.arange(0, 1)
        self.y = np.arange(0, 1)
        self.color = color
        self.plot = plot
        self.line, = ax.plot(self.x, self.y, color=self.color)

    def refresh(self, range: Range, a: Optional[float] = None, t: Optional[float] = None) -> Optional[Plot]:
        self.x = np.linspace(range.x0, range.x1, num=int(100 * range.x_length()))
        if t is not None and t != 0:
            shifted_plot = self.plot.shift(a * t)
            self.y = np.array([shifted_plot(x) for x in self.x])
        else:
            self.y = np.array([self.plot(x) for x in self.x])
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
        if t is not None and t != 0:
            return shifted_plot
        return self.plot
    
    @property
    def x(self) -> np.ndarray:
        return self._x
    @x.setter
    def x(self, x: np.ndarray) -> None:
        self._x = x
    @property
    def y(self) -> np.ndarray:
        return self._y
    @y.setter
    def y(self, y: np.ndarray) -> None:
        self._y = y

    def get_plot(self) -> Plot:
        return self.plot




class PlotInput(QObject):
    finishedDrawing = pyqtSignal(bool)

    def __init__(self, figure:plt.Figure, canvas: FigureCanvasQTAgg, range: Range, initial_plot: Plot=None) -> None:
    # def __init__(self, xlim: list[int, int] = [-5, 5],  ylim: list[int, int] = [-2, 2]) -> None:
        super().__init__()
        self.figure = figure
        self.isEnabled = True
        self.verts = [[range.x0, 0], [range.x1, 0]]
        self.codes = [path.Path.MOVETO, path.Path.LINETO]
        self.canvas = canvas
        
        self.ax = self.figure.add_subplot(111)
        self.range = range
        self.redraw_axes()
        if initial_plot is not None:
            self.initial_draw(initial_plot)

        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)

    def setEnabled(self, enabled: bool) -> None:
        self.isEnabled = enabled
        if not enabled:
            self.ax.set_facecolor('gray')
        else:
            self.ax.set_facecolor('white')

    def initial_draw(self, plot: Plot) -> None:
        self.verts = [[self.range.x0, 0]] + [[segment.x1, segment(segment.x1)] for segment in plot.segments] + [[self.range.x1, 0]]
        self.codes = [path.Path.MOVETO, path.Path.LINETO] + [path.Path.LINETO] * len(plot.segments)
        self.refresh()

        
    def on_click(self, event) -> None:
        if event.inaxes == self.ax and self.isEnabled:
            self.redraw_axes()
            x, y = (float(event.xdata) * 4 + 1) // 2 / 2, (float(event.ydata) * 4 + 1) // 2 / 2
            self.codes.append(path.Path.LINETO)
            self.verts.append([x, y])
            self.verts = sorted(self.verts, key=lambda p: p[0])
            self.refresh()
            self.canvas.setFocus()

        
    def refresh(self) -> None:
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.redraw_axes()
        path_plot = path.Path(self.verts, self.codes)
        patch = patches.PathPatch(path_plot, facecolor='none')
        self.ax.add_patch(patch)
        self.canvas.draw()

    
    def on_key_press(self, event) -> None:
        if event.key in ['enter', ' '] and self.isEnabled:
            self.finishedDrawing.emit(True)
            return self.get_plot()
        if event.key == 'backspace' and self.isEnabled:
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
        
    
    def show(self) -> None:
        plt.show()


    def redraw_axes(self) -> None:
        self.ax.clear()
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.set_title("Click on the plot to add points. Press 'enter' to finish.")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True, alpha=0.2)
        self.ax.set_xlim(self.range.x0-0.1, self.range.x1+0.1)
        self.ax.set_ylim(self.range.y0-0.1, self.range.y1+0.1)

    


class SinglePlot:
    def __init__(self, figure: plt.Figure, canvas: FigureCanvasQTAgg, main_plot: Plot, 
                 range: Range, title: str, function: Optional[Callable[[Plot], Plot]] = None,
                 colors: List[str] = ['blue', 'red']) -> None:
        self.figure = figure
        self.canvas = canvas
        self.main_plot = main_plot
        self.function = function
        self.colors = colors
        self.dynamic_plots = []
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(range.x0-0.1, range.x1+0.1)
        self.ax.set_ylim(range.y0-0.1, range.y1+0.1)
        self.ax.grid(True, alpha=0.2)
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.set_title(title)
        self.plot = DynamicPlot(self.ax, main_plot, color=self.colors[0])
        if self.function is not None:
            self.plot2 = DynamicPlot(self.ax, self.function(main_plot), color=self.colors[1])
            self.plot2.refresh(range)
        self.plot.refresh(range)
        self.canvas.draw()
    
    def get_plots(self) -> list[Plot]:
        if self.function is None:
            return [self.plot.get_plot()]
        return [self.plot.get_plot(), self.plot2.get_plot()]


class WavePlot:
    def __init__(self, figure: plt.Figure, canvas: FigureCanvasQTAgg, main_plot: Plot, title: str, 
                 function: Callable[[Plot, Plot, float], Plot],
                 colors: List[str] = ['blue', 'red', 'green']) -> None:
        self.figure = figure
        self.canvas = canvas
        self.main_plot = main_plot
        self.function = function
        self.colors = colors
        self.dynamic_plots = []
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(title)

        # Plot 1: g(x - at)
        self.plot1 = DynamicPlot(self.ax, main_plot, color=self.colors[0])
        
        # Plot 2: g(x + at)
        self.plot2 = DynamicPlot(self.ax, main_plot, color=self.colors[1])
        
        # Plot 3: function(g(x-at), g(x+at))
        combined_plot = self.function(main_plot, main_plot, 1)
        self.plot3 = DynamicPlot(self.ax, combined_plot, color=self.colors[2])

        self.canvas.draw()
    
    def refresh(self, a: float, t: float, range: Range) -> None:
        if self.plot2.plot.start > (range.x0 - a * t):
            self.plot2.plot = self.plot2.plot.extend(2 * a * t)
        if self.plot1.plot.end < (range.x1 + a * t):
            self.plot1.plot = self.plot1.plot.extend(2 * a * t)
        self.ax.set_xlim(range.x0-0.1, range.x1+0.1)
        self.ax.set_ylim(range.y0-0.1, range.y1+0.1)
        self.ax.grid(True, alpha=0.2)
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        plot_plus = self.plot1.refresh(range, a=a, t=t)
        plot_minus = self.plot2.refresh(range, a=a, t=-t)
        self.plot3.line.remove()
        combined_plot = self.function(plot_plus, plot_minus, a)
        self.plot3 = DynamicPlot(self.ax, combined_plot, color=self.colors[2])
        self.plot3.refresh(range)
        self.canvas.draw()

    def get_plots(self) -> list[Plot]:
        return [self.plot1.get_plot(), self.plot2.get_plot(), self.plot3.get_plot()]
    


class ResultPlot:
    def __init__(self, figure: plt.Figure, canvas: FigureCanvasQTAgg, plot1: Plot, plot2: Plot, range: Range, title: str, 
                 function: Callable[[Plot, Plot], Plot] | Callable[[Plot, Plot, Plot], Plot], plot3: Optional[Plot] = None,
                 colors: List[str] = ['blue', 'red', 'green']) -> None:
        self.figure = figure
        self.canvas = canvas
        self.plot1 = plot1
        self.plot2 = plot2
        self.plot3_exists = plot3 is not None
        self.function = function
        self.colors = colors
        self.dynamic_plots = []
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(range.x0-0.1, range.x1+0.1)
        self.ax.set_ylim(range.y0-0.1, range.y1+0.1)
        self.ax.grid(True, alpha=0.2)
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.set_title(title)

        self.plot1 = DynamicPlot(self.ax, plot1, color=self.colors[0])
        self.plot1.refresh(range)
        self.plot2 = DynamicPlot(self.ax, plot2, color=self.colors[1])
        self.plot2.refresh(range)
        if self.plot3_exists:
            self.plot3 = DynamicPlot(self.ax, plot3, color=self.colors[3])
            self.plot3.refresh(range)
            combined_plot = self.function(plot1, plot2, plot3)
        else:
            combined_plot = self.function(plot1, plot2)
        self.plot_result = DynamicPlot(self.ax, combined_plot, color=self.colors[2])
        self.plot_result.refresh(range)

        self.canvas.draw()

    def get_plots(self) -> list[Plot]:
        if self.plot3_exists:
            return [self.plot1.get_plot(), self.plot2.get_plot(), self.plot3.get_plot(), self.plot_result.get_plot()]
        return [self.plot1.get_plot(), self.plot2.get_plot(), self.plot_result.get_plot()]


# class ThreeDynamicPlots():
#     def __init__(self, figure:plt.Figure, plots: dict['plots': list[Plot], 'dependancy': Optional[list[callable]]], range: Range, colors: list[str], a: float = 1) -> None:
#         # super().__init__(figure, place, spec)
#         self.figure = figure
#         self.plots = []
#         self.colors = colors
#         self.plots_data = plots
#         self.range = range
#         self.refresh(a, 0)

        
#         # Update the line with the new x and y values
#     def init_update(self, functions, dependancies: dict[int: list[list[int], list[callable]]], colors, max_t, a) -> None:
#         self.dependent.clear()
#         self.x_range = [min(function[0][0] for function in functions) - a * max_t, \
#                     max(function[-1][0] for function in functions) + a * max_t]
#         self.y_range = [min(min(function[i][1](function[i][0]), function[i][1](function[(i + 1) % len(function)][0])) \
#                             for i in range(len(function)) for function in functions) * 2, \
#                         max(max(function[i][1](function[i][0]), function[i][1](function[(i + 1) % len(function)][0])) \
#                             for i in range(len(function)) for function in functions) * 2]
#         for index, function in enumerate(functions): 
#             self.dependent.append(DynamicPlot(function, color=colors[index], depending_on=self.dependent[dependancies[index][0]], arythmetic_operators=dependancies[index][1])\
#                                 if dependancies else \
#                                 DynamicPlot(function, color=colors[index]))
#         self.update(0)

#     def refresh(self, a, t) -> None:
#         self.plots.clear()
#         for plots, dependancy in self.plots_data.values():
#             self.plots.add.update(a, t, self.x_range)
#         plt.axis(self.range.x0, self.range.x1, self.range.y0, self.range.y1)
#         self.figure.canvas.draw_idle()
    
#     @property
#     def x_range(self) -> list[float, float]:
#         return self.x_range
#     @property
#     def y_range(self) -> list[float, float]:
#         return self.y_range



# class ThreePlotsFinal(DynamicPlot):
#     def __init__(self, figure:plt.Figure, colors:list[str], place:int, spec:gridspec.GridSpec, dependancies: dict[int: list[list[ThreeDynamicPlots], list[callable]]] =[], a: float = 1, max_t: float = 5) -> None:
#         # super().__init__(figure, place, spec)
#         self.dependent = []
#         self.x_range = [0, 1]
#         self.init_update(dependancies, colors, max_t, a)

#     def init_update(self, dependancies: dict[int: list[list[ThreeDynamicPlots], list[callable]]], colors, max_t, a) -> None:
#         self.dependent.clear()
#         self.x_range = [min(resulting_function.x_range[0] for dependent in dependancies for resulting_function in dependent[0]), \
#                         max(resulting_function.x_range[1] for dependent in dependancies for resulting_function in dependent[0])]
#         self.y_range = [min(resulting_function.y_range[0] * 2 for dependent in dependancies for resulting_function in dependent[0]), \
#                         max(resulting_function.y_range[1] * 2 for dependent in dependancies for resulting_function in dependent[0])]
#         for index, dependent in dependancies.items(): 
#             self.dependent.append(DynamicPlot([[0, lambda x: 0]], color=colors[index], depending_on=dependent[0], arythmetic_operators=dependent[1]))
#         plt.axis([self.x_range[0], self.x_range[1], self.y_range[0], self.y_range[1]]) #! CHECK
#         self.update(0)

#     def update(self, a, t) -> None:
#         for dependent in self.dependent:
#             dependent.update(a, t, self.x_range)
#         self.figure.canvas.draw_idle()



# class ChangebleGraphic():
#     def __init__(self, figure:plt.Figure, color:str, place:int, spec:gridspec.GridSpec, dependent:DynamicGraphic) -> None:
#         self.figure = figure
#         self.dependent = dependent
#         self.x = np.linspace(0, 4, num=400)
#         self.amplitude = 5
#         self.frequency = 2.5
#         self.y = self.amplitude*np.sin(np.pi*self.frequency*self.x)
#         self.figure.add_subplot(spec[(place * 2):(place * 2 + 2), :2])
#         self.line, = plt.plot(self.x, self.y, color=color)
#         plt.axis([0, 4, -10, 10])

#         axfreq = self.figure.add_subplot(spec[place * 2, 2])
#         axamp = self.figure.add_subplot(spec[place * 2 + 1, 2])

#         self.slider_freq = Slider(axfreq, 'Freq', 0, 10.0, valinit=self.frequency, valstep=0.25, valfmt="%.2f")
#         self.slider_amp = Slider(axamp, 'Amp', 0, 10.0, valinit=self.amplitude, valstep=0.25, valfmt="%.2f")
#         self.slider_freq.on_changed(self.update)
#         self.slider_amp.on_changed(self.update)


#     def update(self, val) -> None:
#         self.amplitude = self.slider_amp.val
#         self.frequency = self.slider_freq.val
#         self.y = self.amplitude*np.sin(2*np.pi*self.frequency*self.x)
#         self.line.set_ydata(self.y)
#         self.figure.canvas.draw_idle()
#         self.dependent.update()