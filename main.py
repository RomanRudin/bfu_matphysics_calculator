from src.window import Window
from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

if __name__ == "__main__":
    app = QApplication([argv]) 
    # with open('src\styles\style.qss', 'r', encoding='utf-8') as file:                     
        # app.setStyleSheet(file.read())
    main = Window()
    main.setWindowTitle('Wave equation solver')
    app.setWindowIcon(QIcon(r'src\styles\icon.png'))
    main.show()        
    main.showMaximized()
    exit(app.exec_())