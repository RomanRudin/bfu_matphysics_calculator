from DalamberPlotsCalculator.window import Window
from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from matplotlib import pyplot as plt

if __name__ == "__main__":
    # # input_mode = int(input("Please, input mode of calculation:"))
    # # match input_mode:
    #     # case 1:
    # figure = plt.figure(constrained_layout=True)
    # spec = figure.add_gridspec(ncols=3, nrows=7, left=0.05, right=0.06, wspace=0.05)

    # phi = PlotInput(figure, "orange", [(0, 0), (1, 1)], spec, [-5, 5], [-2, 2])
    # psi = PlotInput(figure, "violet", [(1, 0), (2, 1)], spec, [-5, 5], [-2, 2])
    # result_phi = ThreePlotsIntermediate(figure, ['yellow', "red", 'orange'], [(0, 1), (1, 2)], spec)
    # result_psi = ThreePlotsIntermediate(figure, ['cyan', "blue", 'violet'], [(1, 1), (2, 2)], spec)
    # result = ThreePlotsFinal(figure, ['orange', 'violet', 'green'], [(0, 2), (1, 3)], spec)
    # t_slider = TSlider([result_phi, result_psi, result])
    # result.init__update()
    #     # case 2:
    #         # figure = plt.figure(constrained_layout=True)
    #         # spec = figure.add_gridspec(ncols=3, nrows=7, left=0.05, right=0.06, wspace=0.05)
    #         # result = DynamicGraphic(figure, "violet", 2, spec)

    #         # wave1 = ChangebleGraphic(figure, "red", 0, spec, result)
    #         # wave2 = ChangebleGraphic(figure, "blue", 1, spec, result)
    #     # case _:
    #         # print("Wrong mode!")
    # plt.show()
    try:
        app = QApplication([argv]) 
        # app.setStyleSheet(stylesheet_main)
        main = Window()
        main.resize(1200, 800)
        main.show()        
        exit(app.exec_())
    except Exception as e:
        with open('debug_log.txt', 'w') as file:
            file.write(str(e))