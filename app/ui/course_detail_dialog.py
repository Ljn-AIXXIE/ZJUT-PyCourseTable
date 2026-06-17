from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLabel, QVBoxLayout, QGroupBox
)

from app.models.course import CourseModel


class CourseDetailDialog(QDialog):
    def __init__(self, course: CourseModel, parent=None):
        super().__init__(parent)
        self.setWindowTitle(course.course_name)
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        
        section1 = QGroupBox()
        form1 = QFormLayout(section1)
        form1.addRow("时间", QLabel(f"{course.name_of_day_of_week} {course.time_of_day} 节"))
        form1.addRow("地点", QLabel(f"{course.campus} {course.place}"))
        layout.addWidget(section1)
        
        section2 = QGroupBox()
        form2 = QFormLayout(section2)
        form2.addRow("课程类别", QLabel(course.class_type))
        form2.addRow("学分", QLabel(course.score))
        form2.addRow("总学时", QLabel(course.total_hours))
        layout.addWidget(section2)
        
        section3 = QGroupBox()
        form3 = QFormLayout(section3)
        form3.addRow("教师", QLabel(course.teacher_name))
        form3.addRow("教学班名称", QLabel(course.class_name))
        form3.addRow("教学班组成", QLabel(course.class_composition))
        layout.addWidget(section3)
