from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QWidget, QFrame

from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    FluentIcon,
)

from app.ui.styles import SettingsSectionHeaderStyle
from app.ui.control.line_edit_setting_card import LineEditSettingCard
from app.utils import get_settings

class SettingsWidget(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = get_settings()

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.viewport().setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(24)
        
        auth_group = SettingCardGroup("统一身份认证设置", container)
        SettingsSectionHeaderStyle(auth_group)
        self.export_student_id_card = LineEditSettingCard(
            FluentIcon.PEOPLE,
            "学号",
            "统一身份认证学号",
            placeholder="请输入学号"
        )
        auth_group.addSettingCard(self.export_student_id_card)

        self.export_password_card = LineEditSettingCard(
            FluentIcon.HIDE,
            "密码",
            "统一身份认证密码",
            placeholder="请输入密码",
            password=True
        )
        auth_group.addSettingCard(self.export_password_card)

        layout.addWidget(auth_group)
        
        course_group = SettingCardGroup("课表设置", container)
        SettingsSectionHeaderStyle(course_group)

        self.show_weekend_card = SwitchSettingCard(
            FluentIcon.CALENDAR,
            "显示周末课表",
            "在课表中显示周六和周日的课程",
        )
        course_group.addSettingCard(self.show_weekend_card)

        self.auto_refresh_card = SwitchSettingCard(
            FluentIcon.SYNC,
            "自动刷新课表",
            "每次打开应用时自动从教务系统刷新课表数据",
        )
        course_group.addSettingCard(self.auto_refresh_card)

        self.light_block_card = SwitchSettingCard(
            FluentIcon.PALETTE,
            "使用浅色块",
            "课程块使用浅色背景代替纯色填充",
        )
        course_group.addSettingCard(self.light_block_card)

        layout.addWidget(course_group)
        
        layout.addStretch()

        self.load()

    def load(self):
        self.export_student_id_card.text = self._settings.value("studentId", "")
        self.export_password_card.text = self._settings.value("password", "")
        self.show_weekend_card.switchButton.setChecked(
            self._settings.value("showWeekendCourses", "true") == "true"
        )
        self.auto_refresh_card.switchButton.setChecked(
            self._settings.value("autoRefresh", "true") == "true"
        )
        self.light_block_card.switchButton.setChecked(
            self._settings.value("enableLightBlock", "false") == "true"
        )

    def save(self):
        self._settings.setValue("studentId", self.export_student_id_card.text)
        self._settings.setValue("password", self.export_password_card.text)

        from app.account.account import Account
        account: Account = Account.from_file('my_account.json')
        account._studentId = self.export_student_id_card.text
        account._password = self.export_password_card.text
        account.to_json()

        self._settings.setValue(
            "showWeekendCourses",
            "true" if self.show_weekend_card.switchButton.isChecked() else "false",
        )
        self._settings.setValue(
            "autoRefresh",
            "true" if self.auto_refresh_card.switchButton.isChecked() else "false",
        )
        self._settings.setValue(
            "enableLightBlock",
            "true" if self.light_block_card.switchButton.isChecked() else "false",
        )
        self._settings.sync()

    @property
    def student_id(self) -> str:
        return self.export_student_id_card.text

    @property
    def password(self) -> str:
        return self.export_password_card.text

    @property
    def show_weekend_courses(self) -> bool:
        return self.show_weekend_card.switchButton.isChecked()

    @property
    def auto_refresh(self) -> bool:
        return self.auto_refresh_card.switchButton.isChecked()

    @property
    def enable_light_block(self) -> bool:
        return self.light_block_card.switchButton.isChecked()
