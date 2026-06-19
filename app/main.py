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

    import traceback
    try:
        from app.account.account import Account
        from app.models.course import CourseTableModel
        account: Account = Account.from_file('my_account.json')

        window.table_widget.set_table(CourseTableModel.from_dict(account['course_inf']))
    except Exception:
        traceback.print_exc()

    window.show()

    with qasync.QEventLoop(app) as loop:
        loop.run_forever()

if __name__ == "__main__":
    main()