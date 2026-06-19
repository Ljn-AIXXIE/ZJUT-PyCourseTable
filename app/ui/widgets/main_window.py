from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition

from app.ui.widgets.table_widget import CourseTableWidget
from app.ui.widgets.settings_widget import SettingsWidget
from app.ui.widgets.course_detail_dialog import CourseDetailDialog

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyCourseTable")
        self.setMinimumSize(960, 675)
        self.titleBar.maxBtn.hide()

        table_widget = CourseTableWidget()
        table_widget.setObjectName("courseTable")
        table_widget.course_clicked.connect(self._on_course_clicked)

        settings_widget = SettingsWidget()
        settings_widget.setObjectName("settings")

        self.addSubInterface(table_widget, FluentIcon.CALENDAR, "课表")
        self.addSubInterface(settings_widget, FluentIcon.SETTING, "设置", position=NavigationItemPosition.BOTTOM)

        self.navigationInterface.panel.setExpandWidth(260)
        self.navigationInterface.panel.setMinimumExpandWidth(600)
        self.navigationInterface.panel.expand()
    
    def _on_course_clicked(self, course):
        dlg = CourseDetailDialog(course, self)
        dlg.exec()
