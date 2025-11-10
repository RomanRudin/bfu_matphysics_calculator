from __future__ import annotations
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QLineEdit
import matplotlib.pyplot as plt
import numpy as np
from src.plots import WavePlot, SinglePlot, ResultPlot, PlotInput
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from src.datastructures import Range, Segment, Plot
from src.widgets import Limiters, RadioButtons, TSlider, MAX_T




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
        self.resulting_plots = {
            'resulting φ(x)': None, 
            'resulting Ф(x)': None,
            'resulting f(x)': None
        }

        self.initial_plots_data = {
            'φ(x)': None,
            'ψ(x)': None,
            'Ф(x)': None,
            'f(x)': None
        }

        self.resulting_plots_data = {
            'resulting φ(x)': None,
            'resulting Ф(x)': None,
            'resulting f(x)': None
        }

        settings_layout = QVBoxLayout()
        main_layout.addLayout(settings_layout, stretch=1)

        functions_settings_layout = QVBoxLayout()
        settings_layout.addLayout(functions_settings_layout, stretch=70)

        self.functions_limiter = Limiters(self.input_limiter_refreshed)
        functions_settings_layout.addWidget(self.functions_limiter, stretch=1)

        phi_layout = QVBoxLayout()
        phi_text_layout = QHBoxLayout()
        phi_text = QLabel('U|t=0 = ϕ(x) = ')
        self.phi_parameter = QLineEdit()
        self.phi_parameter.setPlaceholderText('Enter the ϕ(x) or draw it manually in the plot')  
        # self.phi_parameter.setEnabled(False) #?
        phi_text_layout.addWidget(phi_text, stretch=1)
        phi_text_layout.addWidget(self.phi_parameter, stretch=5)
        self.phi_input_plot_figure = plt.figure()
        self.phi_input_plot_figure_canvas = FigureCanvasQTAgg(self.phi_input_plot_figure)
        phi_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.phi_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.phi_input_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        phi_layout.addLayout(phi_text_layout, stretch=1)
        phi_layout.addWidget(self.phi_input_plot_figure_canvas, stretch=12)

        psi_layout = QVBoxLayout()
        psi_text_layout = QHBoxLayout()
        psi_text = QLabel('Ut|t=0 = ψ(x) = ')
        self.psi_parameter = QLineEdit()
        self.psi_parameter.setPlaceholderText('Enter the ψ(x) or draw it manually in the plot')  
        # self.psi_parameter.setEnabled(False) #?
        psi_text_layout.addWidget(psi_text, stretch=1)
        psi_text_layout.addWidget(self.psi_parameter, stretch=5)
        self.psi_input_plot_figure = plt.figure()
        self.psi_input_plot_figure_canvas = FigureCanvasQTAgg(self.psi_input_plot_figure)
        psi_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_parameter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.psi_input_plot_figure_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        psi_layout.addLayout(psi_text_layout, stretch=1)
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
        # self.a_parameter.editingFinished.connect(lambda _: self.refresh(self.a_parameter.text()))
        self.a_parameter.editingFinished.connect(self.refresh_resulting_plots)
        second_part = QLabel('Uxx + ')
        self.f_function = QLineEdit('0')
        self.f_function.setEnabled(False) #! TODOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
        self.f_function.editingFinished.connect(self.refresh_resulting_plots)
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
        self.left_x0_parameter = QLineEdit(str(self.functions_limiter.get_limiters().x0))
        self.left_x0_parameter.setPlaceholderText('Enter the x0 if you choose U|x=x0 = 0 or Ux|x=x0 = 0')
        self.left_x0_parameter.editingFinished.connect(self.refresh_initial_plots)
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
        self.right_constraint_choose.constraintType.connect(self.refresh_right_constraint)
        right_x0_pararameter_layout = QHBoxLayout()
        right_x0_pararameter_text = QLabel('x0 = ')
        self.right_x0_parameter = QLineEdit(str(self.functions_limiter.get_limiters().x1))
        self.right_x0_parameter.setPlaceholderText('Enter the x0 if you choose U|x=x0 = 0 or Ux|x=x0 = 0')
        self.right_x0_parameter.editingFinished.connect(self.refresh_initial_plots)
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


        # Resulting plots limiters
        self.resulting_functions_limiter = Limiters(self.refresh_initial_plots)
        settings_layout.addWidget(self.resulting_functions_limiter, stretch=1)


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

        self.refresh_slider()
        self.refresh_input_plots()

        self.function_parameters = {
            'φ(x)': self.phi_parameter,
            'ψ(x)': self.psi_parameter
        } 

        self.phi_parameter.editingFinished.connect(self.draw_initial_plot('φ(x)', self.phi_parameter, self.phi_input_plot_figure, self.phi_input_plot_figure_canvas), self.changeAccessInputPlot())
        self.psi_parameter.editingFinished.connect(self.draw_initial_plot('φ(x)', self.psi_parameter.text(), self.psi_initial_plot_figure, self.psi_initial_plot_figure_canvas), self.changeAccessInputPlot())

        self.setLayout(main_layout)



    def refresh_slider(self) -> None:
        self.t_slider_figure.clear()
        ax = self.t_slider_figure.add_subplot(111)
        self.t_slider = TSlider(ax)
        self.t_slider.valueChanged.connect(self.refresh_resulting_plots)

        
    def draw_initial_plot(self, function_name: str, function: QLabel, figure: plt.Figure, canvas: FigureCanvasQTAgg) -> None:
        assert function_name in self.input_plots.keys()
        figure.clear()
        ax = figure.add_subplot(111)
        max_range = self.functions_limiter.get_limiters(resulting=True)
        x = np.linspace(max_range.x0, max_range.x1, int((max_range.x1 - max_range.x0) * 250))
        evaluation = ['0'] * len(x)
        if function.text():
            evaluation = [function.text().replace('x', str(dot)) for dot in x]
        y = [eval(evaluation[dot]) for dot in range(len(x))]
        self.input_plots[function_name], = ax.plot(x, y)
        self.refresh_initial_plots()
        canvas.draw()


    def input_limiter_refreshed(self) -> None:
        plot_range = self.functions_limiter.get_limiters()
        self.resulting_functions_limiter.refresh(plot_range)
        self.left_x0_parameter.setText(str(plot_range.x0))
        self.right_x0_parameter.setText(str(plot_range.x1))
        self.refresh_input_plots()



    def refresh_input_plots(self) -> None:
        plot_range = self.functions_limiter.get_limiters()
        self.phi_input_plot_figure.clear()
        self.psi_input_plot_figure.clear()
        self.input_plots['φ(x)'] = PlotInput(figure=self.phi_input_plot_figure, canvas=self.phi_input_plot_figure_canvas, range=plot_range, initial_plot=self.initial_plots_data['φ(x)'])
        self.input_plots['φ(x)'].finishedDrawing.connect(self.refresh_initial_plots)
        self.input_plots['ψ(x)'] = PlotInput(figure=self.psi_input_plot_figure, canvas=self.psi_input_plot_figure_canvas, range=plot_range, initial_plot=self.initial_plots_data['ψ(x)'])
        self.input_plots['ψ(x)'].finishedDrawing.connect(self.refresh_initial_plots)
        self.refresh_initial_plots()


    def refresh_left_constraint(self) -> None:
        self.left_x0_parameter.setEnabled(self.left_constraint_choose.getType() != 'none')
        self.refresh_initial_plots()


    def refresh_right_constraint(self) -> None:
        self.right_x0_parameter.setEnabled('none' != self.right_constraint_choose.getType())
        self.refresh_initial_plots()

    def refresh_initial_plots(self) -> None:
        self.phi_initial_plot_figure.clear()
        self.psi_initial_plot_figure.clear()

        plot_range = self.resulting_functions_limiter.get_limiters()

        left_constraint_type = self.left_constraint_choose.getType()
        right_constraint_type = self.right_constraint_choose.getType()
        left_constraint_x0 = float(self.left_x0_parameter.text().replace(',', '.'))
        right_constraint_x0 = float(self.right_x0_parameter.text().replace(',', '.'))
        assert right_constraint_x0 > left_constraint_x0 #TODO

        for function_name in ['φ(x)', 'ψ(x)']:
            if not self.function_parameters[function_name].text():
                self.initial_plots_data[function_name] = self.input_plots[function_name].get_plot()
            else:
                self.initial_plots_data[function_name] = 

        if left_constraint_type != 'none':
            for function_name in ['φ(x)', 'ψ(x)']:
                self.initial_plots_data[function_name] = self._extend_plot(self.initial_plots_data[function_name], left_constraint_type, left_constraint_x0, 'left')
        if right_constraint_type != 'none':
            for function_name in ['φ(x)', 'ψ(x)']:
                self.initial_plots_data[function_name] = self._extend_plot(self.initial_plots_data[function_name], right_constraint_type, right_constraint_x0, 'right')
        if left_constraint_type != 'none' and right_constraint_type != 'none':
            for _ in range(2):
                for function_name in ['φ(x)', 'ψ(x)']:
                    self.initial_plots_data[function_name] = self._extend_plot(self.initial_plots_data[function_name], left_constraint_type, left_constraint_x0, 'left')
                for function_name in ['φ(x)', 'ψ(x)']:
                    self.initial_plots_data[function_name] = self._extend_plot(self.initial_plots_data[function_name], right_constraint_type, right_constraint_x0, 'right')

        SinglePlot(self.phi_initial_plot_figure, self.phi_initial_plot_figure_canvas, self.initial_plots_data['φ(x)'], plot_range, 'Initial φ(x)', colors=['orange'])
        self.initial_plots_data['Ф(x)'] = SinglePlot(self.psi_initial_plot_figure, self.psi_initial_plot_figure_canvas, self.initial_plots_data['ψ(x)'], plot_range, 'Initial ψ(x), Ф(x)', lambda plot: plot.integrate(), colors=['black', 'blue']).get_plots()[1]

        self.initialize_resulting_plots()


    def _extend_plot(self, plot: Plot, constraint_type: str, constraint_x0: float, side: str) -> Plot:
        if constraint_type == 'none' or plot is None:
            return plot
        reflected_segments = []
        if constraint_x0 < plot.start:
            start, function = plot.start, plot(plot.start)
            plot.segments.insert(0, Segment(constraint_x0, start, lambda _: function)) 
        if constraint_x0 > plot.end:
            end, function = plot.end, plot(plot.end)
            plot.segments.append(Segment(end, constraint_x0, lambda _: function))

        if side == 'left':
            for segment in plot.segments:
                if segment.x1 <= constraint_x0:
                    continue
                if segment.x0 < constraint_x0 < segment.x1:
                    segment = Segment(constraint_x0, segment.x1, segment.function)

                reflected_x0 = 2 * constraint_x0 - segment.x1
                reflected_x1 = 2 * constraint_x0 - segment.x0

                if constraint_type == 'even':
                    reflected_function = lambda x, seg=segment, cx0=constraint_x0: seg(2 * cx0 - x)
                else:  # 'odd'
                    reflected_function = lambda x, seg=segment, cx0=constraint_x0: -seg(2 * cx0 - x)

                reflected_segment = Segment(reflected_x0, reflected_x1, reflected_function)
                reflected_segments.append(reflected_segment)

            cut_input_segments = [segment for segment in plot.segments if segment.x1 > constraint_x0] 
            if cut_input_segments[0].x0 < constraint_x0:
                cut_input_segments[0].x0 = constraint_x0

            all_segments = sorted(reflected_segments + cut_input_segments, key=lambda segment: segment.x0)

            return Plot(all_segments)

        for segment in plot.segments:
            if segment.x0 >= constraint_x0:
                continue
            if segment.x0 < constraint_x0 < segment.x1:
                segment = Segment(segment.x0, constraint_x0, segment.function)
            reflected_x0 = 2 * constraint_x0 - segment.x1
            reflected_x1 = 2 * constraint_x0 - segment.x0

            if constraint_type == 'even':
                reflected_function = lambda x, seg=segment, cx0=constraint_x0: seg(2 * cx0 - x)
            else:  # 'odd'
                reflected_function = lambda x, seg=segment, cx0=constraint_x0: -seg(2 * cx0 - x)

            reflected_segment = Segment(reflected_x0, reflected_x1, reflected_function)
            reflected_segments.append(reflected_segment)

        cut_input_segments = [segment for segment in plot.segments if segment.x0 < constraint_x0] 
        if cut_input_segments[-1].x1 > constraint_x0:
            cut_input_segments[-1].x1 = constraint_x0
        all_segments = sorted(reflected_segments + cut_input_segments, key=lambda segment: segment.x0)
        return Plot(all_segments)

    
    def initialize_resulting_plots(self) -> None:
        self.phi_plot_figure.clear()
        self.psi_plot_figure.clear()
        self.f_plot_figure.clear()
        self.result_plot_figure.clear()

        self.resulting_plots['resulting φ(x)'] = WavePlot(self.phi_plot_figure, self.phi_plot_figure_canvas, \
                self.initial_plots_data['φ(x)'], 'Resulting φ(x)', lambda plot1, plot2, a: 1/2 * (plot1 + plot2), colors=['red', 'yellow', 'orange'])
        self.resulting_plots['resulting Ф(x)'] = WavePlot(self.psi_plot_figure, self.psi_plot_figure_canvas, \
                self.initial_plots_data['Ф(x)'], 'Resulting Фx)', lambda plot1, plot2, a: (1/(2 * a)) * (plot2 - plot1), colors=['violet', 'cyan', 'blue'])
        # self.resulting_plots['resulting f(x, t)'] = WavePlot(self.f_plot_figure,     self.f_plot_figure_canvas, \
        #         self.initial_plots_data['f(x)'], 'Resulting f(x, t)', lambda plot1, plot2: plot1 - plot2, colors=['blue', 'red', 'green']).get_plots()[2]
        self.refresh_resulting_plots()

    def refresh_resulting_plots(self) -> None:
        self.result_plot_figure.clear()

        plot_range = self.resulting_functions_limiter.get_limiters()
        a = float(self.a_parameter.text().replace(',', '.'))
        assert a > 0
        a = a ** 0.5
        t = self.t_slider.val()

        for function_name in ['φ(x)', 'Ф(x)']:
            self.resulting_plots[f'resulting {function_name}'].refresh(a, t, plot_range)
            self.resulting_plots_data[f'resulting {function_name}'] = self.resulting_plots[f'resulting {function_name}'].get_plots()[2]
        ResultPlot(self.result_plot_figure, self.result_plot_figure_canvas, \
                self.resulting_plots_data['resulting φ(x)'], self.resulting_plots_data['resulting Ф(x)'], 
                plot_range, 'Result', lambda plot1, plot2: plot1 + plot2, colors=['orange', 'blue', 'green'])
        

    def changeAccessInputPlot(self):
        for key, plot in self.input_plots.items():
            if self.function_parameters[key].text():
                plot.setEnabled(False)
            else:
                plot.setEnabled(True)