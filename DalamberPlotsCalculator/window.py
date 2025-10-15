from __future__ import annotations
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QLineEdit, QRadioButton, QGridLayout, QButtonGroup
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
import numpy as np
from manual_drawn_plot import PlotInput, Plot, Segment
from plots import TSlider, WavePlot, Range, SinglePlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg



class Limiters(QWidget):
    limitersChanged = pyqtSignal(float, float, float, float, float)

    def __init__(self, parent: Window) -> None:
        super().__init__()
        main_layout = QVBoxLayout()
        limiters_text = QLabel(f'Limiters of plot for functions below:')
        limiters_layout = QGridLayout()

        left_limiter_text, right_limiter_text, upper_limiter_text, bottom_limiter_text = QLabel('Left limiter:'), QLabel('Right limiter:'), QLabel('Upper limiter:'), QLabel('Bottom limiter:')
        self.left_limiter, self.right_limiter, self.upper_limiter, self.bottom_limiter = QLineEdit('0'), QLineEdit('5'), QLineEdit('-1'), QLineEdit('1')
        self.left_limiter.textChanged.connect(parent.refresh_input_plots)
        self.right_limiter.textChanged.connect(parent.refresh_input_plots)
        self.upper_limiter.textChanged.connect(parent.refresh_input_plots)
        self.bottom_limiter.textChanged.connect(parent.refresh_input_plots)
        limiters_layout.addWidget(left_limiter_text, 0, 0), limiters_layout.addWidget(self.left_limiter, 1, 0), 
        limiters_layout.addWidget(right_limiter_text, 2, 0), limiters_layout.addWidget(self.right_limiter, 3, 0) 
        limiters_layout.addWidget(upper_limiter_text, 0, 1), limiters_layout.addWidget(self.upper_limiter, 1, 1)
        limiters_layout.addWidget(bottom_limiter_text, 2, 1), limiters_layout.addWidget(self.bottom_limiter, 3, 1)
        limiters_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.upper_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bottom_limiter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(limiters_text, stretch=1)
        main_layout.addLayout(limiters_layout, stretch=2)
        self.setLayout(main_layout)
    
    def get_limiters(self, resulting: bool = False) -> Range:
        if resulting:
            return Range(float(self.left_limiter.text().replace(',', '.')), float(self.right_limiter.text().replace(',', '.')), float(self.upper_limiter.text().replace(',', '.')) * 2, float(self.bottom_limiter.text().replace(',', '.')) * 2)
        return Range(float(self.left_limiter.text().replace(',', '.')), float(self.right_limiter.text().replace(',', '.')), float(self.upper_limiter.text().replace(',', '.')), float(self.bottom_limiter.text().replace(',', '.')))


    

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
        button_group.buttonReleased.connect(self.onTypeChange)
        main_layout.addWidget(self.button_1)
        main_layout.addWidget(self.button_2)
        main_layout.addWidget(self.button_3)
        self.setLayout(main_layout)

    def onTypeChange(self, button) -> None:
        print("onTypeChange!")
        data = {
            'Infinite': 'none',
            'U|x=x0 = 0': 'even', 
            'Ux|x=x0 = 0': 'odd'
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
        plots_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        main_layout.addLayout(plots_layout, stretch=3)


        # Parameters phi and psi
        self.input_plots = {
            'φ(x)': None,
            'ψ(x)': None
        }

        self.plots_data = {
            'φ(x)': None,
            'ψ(x)': None
        }

        settings_layout = QVBoxLayout()
        main_layout.addLayout(settings_layout, stretch=1)

        functions_settings_layout = QVBoxLayout()
        settings_layout.addLayout(functions_settings_layout, stretch=70)

        self.functions_limiter = Limiters(self)
        functions_settings_layout.addWidget(self.functions_limiter, stretch=1)

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
        phi_layout.addWidget(self.phi_input_plot_figure_canvas, stretch=12)

        psi_layout = QVBoxLayout()
        psi_text_layout = QHBoxLayout()
        psi_text = QLabel('Ut|t=0 = ψ(x) = ')
        self.psi_parameter = QLineEdit()
        self.psi_parameter.setPlaceholderText('Enter the ψ(x) or draw it manually in the plot')  
        self.psi_parameter.textChanged.connect(lambda _: self.draw_initial_plot('φ(x)', self.psi_parameter.text(), self.psi_initial_plot_figure, self.psi_initial_plot_figure_canvas))
        psi_text_layout.addWidget(psi_text, stretch=1)
        psi_text_layout.addWidget(self.psi_parameter, stretch=5)
        self.psi_input_plot_figure = plt.figure()
        self.psi_input_plot_figure_canvas = FigureCanvasQTAgg(self.psi_input_plot_figure)
        psi_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_input_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        psi_layout.addLayout(psi_text_layout, stretch=3)
        psi_layout.addWidget(self.psi_input_plot_figure_canvas, stretch=12)
        
        functions_settings_layout.addLayout(phi_layout, stretch=3)
        functions_settings_layout.addLayout(psi_layout, stretch=3)


        # Parameters a, t and f(x, t)
        main_settings_layout = QVBoxLayout()
        settings_layout.addLayout(main_settings_layout, stretch=5)

        equation_text_layout = QHBoxLayout()
        main_settings_layout.addLayout(equation_text_layout, stretch=1)
        first_part = QLabel('Utt = ')
        self.a_parameter = QLineEdit('1')
        self.a_parameter.setPlaceholderText('a ** 2')
        # self.a_parameter.textChanged.connect(lambda _: self.refresh(self.a_parameter.text()))
        self.a_parameter.textChanged.connect(self.refresh_resulting_plots)
        second_part = QLabel('Uxx + ')
        self.f_function = QLineEdit('0')
        self.f_function.setEnabled(False) #! TODOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
        self.f_function.textChanged.connect(self.refresh_resulting_plots)
        equation_text_layout.addWidget(first_part, stretch=3)
        equation_text_layout.addWidget(self.a_parameter, stretch=1)
        equation_text_layout.addWidget(second_part, stretch=3)
        equation_text_layout.addWidget(self.f_function, stretch=1)
        first_part.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.a_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        second_part.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.f_function.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.t_slider_figure = plt.figure()
        self.t_slider_figure_canvas = FigureCanvasQTAgg(self.t_slider_figure)
        main_settings_layout.addWidget(self.t_slider_figure_canvas, stretch=1)
        self.t_slider_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        # Limiters of the string 
        constraint_layout = QHBoxLayout()
        settings_layout.addLayout(constraint_layout, stretch=10)
        
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
        plots_layout.addLayout(initial_plots_layout, stretch=20)

        self.phi_initial_plot_figure = plt.figure()
        self.phi_initial_plot_figure_canvas = FigureCanvasQTAgg(self.phi_initial_plot_figure)
        self.phi_initial_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        initial_plots_layout.addWidget(self.phi_initial_plot_figure_canvas, stretch=1)

        self.psi_initial_plot_figure = plt.figure()
        self.psi_initial_plot_figure_canvas = FigureCanvasQTAgg(self.psi_initial_plot_figure)
        self.psi_initial_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        
        initial_plots_layout.addWidget(self.psi_initial_plot_figure_canvas, stretch=1)


        # Resulting plots
        resulting_plots_layout = QHBoxLayout()
        plots_layout.addLayout(resulting_plots_layout, stretch=20)

        self.phi_plot_figure = plt.figure()
        self.psi_plot_figure = plt.figure()
        self.phi_plot_figure_canvas = FigureCanvasQTAgg(self.phi_plot_figure)
        self.psi_plot_figure_canvas = FigureCanvasQTAgg(self.psi_plot_figure)
        resulting_plots_layout.addWidget(self.phi_plot_figure_canvas)
        resulting_plots_layout.addWidget(self.psi_plot_figure_canvas)
        self.phi_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        result_and_f_plots_layout = QHBoxLayout()
        plots_layout.addLayout(result_and_f_plots_layout, stretch=20)

        self.f_plot_figure = plt.figure()
        self.result_plot_figure = plt.figure()
        self.f_plot_figure_canvas = FigureCanvasQTAgg(self.f_plot_figure)
        self.result_plot_figure_canvas = FigureCanvasQTAgg(self.result_plot_figure)
        result_and_f_plots_layout.addWidget(self.f_plot_figure_canvas, stretch=1)
        result_and_f_plots_layout.addWidget(self.result_plot_figure_canvas, stretch=1)
        self.f_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.extended_range = self.functions_limiter.get_limiters()
        self.refresh_slider(10)
        self.refresh_input_plots()
        self.setLayout(main_layout)



    def refresh_slider(self, max_value: float) -> None:
        self.t_slider_figure.clear()
        ax = self.t_slider_figure.add_subplot(111)
        self.t_slider = TSlider(ax, 0, max_value)
        self.t_slider.valueChanged.connect(self.refresh_parameter_changed)

        
    def draw_initial_plot(self, function_name: str, function: str, figure: plt.Figure, canvas: FigureCanvasQTAgg) -> None: #TODO
        assert function_name in self.input_plots.keys()
        figure.clear()
        ax = figure.add_subplot(111)
        # y = eval(function)
        x = np.linspace(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0]) * 100)
        y = [(dot) for dot in x]
        self.input_plots[function_name], = ax.plot(x, y)
        self.refresh_initial_plots()
        canvas.draw()



    def refresh_input_plots(self) -> None:
        range = self.functions_limiter.get_limiters(resulting=True)
        self.phi_input_plot_figure.clear()
        self.psi_input_plot_figure.clear()
        self.input_plots['φ(x)'] = PlotInput(figure=self.phi_input_plot_figure, canvas=self.phi_input_plot_figure_canvas, xlim=[range.x0, range.x1], ylim=[range.y0, range.y1])
        self.input_plots['φ(x)'].finishedDrawing.connect(self.refresh_initial_plots)
        self.input_plots['ψ(x)'] = PlotInput(figure=self.psi_input_plot_figure, canvas=self.psi_input_plot_figure_canvas, xlim=[range.x0, range.x1], ylim=[range.y0, range.y1])
        self.input_plots['ψ(x)'].finishedDrawing.connect(self.refresh_initial_plots)
        self.refresh_initial_plots()


    def refresh_left_constraint(self) -> None:
        print("Left Constraint has changed!")
        print(self.left_constraint_choose.getType())
        self.left_x0_parameter.setEnabled(self.left_constraint_choose.getType() != 'none')
        self.refresh_initial_plots()


    def refresh_right_constraint(self) -> None:
        print("Left Constraint has changed!")
        print(self.left_constraint_choose.getType())
        self.right_x0_parameter.setEnabled('none' != self.right_constraint_choose.getType())
        self.refresh_initial_plots()


    # def refresh_initial_plots(self) -> None:
    #     self.phi_initial_plot_figure.clear()
    #     self.psi_initial_plot_figure.clear()

    #     range = self.functions_limiter.get_limiters()
    #     a = float(self.a_parameter.text().replace(',', '.'))
    #     assert a > 0
    #     a = a ** 0.5

    #     left_constraint_type = self.left_constraint_choose.getType()
    #     right_constraint_type = self.right_constraint_choose.getType()
    #     left_constraint_x0 = float(self.left_x0_parameter.text().replace(',', '.'))
    #     right_constraint_x0 = float(self.right_x0_parameter.text().replace(',', '.'))
    #     assert left_constraint_x0 >= range.x0
    #     assert right_constraint_x0 <= range.x1
    #     assert right_constraint_x0 > left_constraint_x0

    #     self.plots_data['φ(x)'] = self.input_plots['φ(x)'].get_plot()
    #     self.plots_data['ψ(x)'] = self.input_plots['ψ(x)'].get_plot()

    #     def extend_plot(plot: Plot, left_bound: float, left_type: str, right_bound: float, right_type: str) -> Plot:
    #         left_extension = [] 
    #         right_extension = []
    #         if left_type != 'none':
    #             if left_type == 'even':
    #                 for segment in plot.segments:
    #                     if segment.x0 >= left_bound:
    #                         segment = Segment(left_bound - segment.x0, left_bound - segment.x1, segment.function)
    #                         left_extension.append(segment)
    #             elif left_type == 'odd': 
    #                 for segment in plot.segments:
    #                     if segment.x0 >= left_bound:
    #                         segment = Segment(left_bound - segment.x0, left_bound - segment.x1, lambda x: -segment(x))
    #                         left_extension.append(segment)
    #             left_extension.reverse()
    #         left_extension += [segment for segment in plot.segments]
    #         if right_type != 'none':
    #             if right_type == 'even':
    #                 for segment in plot.segments[::-1]:
    #                     if segment.x1 <= right_type:
    #                         segment = Segment(segment.x1 - right_type, right_type - segment.x0, segment.function)
    #                         right_extension.append(segment)
    #             elif right_type == 'odd':
    #                 for segment in plot.segments[::-1]:
    #                     if segment.x1 <= right_type:
    #                         segment = Segment(segment.x1 - right_type, right_type - segment.x0, lambda x: -segment(x))
    #                         right_extension.append(segment)
    #         return Plot(left_extension + right_extension)

    #     # Создаем расширенный диапазон для отображения
    #     extended_range = Range(
    #         range.x0 - extension_width,
    #         range.x1 + extension_width,
    #         range.y0, range.y1
    #     )

    #     # Расширяем графики
    #     extended_phi_plot = extend_plot(phi_plot, left_constraint_x0, left_constraint_type, right_constraint_x0, right_constraint_type)
    #     extended_psi_plot = extend_plot(psi_plot, left_constraint_x0, left_constraint_type, right_constraint_x0, right_constraint_type)

    #     # Отрисовываем расширенные графики
    #     SinglePlot(self.phi_initial_plot_figure, self.phi_initial_plot_figure_canvas, extended_phi_plot, a, extended_range, 'Extended φ(x)', colors=['orange'])
    #     SinglePlot(self.psi_initial_plot_figure, self.psi_initial_plot_figure_canvas, extended_psi_plot, a, extended_range, 'Extended ψ(x)', lambda plot: plot.integrate(), colors=['black', 'blue'])

    #     # Добавляем вертикальные линии для обозначения границ
    #     ax_phi = self.phi_initial_plot_figure.gca()
    #     ax_psi = self.psi_initial_plot_figure.gca()

    #     ax_phi.axvline(x=left_constraint_x0, color='r', linestyle='--', alpha=0.7, label=f'Left bound ({left_constraint_type})')
    #     ax_phi.axvline(x=right_constraint_x0, color='g', linestyle='--', alpha=0.7, label=f'Right bound ({right_constraint_type})')

    #     ax_psi.axvline(x=left_constraint_x0, color='r', linestyle='--', alpha=0.7, label=f'Left bound ({left_constraint_type})')
    #     ax_psi.axvline(x=right_constraint_x0, color='g', linestyle='--', alpha=0.7, label=f'Right bound ({right_constraint_type})')

    #     ax_phi.legend()
    #     ax_psi.legend()

    #     self.refresh_resulting_plots()



    def refresh_initial_plots(self) -> None:
        self.phi_initial_plot_figure.clear()
        self.psi_initial_plot_figure.clear()

        range = self.functions_limiter.get_limiters()
        a = float(self.a_parameter.text().replace(',', '.'))
        assert a > 0
        a = a ** 0.5
        
        left_constraint_type = self.left_constraint_choose.getType()
        right_constraint_type = self.right_constraint_choose.getType()
        left_constraint_x0 = float(self.left_x0_parameter.text().replace(',', '.'))
        right_constraint_x0 = float(self.right_x0_parameter.text().replace(',', '.'))
        assert right_constraint_x0 > left_constraint_x0

        SinglePlot(self.phi_initial_plot_figure, self.phi_initial_plot_figure_canvas, self.input_plots['φ(x)'].get_plot(), a, range, 'Initial φ(x)', colors=['orange'])
        SinglePlot(self.psi_initial_plot_figure, self.psi_initial_plot_figure_canvas, self.input_plots['ψ(x)'].get_plot(), a, range, 'Initial ψ(x)', lambda plot: plot.integrate(), colors=['black', 'blue'])

        self.refresh_resulting_plots()


    def refresh_parameter_changed(self) -> None:
        self.phi_plot_figure


    def refresh_resulting_plots(self) -> None:
        self.phi_plot_figure.clear()
        self.psi_plot_figure.clear()
        self.f_plot_figure.clear()
        self.result_plot_figure.clear()

        if self.a_parameter.text() != '':
            a = float(self.a_parameter.text().replace(',', '.')) ** 0.5
        else:
            a = 1
        t = self.t_slider.val()

        ax1 = self.phi_plot_figure.add_subplot(111)
        ax2 = self.psi_plot_figure.add_subplot(111)
        ax3 = self.f_plot_figure.add_subplot(111)
        ax4 = self.result_plot_figure.add_subplot(111)
        
        ax1.set_title('Modification of the φ(x)')
        ax1.legend()
        ax2.set_title('Modification of the ψ(x)')
        ax2.legend()
        ax3.set_title('Modification of the f(x, t)')
        ax3.legend()
        ax4.set_title('Result')
        ax4.legend()
        
        self.phi_plot_figure_canvas.draw()
        self.psi_plot_figure_canvas.draw()
        self.f_plot_figure_canvas.draw()
        self.result_plot_figure_canvas.draw()

    
    def find_range(self) -> Range:
        range = self.functions_limiter.get_limiters()
        if self.left_x0_parameter != '0':
            range.x0 -= range.x1 - float(self.left_x0_parameter.text().replace(',', '.'))
        if self.right_x0_parameter != '0':
            range.x1 += float(self.right_x0_parameter.text().replace(',', '.')) - range.x0 
        range.x0 -= 2
        range.x1 += 2
        range.y0 *= 2
        range.y1 *= 2
        return range