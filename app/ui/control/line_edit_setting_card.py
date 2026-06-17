from qfluentwidgets import LineEdit, PasswordLineEdit, SettingCard

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
