from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition

from app.ui.widgets.table_widget import CourseTableWidget
from app.ui.widgets.exam_widget import ExamWidget
from app.ui.widgets.grade_widget import GradeWidget
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

        exam_widget = ExamWidget()
        exam_widget.setObjectName("examInfo")
        self.addSubInterface(exam_widget, FluentIcon.EDUCATION, "期末考试信息")

        grade_widget = GradeWidget()
        grade_widget.setObjectName("gradeInfo")
        self.addSubInterface(grade_widget, FluentIcon.CERTIFICATE, "期末成绩")

        self.addSubInterface(settings_widget, FluentIcon.SETTING, "设置", position=NavigationItemPosition.BOTTOM)

        self.navigationInterface.panel.setExpandWidth(260)
        self.navigationInterface.panel.setMinimumExpandWidth(600)
        self.navigationInterface.panel.expand()
    
    def _on_course_clicked(self, course):
        dlg = CourseDetailDialog(course, self)
        dlg.exec()
