from __future__ import annotations
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QLineEdit, QRadioButton, QGridLayout, QButtonGroup
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
import numpy as np
from manual_drawn_plot import PlotInput
from plots import TSlider, DynamicGraphic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg



class Limiters(QWidget):
    limitersChanged = pyqtSignal(str, str, str, str, str, plt.Figure)

    def __init__(self, parent: Window, function_name: str, plot: plt.Figure) -> None:
        super().__init__()
        main_layout = QVBoxLayout()
        limiters_text = QLabel(f'Limiters of plot for {function_name} function below:')
        limiters_layout = QGridLayout()

        left_limiter, right_limiter, upper_limiter, bottom_limiter = QLineEdit('Left limiter:'), QLineEdit('Right limiter:'), QLineEdit('Upper limiter:'), QLineEdit('Bottom limiter:')
        left_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(float(left_limiter.text().replace(',', '.')), float(right_limiter.text().replace(',', '.')), float(upper_limiter.text().replace(',', '.')), float(bottom_limiter.text().replace(',', '.')), function_name, plot))
        right_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(float(left_limiter.text().replace(',', '.')), float(right_limiter.text().replace(',', '.')), float(upper_limiter.text().replace(',', '.')), float(bottom_limiter.text().replace(',', '.')), function_name, plot))
        upper_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(float(left_limiter.text().replace(',', '.')), float(right_limiter.text().replace(',', '.')), float(upper_limiter.text().replace(',', '.')), float(bottom_limiter.text().replace(',', '.')), function_name, plot))
        bottom_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(float(left_limiter.text().replace(',', '.')), float(right_limiter.text().replace(',', '.')), float(upper_limiter.text().replace(',', '.')), float(bottom_limiter.text().replace(',', '.')), function_name, plot))
        limiters_layout.addWidget(left_limiter, 0, 0)
        limiters_layout.addWidget(right_limiter, 0, 1)
        limiters_layout.addWidget(upper_limiter, 1, 0)
        limiters_layout.addWidget(bottom_limiter, 1, 1)
        limiters_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        upper_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bottom_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(limiters_text, stretch=1)
        main_layout.addLayout(limiters_layout, stretch=2)
        self.setLayout(main_layout)


    

class RadioButtons(QWidget):
    constraintType = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        main_layout = QVBoxLayout()
        button_group = QButtonGroup()
        self.button_1 = QRadioButton('Infinite')
        self.button_2 = QRadioButton('U|x=x0 = 0')
        self.button_3 = QRadioButton('Ux|x=x0 = 0')
        self.button_1.setChecked(True)
        button_group.addButton(self.button_1)
        button_group.addButton(self.button_2)
        button_group.addButton(self.button_3)
        self.button_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button_group.buttonClicked.connect(self.onTypeChange)
        main_layout.addWidget(self.button_1)
        main_layout.addWidget(self.button_2)
        main_layout.addWidget(self.button_3)
        self.setLayout(main_layout)

    def onTypeChange(self, button) -> None:
        data = {
            'Infinite': 'none',
            'U|x=...': 'even',
            'Ux|x=...': 'odd'
        }
        assert data[button.text()] is not None
        self.constraintType.emit(data[button.text()])

    def getType(self) -> str:
        if self.button_2.isChecked():
            return "even"
        elif self.button_3.isChecked():
            return "odd"
        return "none"




class Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        main_layout = QVBoxLayout()

        self.range = [[-10, 10], [-10, 10]]


        # Parameters phi and psi
        self.input_plots = {
            'φ(x)': None,
            'ψ(x)': None
        }

        functions_settings_layout = QHBoxLayout()
        main_layout.addLayout(functions_settings_layout)

        phi_layout = QVBoxLayout()
        phi_text_layout = QHBoxLayout()
        phi_text = QLabel('U|t=0 = ϕ(x) = ')
        self.phi_parameter = QLineEdit()
        self.phi_parameter.setPlaceholderText('Enter the ϕ(x) or draw it manually in the plot')  
        self.phi_parameter.textChanged.connect(lambda _: self.draw_initial_plot('φ(x)', self.phi_parameter.text(), self.phi_input_plot_figure, self.phi_input_plot_figure_canvas))
        phi_text_layout.addWidget(phi_text, stretch=1)
        phi_text_layout.addWidget(self.phi_parameter, stretch=5)
        self.phi_input_plot_figure = plt.figure()
        self.phi_input_plot_figure_canvas = FigureCanvasQTAgg(self.phi_input_plot_figure)
        phi_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.phi_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.phi_input_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        phi_layout.addLayout(phi_text_layout, stretch=3)
        phi_layout.addWidget(Limiters(self, 'φ(x)', self.phi_input_plot_figure), stretch=3)
        phi_layout.addWidget(self.phi_input_plot_figure_canvas, stretch=12)

        psi_layout = QVBoxLayout()
        psi_text_layout = QHBoxLayout()
        psi_text = QLabel('Ut|t=0 = ψ(x) = ')
        self.psi_parameter = QLineEdit()
        self.psi_parameter.setPlaceholderText('Enter the ψ(x) or draw it manually in the plot')  
        self.psi_parameter.textChanged.connect(lambda _: self.draw_initial_plot('φ(x)', self.phi_parameter.text(), self.psi_initial_plot_figure, self.psi_initial_plot_figure_canvas))
        psi_text_layout.addWidget(psi_text, stretch=1)
        psi_text_layout.addWidget(self.psi_parameter, stretch=5)
        self.psi_input_plot_figure = plt.figure()
        self.psi_input_plot_figure_canvas = FigureCanvasQTAgg(self.phi_input_plot_figure)
        psi_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_input_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        psi_layout.addLayout(psi_text_layout, stretch=3)
        psi_layout.addWidget(Limiters(self, 'ψ(x)', self.psi_input_plot_figure), stretch=3)
        psi_layout.addWidget(self.psi_input_plot_figure_canvas, stretch=12)
        
        functions_settings_layout.addLayout(phi_layout, stretch=1)
        functions_settings_layout.addLayout(psi_layout, stretch=1)


        # Parameters a, t and f(x, t)
        main_settings_layout = QVBoxLayout()
        main_layout.addLayout(main_settings_layout)

        equation_text_layout = QHBoxLayout()
        main_settings_layout.addLayout(equation_text_layout, stretch=1)
        first_part = QLabel('Utt = ')
        self.a_parameter = QLineEdit()
        self.a_parameter.setPlaceholderText('a ** 2')
        # self.a_parameter.textChanged.connect(lambda _: self.refresh(self.a_parameter.text()))
        self.a_parameter.textChanged.connect(self.refresh_resulting_plots)
        second_part = QLabel('Uxx + f(x, t)')
        equation_text_layout.addWidget(first_part, stretch=3)
        equation_text_layout.addWidget(self.a_parameter, stretch=1)
        equation_text_layout.addWidget(second_part, stretch=3)
        first_part.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.a_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        second_part.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.t_slider_figure = plt.figure()
        self.t_slider_figure_canvas = FigureCanvasQTAgg(self.t_slider_figure)
        main_settings_layout.addWidget(self.t_slider_figure_canvas, stretch=1)
        self.t_slider_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        f_layout = QHBoxLayout()
        main_settings_layout.addLayout(f_layout, stretch=1)
        f_text = QLabel('f(x, t) = ')
        self.f_function = QLineEdit()
        self.f_function.setPlaceholderText('0')
        self.f_function.setEnabled(False) #! TODOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
        self.f_function.textChanged.connect(self.refresh_resulting_plots)
        # self.f_function.textChanged.connect(lambda _: self.refresh(self.f_function.text()))
        f_layout.addWidget(f_text, stretch=1)
        f_layout.addWidget(self.f_function, stretch=4)
        f_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.f_function.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        # Limiters of the string 
        constraint_layout = QHBoxLayout()
        main_layout.addLayout(constraint_layout)
        
        left_constraint_layout = QVBoxLayout()
        self.left_constraint_choose = RadioButtons()
        self.left_constraint_choose.constraintType.connect(self.refresh_left_constraint)
        left_x0_pararameter_layout = QHBoxLayout()
        left_x0_pararameter_text = QLabel('x0 = ')
        self.left_x0_parameter = QLineEdit('0')
        self.left_x0_parameter.setPlaceholderText('Enter the x0 if you choose U|x=x0 = 0 or Ux|x=x0 = 0')
        self.left_x0_parameter.textChanged.connect(self.refresh_initial_plots)
        self.left_x0_parameter.setEnabled(False)
        left_x0_pararameter_layout.addWidget(left_x0_pararameter_text, stretch=1)
        left_x0_pararameter_layout.addWidget(self.left_x0_parameter, stretch=4)
        self.left_constraint_choose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_x0_pararameter_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_x0_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        left_constraint_layout.addWidget(self.left_constraint_choose)
        left_constraint_layout.addLayout(left_x0_pararameter_layout)
        
        right_constraint_layout = QVBoxLayout()
        self.right_constraint_choose = RadioButtons()
        self.right_constraint_choose.constraintType.connect(self.refresh_initial_plots)
        right_x0_pararameter_layout = QHBoxLayout()
        right_x0_pararameter_text = QLabel('x0 = ')
        self.right_x0_parameter = QLineEdit('1')
        self.right_x0_parameter.setPlaceholderText('Enter the x0 if you choose U|x=x0 = 0 or Ux|x=x0 = 0')
        self.right_x0_parameter.textChanged.connect(self.refresh_initial_plots)
        self.right_x0_parameter.setEnabled(False)
        right_x0_pararameter_layout.addWidget(right_x0_pararameter_text, stretch=1)
        right_x0_pararameter_layout.addWidget(self.right_x0_parameter, stretch=4)
        self.right_constraint_choose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_x0_pararameter_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_x0_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_constraint_layout.addWidget(self.right_constraint_choose)
        right_constraint_layout.addLayout(right_x0_pararameter_layout)

        constraint_layout.addLayout(left_constraint_layout, stretch=1)
        constraint_layout.addLayout(right_constraint_layout, stretch=1)


        # Initial plots
        initial_plots_layout = QHBoxLayout()
        main_layout.addLayout(initial_plots_layout)

        self.phi_initial_plot_figure = plt.figure()
        self.phi_initial_plot_figure_canvas = FigureCanvasQTAgg(self.phi_initial_plot_figure)
        self.phi_initial_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        initial_plots_layout.addWidget(self.phi_initial_plot_figure_canvas, stretch=1)

        self.psi_initial_plot_figure = plt.figure()
        self.psi_initial_plot_figure_canvas = FigureCanvasQTAgg(self.psi_initial_plot_figure)
        self.psi_initial_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        
        initial_plots_layout.addWidget(self.psi_initial_plot_figure_canvas, stretch=1)


        # Resulting plots
        self.phi_plot_figure = plt.figure()
        self.phi_plot_figure_canvas = FigureCanvasQTAgg(self.phi_plot_figure)
        self.phi_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.phi_plot_figure_canvas, stretch=1)
        
        self.psi_plot_figure = plt.figure()
        self.psi_plot_figure_canvas = FigureCanvasQTAgg(self.psi_plot_figure)
        self.psi_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.psi_plot_figure_canvas, stretch=1)
        
        self.result_plot_figure = plt.figure()
        self.result_plot_figure_canvas = FigureCanvasQTAgg(self.result_plot_figure)
        self.result_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.result_plot_figure_canvas, stretch=1)

        self.refresh_slider(10)
        self.refresh_input_plot(-5, 5, -2, 2, 'φ(x)', self.phi_input_plot_figure, self.phi_initial_plot_figure_canvas)
        self.refresh_input_plot(-5, 5, -2, 2, 'ψ(x)', self.psi_input_plot_figure, self.psi_initial_plot_figure_canvas)
        self.refresh_initial_plots()
        self.setLayout(main_layout)



    def refresh_slider(self, max_value: float) -> None:
        self.t_slider_figure.clear()
        ax = self.t_slider_figure.add_subplot(111)
        self.t_slider = TSlider(ax, 0, max_value)
        self.t_slider.valueChanged.connect(self.refresh_resulting_plots)

        
    def draw_initial_plot(self, function_name: str, function: str, figure: plt.Figure, canvas: FigureCanvasQTAgg) -> None: #TODO
        assert function_name in self.input_plots.keys()
        figure.clear()
        ax = figure.add_subplot(111)
        y = eval(function)
        x = np.linspace(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0]) * 100)
        y = [y(dot) for dot in x]
        self.input_plots[function_name], = ax.plot(x, y)
        self.refresh_initial_plots()
        canvas.draw()



    def refresh_input_plot(self, left: float, right: float, upper: float, bottom: float, function_name: str, figure: plt.Figure, canvas: FigureCanvasQTAgg) -> None:#TODO
        assert function_name in self.input_plots.keys()
        figure.clear()
        self.input_plots[function_name] = PlotInput(figure=figure, xlim=[left, right], ylim=[bottom, upper])
        self.input_plots[function_name].finishedDrawing.connect(self.refresh_initial_plots)
        canvas.draw()


    def refresh_left_constraint(self) -> None:
        self.left_x0_parameter.setEnabled('none' != self.left_constraint_choose.getType())
        self.refresh_initial_plots()


    def refresh_right_constraint(self) -> None:
        self.right_x0_parameter.setEnabled('none' != self.right_constraint_choose.getType())
        self.refresh_initial_plots()


    def refresh_initial_plots(self) -> None:
        self.phi_initial_plot_figure.clear()
        self.psi_initial_plot_figure.clear()

        ax1 = self.phi_initial_plot_figure.add_subplot(111)
        ax2 = self.psi_initial_plot_figure.add_subplot(111)
        
        ax1.set_title('φ(x)')
        ax2.set_title('ψ(x)')

        left_constraint_type = self.left_constraint_choose.getType()
        right_constraint_type = self.right_constraint_choose.getType()
        left_constraint_x0 = float(self.left_x0_parameter.text().replace(',', '.'))
        right_constraint_x0 = float(self.right_x0_parameter.text().replace(',', '.'))
        assert right_constraint_x0 > left_constraint_x0
        
        self.phi_initial_plot_figure_canvas.draw()
        self.psi_initial_plot_figure_canvas.draw()
        self.refresh_resulting_plots()


    def refresh_resulting_plots(self) -> None:
        self.phi_plot_figure.clear()
        self.psi_plot_figure.clear()
        self.result_plot_figure.clear()

        if self.a_parameter.text() != '':
            a = float(self.a_parameter.text().replace(',', '.')) ** 0.5
        else:
            a = 1
        t = self.t_slider.val()

        ax1 = self.phi_plot_figure.add_subplot(111)
        ax2 = self.psi_plot_figure.add_subplot(111)
        ax3 = self.result_plot_figure.add_subplot(111)
        
        ax1.set_title('Modification of the φ(x)')
        ax1.legend()
        ax2.set_title('Modification of the ψ(x)')
        ax2.legend()
        ax3.set_title('Result')
        ax3.legend()
        
        self.phi_plot_figure_canvas.draw()
        self.psi_plot_figure_canvas.draw()
        self.result_plot_figure_canvas.draw()
