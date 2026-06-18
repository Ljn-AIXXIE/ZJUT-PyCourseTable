from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from qfluentwidgets import MessageBoxBase

from app.models.course import CourseModel


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    font = QFont()
    font.setPixelSize(14)
    font.setWeight(QFont.Weight.DemiBold)
    lbl.setFont(font)
    lbl.setContentsMargins(0, 8, 0, 2)
    return lbl


def _value_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 13px;")
    lbl.setContentsMargins(8, 0, 0, 0)
    return lbl


class CourseDetailDialog(MessageBoxBase):
    def __init__(self, course: CourseModel, parent=None):
        super().__init__(parent)
        self.setWindowTitle(course.course_name)

        self.cancelButton.hide()
        self.yesButton.setText("确定")

        self.viewLayout.addWidget(_section_label("时间地点"))
        self.viewLayout.addWidget(_value_label(
            f"时间  {course.name_of_day_of_week} {course.time_of_day} 节"
        ))
        self.viewLayout.addWidget(_value_label(
            f"地点  {course.campus} {course.place}"
        ))

        self.viewLayout.addSpacing(8)
        self.viewLayout.addWidget(_section_label("课程信息"))
        self.viewLayout.addWidget(_value_label(f"课程类别  {course.class_type}"))
        self.viewLayout.addWidget(_value_label(f"学分  {course.score}"))
        self.viewLayout.addWidget(_value_label(f"总学时  {course.total_hours}"))

        self.viewLayout.addSpacing(8)
        self.viewLayout.addWidget(_section_label("教师班级"))
        self.viewLayout.addWidget(_value_label(f"教师  {course.teacher_name}"))
        self.viewLayout.addWidget(_value_label(f"教学班名称  {course.class_name}"))
        self.viewLayout.addWidget(_value_label(f"教学班组成  {course.class_composition}"))
