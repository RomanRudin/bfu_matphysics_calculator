from window import Window
from sys import argv, exit
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([argv]) 
    # app.setStyleSheet(stylesheet_main)
    main = Window()
    main.resize(1200, 800)
    main.show()        
    exit(app.exec_())