from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider
from typing import Optional
from PyQt5.QtCore import pyqtSignal, QObject
from manual_drawn_plot import Plot
from dataclasses import dataclass
from typing import Callable, List

@dataclass
class Range:
    x0: float
    x1: float
    y0: float
    y1: float

    def x_length(self) -> float: return self.x1 - self.x0
    def x_range(self) -> list[float, float]: return [self.x0, self.x1]
    def y_range(self) -> list[float, float]: return [self.y0, self.y1]


class TSlider(QObject):
    valueChanged = pyqtSignal(int)
    def __init__(self, ax, min_value, max_value, *args, **kwargs) -> None:
        super().__init__()
        self.slider = Slider(ax, 't', min_value, max_value, valinit=1, valstep=0.25, valfmt="%.2f")
        self.slider.on_changed(lambda _: self.on_changed(self.slider.val))

    def on_changed(self, val) -> None:
        self.valueChanged.emit(int(val))

    def val(self) -> float:
        return float(self.slider.val)



class DynamicPlot():
    def __init__(self, ax, plot: Plot, color: str = 'black') -> None:
        if plot['dependancy'] is None: assert len(plot['plots']) == 1 
        self.x = np.arange(0, 1)
        self.y = np.arange(0, 1)
        self.color = color
        self.plot = plot
        self.line, = ax.plot(self.x, self.y, color=self.color)

    def refresh(self, a: float, t: float, range: Range) -> None:
        self.x = np.linspace(range.x0, range.x1, num=100 * range.x_length())
        if t != 0:
            shifted_plot = self.plot.shift(a * t)
            self.y = np.array([shifted_plot(x) for x in self.x])
        else:
            self.y = np.array([self.plot(x) for x in self.x])
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
    
    @property
    def x(self) -> np.ndarray:
        return self.x
    @property
    def y(self) -> np.ndarray:
        return self.y
    


class WavePlot:
    def __init__(self, figure: plt.Figure, main_plot: Plot, a: float, t: float, 
                 function: Callable[[Plot, Plot], Plot],
                 colors: List[str] = ['blue', 'red', 'green']) -> None:
        self.figure = figure
        self.main_plot = main_plot
        self.a = a
        self.t = t
        self.function = function
        self.colors = colors
        self.dynamic_plots = []
        self.ax = self.figure.add_subplot()

        # Plot 1: g(x - at)
        plot_minus = self._create_shifted_plot(-1)
        self.plot1 = DynamicPlot(plot_minus, color=self.colors[0])
        
        # Plot 2: g(x + at)
        plot_plus = self._create_shifted_plot(1)
        self.plot2 = DynamicPlot(plot_plus, color=self.colors[1])
        
        # Plot 3: function(g(x-at), g(x+at))
        combined_plot = self.function(plot_minus, plot_plus)
        self.plot3 = DynamicPlot(combined_plot, color=self.colors[2])

        self.figure.canvas.draw()
    
    def refresh(self, a: float, t: float, range: Range) -> None:
        plt.axis([range.x0, range.x1, range.y0, range.y1])
        self.plot1.refresh(a, t, range)
        self.plot2.refresh(a, t, range)
        self.plot3.refresh(a, t, range)

    def get_plots(self) -> List[DynamicPlot]:
        return self.dynamic_plots



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