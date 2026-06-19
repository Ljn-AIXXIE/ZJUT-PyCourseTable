from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QFrame
)

from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    FluentIcon,
    ScrollArea
)

from app.ui.styles import SettingsSectionHeaderStyle
from app.ui.controls import LineEditSettingCard, ComboBoxSettingCard
from app.settings import get as get_settings

class SettingsWidget(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        s = get_settings()

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.viewport().setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(24)
        
        student_id_card = LineEditSettingCard(FluentIcon.PEOPLE, "学号", "统一身份认证学号", placeholder="请输入学号")
        student_id_card.text = s.value("studentId")
        student_id_card.line_edit.editingFinished.connect(lambda: s.setValue("studentId", student_id_card.text))

        password_card = LineEditSettingCard(FluentIcon.HIDE, "密码", "统一身份认证密码", placeholder="请输入密码", password=True)
        password_card.text = s.value("password")
        password_card.line_edit.editingFinished.connect(lambda: s.setValue("password", password_card.text))

        auth_group = SettingCardGroup("统一身份认证设置", container)
        SettingsSectionHeaderStyle(auth_group)
        auth_group.addSettingCard(student_id_card)
        auth_group.addSettingCard(password_card)
        layout.addWidget(auth_group)
        
        show_weekend_card = SwitchSettingCard(FluentIcon.CALENDAR, "显示周末课表", "在课表中显示周六和周日的课程")
        show_weekend_card.switchButton.setChecked(s.value("showWeekendCourses") == "true")
        show_weekend_card.switchButton.checkedChanged.connect(lambda v: s.setValue("showWeekendCourses", "true" if v else "false"))

        auto_refresh_card = SwitchSettingCard(FluentIcon.SYNC, "自动刷新课表", "每次打开应用时自动从教务系统刷新课表数据")
        auto_refresh_card.switchButton.setChecked(s.value("autoRefresh") == "true")
        auto_refresh_card.switchButton.checkedChanged.connect(lambda v: s.setValue("autoRefresh", "true" if v else "false"))
        
        light_block_card = SwitchSettingCard(FluentIcon.PALETTE, "使用浅色块", "课程块使用浅色背景代替纯色填充")
        light_block_card.switchButton.setChecked(s.value("enableLightBlock") == "true")
        light_block_card.switchButton.checkedChanged.connect(lambda v: s.setValue("enableLightBlock", "true" if v else "false"))

        course_group = SettingCardGroup("课表设置", container)
        SettingsSectionHeaderStyle(course_group)
        course_group.addSettingCard(show_weekend_card)
        course_group.addSettingCard(auto_refresh_card)
        course_group.addSettingCard(light_block_card)
        layout.addWidget(course_group)

        ac_year_card = LineEditSettingCard(FluentIcon.EDUCATION, "学年", "当前学年", placeholder="请输入学年，如 2026")
        ac_year_card.text = s.value("acYear")
        ac_year_card.line_edit.setValidator(QIntValidator(2000, 2099))
        ac_year_card.line_edit.editingFinished.connect(lambda: s.setValue("acYear", ac_year_card.text))

        ac_term_card = ComboBoxSettingCard(FluentIcon.EDUCATION, "学期", "当前学期", items=["1", "2", "3"])
        ac_term_card.currentText = s.value("acTerm")
        ac_term_card.combo_box.currentTextChanged.connect(lambda v: s.setValue("acTerm", v))

        ac_period_group = SettingCardGroup("教务设置", container)
        SettingsSectionHeaderStyle(ac_period_group)
        ac_period_group.addSettingCard(ac_year_card)
        ac_period_group.addSettingCard(ac_term_card)
        layout.addWidget(ac_period_group)

        layout.addStretch()
