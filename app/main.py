import sys
import qasync
from PyQt6.QtWidgets import QApplication

from qfluentwidgets import setTheme, Theme

from app.ui.main_window import MainWindow
from app.utils import apply_system_accent_color

def main():
    app = QApplication(sys.argv)

    setTheme(Theme.AUTO)
    apply_system_accent_color()

    window = MainWindow()

    # TODO: remove after debugging
    from app.models.test_data import create_test_table
    window.table_widget.set_table(create_test_table())

    window.show()

    with qasync.QEventLoop(app) as loop:
        loop.run_forever()

if __name__ == "__main__":
    main()