from qfluentwidgets import LineEdit, PasswordLineEdit, SettingCard, ComboBox

class LineEditSettingCard(SettingCard):
    """A SettingCard with a QLineEdit on the right."""

    def __init__(self, icon, title, content, placeholder="", password=False, parent=None):
        super().__init__(icon, title, content, parent)
        if password:
            self.line_edit = PasswordLineEdit(self)
        else:
            self.line_edit = LineEdit(self)
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setFixedWidth(220)
        self.hBoxLayout.addWidget(self.line_edit)
        self.hBoxLayout.addSpacing(20)

    @property
    def text(self) -> str:
        return self.line_edit.text()

    @text.setter
    def text(self, value: str):
        self.line_edit.setText(value)


class ComboBoxSettingCard(SettingCard):
    """A SettingCard with a ComboBox on the right."""

    def __init__(self, icon, title, content, items: list[str] | None = None, parent=None):
        super().__init__(icon, title, content, parent)
        self.combo_box = ComboBox(self)
        if items:
            self.combo_box.addItems(items)
        self.combo_box.setFixedWidth(220)
        self.hBoxLayout.addWidget(self.combo_box)
        self.hBoxLayout.addSpacing(20)

    @property
    def currentText(self) -> str:
        return self.combo_box.currentText()

    @currentText.setter
    def currentText(self, value: str):
        self.combo_box.setCurrentText(value)