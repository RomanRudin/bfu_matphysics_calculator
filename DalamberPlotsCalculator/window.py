from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QLineEdit, QRadioButton, QGridLayout, QButtonGroup
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from manual_drawn_plot import PlotInput
from plots import ThreePlotsFinal, ThreePlotsIntermediate, TSlider
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from __future__ import annotations


class Limiters(QWidget):
    def __init__(self, parent: Window, function_name: str, plot: plt.Figure) -> None:
        super().__init__()
        main_layout = QVBoxLayout()
        limiters_text = QLabel(f'Limiters of plot for {function_name} function below:')
        limiters_layout = QGridLayout()

        left_limiter, right_limiter, upper_limiter, bottom_limiter = QLineEdit('Left limiter:'), QLineEdit('Right limiter:'), QLineEdit('Upper limiter:'), QLineEdit('Bottom limiter:')
        left_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(left_limiter.text(), right_limiter.text(), upper_limiter.text(), bottom_limiter.text(), function_name, plot))
        right_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(left_limiter.text(), right_limiter.text(), upper_limiter.text(), bottom_limiter.text(), function_name, plot))
        upper_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(left_limiter.text(), right_limiter.text(), upper_limiter.text(), bottom_limiter.text(), function_name, plot))
        bottom_limiter.textChanged.connect(lambda _: parent.refresh_input_plots(left_limiter.text(), right_limiter.text(), upper_limiter.text(), bottom_limiter.text(), function_name, plot))
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
        main_layout.addWidget(button_group)
        button_group.buttonClicked.connect(self.onTypeChange)
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
        self.phi_parameter.textChanged.connect(self.refresh)
        phi_text_layout.addWidget(phi_text, stretch=1)
        phi_text_layout.addWidget(self.phi_parameter, stretch=5)
        self.phi_input_plot_figure = plt.figure()
        self.phi_input_plot_figure_canvas = FigureCanvasQTAgg(self.phi_input_plot_figure)
        phi_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.phi_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.phi_input_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        phi_layout.addLayout(phi_text_layout, stretch=3)
        phi_layout.addWidget(Limiters(self, 'φ(x)', self.psi_input_plot_figure), stretch=3)
        phi_layout.addWidget(self.phi_input_plot_figure_canvas, stretch=12)

        psi_layout = QVBoxLayout()
        psi_text_layout = QHBoxLayout()
        psi_text = QLabel('Ut|t=0 = ψ(x) = ')
        self.psi_parameter = QLineEdit()
        self.psi_parameter.setPlaceholderText('Enter the ψ(x) or draw it manually in the plot')  
        self.psi_parameter.textChanged.connect(self.refresh)
        psi_text_layout.addWidget(psi_text, stretch=1)
        psi_text_layout.addWidget(self.psi_parameter, stretch=5)
        self.psi_input_plot_figure = plt.figure()
        self.psi_input_plot_figure_canvas = FigureCanvasQTAgg(self.phi_input_plot_figure)
        psi_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_input_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        psi_layout.addLayout(psi_text_layout, stretch=3)
        phi_layout.addWidget(Limiters(self, 'ψ(x)', self.psi_input_plot_figure), stretch=3)
        psi_layout.addWidget(self.psi_input_plot, stretch=12)
        
        functions_settings_layout.addLayout(phi_layout, stretch=1)
        functions_settings_layout.addLayout(psi_layout, stretch=1)


        # Parameters a, t and f(x, t)
        main_settings_layout = QHBoxLayout()
        main_layout.addLayout(main_settings_layout)

        equation_text_layout = QHBoxLayout()
        main_settings_layout.addLayout(equation_text_layout, stretch=1)
        first_part = QLabel('Utt = ')
        self.a_parameter = QLineEdit()
        self.a_parameter.setPlaceholderText('a ** 2')
        # self.a_parameter.textChanged.connect(lambda _: self.refresh(self.a_parameter.text()))
        self.a_parameter.textChanged.connect(self.refresh)
        second_part = QLabel('Uxx + f(x, t)')
        equation_text_layout.addWidget(first_part, stretch=3)
        equation_text_layout.addWidget(self.a_parameter, stretch=1)
        equation_text_layout.addWidget(second_part, stretch=3)
        first_part.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.a_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        second_part.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        t_slider = TSlider()
        main_settings_layout.addWidget(t_slider, stretch=1)
        t_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        f_layout = QHBoxLayout()
        main_settings_layout.addLayout(f_layout, stretch=1)
        f_text = QLabel('f(x, t) = ')
        self.f_function = QLineEdit()
        self.f_function.setPlaceholderText('0')
        self.f_function.textChanged.connect(self.refresh)
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
        self.left_constraint_choose.constraintType.connect(self.refresh)
        self.left_constraint_choose.constraintType.connect(self.refresh_left_constraint)
        left_x0_pararameter_layout = QHBoxLayout()
        left_x0_pararameter_text = QLabel('x0 = ')
        self.left_x0_parameter = QLineEdit('0')
        self.left_x0_parameter.setPlaceholderText('Enter the x0 if you choose U|x=x0 = 0 or Ux|x=x0 = 0')
        self.left_x0_parameter.textChanged.connect(self.refresh)
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
        self.right_constraint_choose.constraintType.connect(self.refresh)
        self.right_constraint_choose.constraintType.connect(self.refresh_right_constraint)
        right_x0_pararameter_layout = QHBoxLayout()
        right_x0_pararameter_text = QLabel('x0 = ')
        self.right_x0_parameter = QLineEdit('0')
        self.right_x0_parameter.setPlaceholderText('Enter the x0 if you choose U|x=x0 = 0 or Ux|x=x0 = 0')
        self.right_x0_parameter.textChanged.connect(self.refresh)
        self.right_x0_parameter.setEnabled(False)
        right_x0_pararameter_layout.addWidget(right_x0_pararameter_text, stretch=1)
        right_x0_pararameter_layout.addWidget(self.right_x0_parameter, stretch=4)
        self.right_constraint_choose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_x0_pararameter_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_x0_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_constraint_layout.addWidget(self.right_constraint_choose)
        right_constraint_layout.addLayout(right_x0_pararameter_layout)

        constraint_layout.addLayout(right_constraint_layout, stretch=1)
        constraint_layout.addLayout(right_constraint_layout, stretch=1)



        self.
        self.setLayout(main_layout)
        self.plot()


    def refresh(self) -> None:
        left_constraint_type = self.left_constraint_choose.getType()
        right_constraint_type = self.right_constraint_choose.getType()
        left_constraint_x0 = float(self.left_x0_parameter.text().replace(',', '.'))
        right_constraint_x0 = float(self.right_x0_parameter.text().replace(',', '.'))
        assert right_constraint_x0 > left_constraint_x0


    def refresh_left_constraint(self) -> None:
        self.left_x0_parameter.setEnabled('none' != self.left_constraint_choose.getType())

    def refresh_right_constraint(self) -> None:
        self.right_x0_parameter.setEnabled('none' != self.right_constraint_choose.getType())

    def refresh_input_plots(self, left: str, right: str, upper: str, bottom: str, function_name: str, plot: plt.Figure) -> None:
        left = float(left.replace(',', '.'))
        right = float(right.replace(',', '.'))    
        upper = float(upper.replace(',', '.'))
        bottom = float(bottom.replace(',', '.'))
        assert function_name in self.input_plots.keys()
        self.input_plots[] = PlotInput(figure=plot, xlim=[left, right], ylim=[bottom, upper])
        changeable_plot.finishedDrawing.connect(self.refresh)


    def plot(self):
        self.statistic_in_spheres.clear()
        self.statistic_of_programms.clear()

        ax1 = self.statistic_in_spheres.add_subplot(111)
        ax2 = self.statistic_of_programms.add_subplot(111)


        time_in_sphere = {bar: sum(data[1] / 3600 for data in log.logs.values() if data[0] == bar) for bar in BARS}

        ax1.barh(list(time_in_sphere.keys()), list(time_in_sphere.values()), align='center', alpha=0.4, color=BAR1_COLORS)
        ax1.plot([NORM_SCHEDULE[str(date.today().weekday())][bar] / 60 for bar in list(time_in_sphere.keys())], list(time_in_sphere.keys()), marker='D', linestyle='none', alpha=0.8, color='red')
        #TODO make a plot-marker for changeable markers. Firstly I'll need to make a function, that will count those markers
        if CONSUMPTION_RECALCULATOR:
            recalculated_norm_list = [(NORM_SCHEDULE[str(date.today().weekday())][bar] - self.recalculated_norm[bar]['sum']) \
                for bar in list(time_in_sphere.keys())]
            recalculated_norm_list = [num / 60 if num > 0 else 0 for num in recalculated_norm_list]
            ax1.plot(recalculated_norm_list, list(time_in_sphere.keys()), marker='D', linestyle='none', alpha=0.8, color='green')

        ax1.set_xlabel('Hours spent')
        ax1.set_title('The activity in thr monitored categories')


        top_programms, bar_labels, time, bar_colors = [], [], [], []
        for i in range(10):
            try:
                values = list(log.logs.values())[i]
                top_programms.append(list(log.logs.keys())[i].strip())
                if values[0] not in bar_labels: 
                    bar_labels.append(values[0].strip())
                else:
                    bar_labels.append('_' + values[0].strip())
                time.append(int(values[1]) / 3600)
                bar_colors.append(self.color_data[values[0].strip()])
            except IndexError:
                break
        ax2.bar(top_programms, time, label=bar_labels, color=bar_colors)
        ax2.set_ylabel('')
        ax2.set_title('')
        ax2.legend(title='Type of the programm')


        #ax3 changing? Is it better to make Simple QLables with data instead of making plot?


        self.statistic_in_spheres_canvas.draw()
        self.statistic_of_programms_canvas.draw()
