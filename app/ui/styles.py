from PyQt6.QtGui import QFont

from qfluentwidgets import SettingCardGroup


def SettingsSectionHeaderStyle(group: SettingCardGroup):
    label = group.titleLabel
    font = QFont()
    font.setPixelSize(14)
    font.setWeight(QFont.Weight.DemiBold)
    label.setFont(font)
    label.setContentsMargins(1, 0, 0, 6)
