from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider
from typing import Optional
from manual_drawn_plot import Segment


class TSlider(Slider):
    def __init__(self, dependent: list[DynamicGraphic], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for dependent in dependent:
            dependent.update()



class DynamicGraphic():
    def __init__(self, function: list[float, callable, callable], color: str = 'black', depending_on: Optional[list[DynamicGraphic]] = [], arythmetic_operators: Optional[list[callable]] = []) -> None:
        self.function = function
        assert len(arythmetic_operators) == len(depending_on)
        self.depending_on = depending_on
        self.arythmetic_operators = arythmetic_operators
        self.x = np.arange(0, 1)
        self.y = np.arange(0, 1)
        self.color = color
        self.line, = plt.plot(self.x, self.y, color=self.color)

    def update(self, a: float, t: float, x_range: list[float, float]) -> None:
        self.x = np.linspace(x_range[0], x_range[1], num=100 * (x_range[1] - x_range[0]))
        self.y = np.array()
        for x in self.x:
            i = 0
            while (self.function[i][2](x, a, t) < self.function[i][0]) and (i < len(self.function) - 1): i += 1
            np.append(self.y, self.function[i][1](self.function[i][2](x, a, t)))
        if self.depending_on:
            for index, result in enumerate(self.depending_on):
                self.y = self.arythmetic_operators[index](self.y, result.y)
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
    
    @property
    def x(self) -> np.ndarray:
        return self.x
    @property
    def y(self) -> np.ndarray:
        return self.y

    



class ThreePlotsIntermediate(DynamicGraphic):
    def __init__(self, figure:plt.Figure, colors:list[str], place:int, spec:gridspec.GridSpec, functions: list[list[float, callable, callable]], dependancies: dict[int: list[list[int], list[callable]]] =[], a: float = 1, max_t: float = 5) -> None:
        # super().__init__(figure, place, spec)
        self.dependent = []
        self.x_range = [0, 1]
        self.init_update(functions, dependancies, colors, max_t, a)

    def init_update(self, functions, dependancies: dict[int: list[list[int], list[callable]]], colors, max_t, a) -> None:
        self.dependent.clear()
        self.x_range = [min(function[0][0] for function in functions) - a * max_t, \
                    max(function[-1][0] for function in functions) + a * max_t]
        self.y_range = [min(min(function[i][1](function[i][0]), function[i][1](function[(i + 1) % len(function)][0])) \
                            for i in range(len(function)) for function in functions) * 2, \
                        max(max(function[i][1](function[i][0]), function[i][1](function[(i + 1) % len(function)][0])) \
                            for i in range(len(function)) for function in functions) * 2]
        for index, function in enumerate(functions): 
            self.dependent.append(DynamicGraphic(function, color=colors[index], depending_on=self.dependent[dependancies[index][0]], arythmetic_operators=dependancies[index][1])\
                                if dependancies else \
                                DynamicGraphic(function, color=colors[index]))
        plt.axis([self.x_range[0], self.x_range[1], self.y_range[0], self.y_range[1]]) #! CHECK
        self.update(0)

    def update(self, a, t) -> None:
        for dependent in self.dependent:
            dependent.update(a, t, self.x_range)
        self.figure.canvas.draw_idle()
    
    def resulting_function(self) -> list[np.ndarray, np.ndarray]:
        return (self.dependent[-1].x, self.dependent[-1].y)
    
    @property
    def x_range(self) -> list[float, float]:
        return self.x_range
    @property
    def y_range(self) -> list[float, float]:
        return self.y_range



class ThreePlotsFinal(DynamicGraphic):
    def __init__(self, figure:plt.Figure, colors:list[str], place:int, spec:gridspec.GridSpec, dependancies: dict[int: list[list[ThreePlotsIntermediate], list[callable]]] =[], a: float = 1, max_t: float = 5) -> None:
        # super().__init__(figure, place, spec)
        self.dependent = []
        self.x_range = [0, 1]
        self.init_update(dependancies, colors, max_t, a)

    def init_update(self, dependancies: dict[int: list[list[ThreePlotsIntermediate], list[callable]]], colors, max_t, a) -> None:
        self.dependent.clear()
        self.x_range = [min(resulting_function.x_range[0] for dependent in dependancies for resulting_function in dependent[0]), \
                        max(resulting_function.x_range[1] for dependent in dependancies for resulting_function in dependent[0])]
        self.y_range = [min(resulting_function.y_range[0] * 2 for dependent in dependancies for resulting_function in dependent[0]), \
                        max(resulting_function.y_range[1] * 2 for dependent in dependancies for resulting_function in dependent[0])]
        for index, dependent in dependancies.items(): 
            self.dependent.append(DynamicGraphic([[0, lambda x: 0]], color=colors[index], depending_on=dependent[0], arythmetic_operators=dependent[1]))
        plt.axis([self.x_range[0], self.x_range[1], self.y_range[0], self.y_range[1]]) #! CHECK
        self.update(0)

    def update(self, a, t) -> None:
        for dependent in self.dependent:
            dependent.update(a, t, self.x_range)
        self.figure.canvas.draw_idle()



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