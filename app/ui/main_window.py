from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition

from app.ui.table_widget import CourseTableWidget
from app.ui.settings_widget import SettingsWidget
from app.ui.course_detail_dialog import CourseDetailDialog


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCourseTable")
        self.setFixedSize(960, 660)
        self.setResizeEnabled(False)
        self.titleBar.maxBtn.hide()

        self._table_widget = CourseTableWidget()
        self._table_widget.setObjectName("courseTable")
        self._table_widget.course_clicked.connect(self._on_course_clicked)

        self._settings_widget = SettingsWidget()
        self._settings_widget.setObjectName("settings")

        self.addSubInterface(
            self._table_widget,
            FluentIcon.CALENDAR,
            "课表"
        )
        self.addSubInterface(
            self._settings_widget,
            FluentIcon.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.panel.setExpandWidth(260)
        self.navigationInterface.panel.setMinimumExpandWidth(600)
        self.navigationInterface.panel.expand()
        self.stackedWidget.currentChanged.connect(self._on_page_changed)

    def _on_page_changed(self, index: int):
        widget = self.stackedWidget.widget(index)
        if widget is self._table_widget:
            self._settings_widget.save()
            self._table_widget._rebuild_grid()

    def _on_course_clicked(self, course):
        dlg = CourseDetailDialog(course, self)
        dlg.exec()

    @property
    def table_widget(self) -> CourseTableWidget:
        return self._table_widget

    @property
    def settings_widget(self) -> SettingsWidget:
        return self._settings_widget
