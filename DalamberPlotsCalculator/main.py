from window import Window
from sys import argv, exit
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    # try:
        app = QApplication([argv]) 
        # app.setStyleSheet(stylesheet_main)
        main = Window()
        main.resize(1200, 800)
        main.show()        
        exit(app.exec_())
    # except Exception as e:
    #     with open('debug_log.txt', 'w') as file:
    #         file.write(str(e))