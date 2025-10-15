from __future__ import annotations
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QButtonGroup, QGridLayout, QLabel, QLineEdit, QRadioButton, QSizePolicy
from matplotlib.widgets import Slider
from PyQt5.QtCore import QObject
from plots import Range

STANDART_LIMITERS = Range(-2, 5, 2, -2)
MAX_T = 10


class TSlider(QObject):
    valueChanged = pyqtSignal(int)
    def __init__(self, ax, min_value, max_value, *args, **kwargs) -> None:
        super().__init__()
        self.slider = Slider(ax, 't', min_value, max_value, valinit=0, valstep=0.25, valfmt="%.2f")
        self.slider.on_changed(lambda _: self.on_changed(self.slider.val))

    def on_changed(self, val) -> None:
        self.valueChanged.emit(int(val))

    def val(self) -> float:
        return float(self.slider.val)
    



class Limiters(QWidget):
    limitersChanged = pyqtSignal(float, float, float, float, float)

    def __init__(self, parent: 'Window') -> None:
        super().__init__()
        main_layout = QVBoxLayout()
        limiters_text = QLabel(f'Limiters of plot for functions below:')
        limiters_layout = QGridLayout()

        left_limiter_text, right_limiter_text, upper_limiter_text, bottom_limiter_text = QLabel('Left limiter:'), QLabel('Right limiter:'), QLabel('Upper limiter:'), QLabel('Bottom limiter:')
        self.left_limiter, self.right_limiter, self.bottom_limiter, self.upper_limiter = QLineEdit(str(STANDART_LIMITERS.x0)), QLineEdit(str(STANDART_LIMITERS.x1)), QLineEdit(str(STANDART_LIMITERS.y0)), QLineEdit(str(STANDART_LIMITERS.y1))
        self.left_limiter.editingFinished.connect(parent.refresh_input_plots)
        self.right_limiter.editingFinished.connect(parent.refresh_input_plots)
        self.upper_limiter.editingFinished.connect(parent.refresh_input_plots)
        self.bottom_limiter.editingFinished.connect(parent.refresh_input_plots)
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