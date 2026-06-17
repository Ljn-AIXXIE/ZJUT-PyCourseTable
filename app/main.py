import sys
import qasync
from PyQt6.QtWidgets import QApplication

from app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    with qasync.QEventLoop(app) as loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
