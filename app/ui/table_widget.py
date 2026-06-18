from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QScrollArea, QHBoxLayout, QVBoxLayout,
    QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from app.account.account import Account
from app.models.course import (
    CourseModel, CourseTableModel, CourseGraphicObject,
    create_course_graphics_of_day, BASE_HEIGHT
)
from app.utils import get_settings
import app.api as api

DAYS_IN_WEEK = ["一", "二", "三", "四", "五", "六", "日"]


class _CourseBlock(QFrame):
    clicked = pyqtSignal(CourseModel)

    def __init__(self, graphic: CourseGraphicObject):
        super().__init__()
        self._course = graphic.course_data
        self.setFixedHeight(graphic.height)
        self.setCursor(Qt.CursorShape.PointingHandCursor if graphic.has_course else Qt.CursorShape.ArrowCursor)

        if not graphic.has_course:
            self.setStyleSheet("background: transparent;")
            return

        r, g, b, a = graphic.color.getRgb()
        self.setStyleSheet(
            f"background: rgba({r},{g},{b},200); "
            f"border: 1px solid rgba({r},{g},{b},255); "
            f"border-radius: 8px;"
        )

        inner = QVBoxLayout(self)
        inner.setContentsMargins(4, 4, 4, 4)
        inner.setSpacing(4)

        place_label = QLabel(graphic.place if graphic.place else "")
        place_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        place_label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: 600; border: none; background: transparent;"
        )
        inner.addWidget(place_label)

        inner.addStretch()

        name_label = QLabel(graphic.course_name if graphic.course_name else "")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet(
            "color: white; font-size: 14px; font-weight: 600; border: none; background: transparent;"
        )
        inner.addWidget(name_label)

    def mousePressEvent(self, event):
        if self._course:
            self.clicked.emit(self._course)
        super().mousePressEvent(event)


class _DayColumn(QWidget):
    block_clicked = pyqtSignal(CourseModel)

    def __init__(self, day_index: int, table: CourseTableModel, color_dict: dict, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(48)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(8)

        graphics = create_course_graphics_of_day(day_index + 1, table, color_dict)
        for g in graphics:
            block = _CourseBlock(g)
            if g.has_course:
                block.clicked.connect(self.block_clicked.emit)
            layout.addWidget(block)

        layout.addStretch()


class CourseTableWidget(QWidget):
    course_clicked = pyqtSignal(CourseModel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = get_settings()
        self._color_dict: dict[str, QColor] = {}
        self._table: CourseTableModel | None = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.viewport().setStyleSheet("background: transparent;")

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QHBoxLayout(self._grid_container)
        self._grid_layout.setContentsMargins(2, 0, 2, 0)
        self._grid_layout.setSpacing(2)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._grid_container)
        root.addWidget(self._scroll, 1)
        
        self._footer = QWidget()
        footer_layout = QHBoxLayout(self._footer)
        footer_layout.setContentsMargins(0, 8, 0, 0)

        self._week_label = QLabel()

        self._last_refresh_label = QLabel()
        self._last_refresh_label.setStyleSheet("color: gray; font-size: 14px;")

        self._refresh_btn = QPushButton("刷新课表")
        self._refresh_btn.clicked.connect(self.on_refresh_btn_click)

        footer_layout.addWidget(self._refresh_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self._week_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self._last_refresh_label)

        root.addWidget(self._footer)

    @property
    def refresh_button(self) -> QPushButton:
        return self._refresh_btn
    
    def on_refresh_btn_click(self):
        import traceback
        try:
            account: Account = Account.from_file('my_account.json')
            if api.run(account):
                self.set_table(CourseTableModel.from_dict(account['course_inf']))
        except Exception:
            traceback.print_exc()

    def set_table(self, table: CourseTableModel):
        self._table = table
        self._color_dict.clear()
        self._rebuild_grid()

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                CourseTableWidget._clear_layout(item.layout())
            if item.widget():
                item.widget().deleteLater()

    def light_block_mode(self) -> bool:
        return self._settings.value("enableLightBlock", "false") == "true"

    def _rebuild_grid(self):
        if self._table is None:
            return

        show_weekend = self._settings.value("showWeekendCourses", "true") == "true"
        end_day = 7 if show_weekend else 5

        # clear
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.layout():
                self._clear_layout(item.layout())
            if item.widget():
                item.widget().deleteLater()
        
        for i in range(end_day):
            day_wrapper = QVBoxLayout()
            day_wrapper.setContentsMargins(0, 0, 0, 0)
            day_wrapper.setSpacing(16)

            lbl = QLabel(DAYS_IN_WEEK[i])
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: gray; font-size: 12px;")
            lbl.setMinimumWidth(48)
            day_wrapper.addWidget(lbl)

            col = _DayColumn(i, self._table, self._color_dict)
            col.block_clicked.connect(self.course_clicked.emit)
            day_wrapper.addWidget(col)

            self._grid_layout.addLayout(day_wrapper)

        # footer
        self._week_label.setText(f"第 {self._table.week_time} 周")
        self._week_label.setStyleSheet("color: gray; font-size: 14px;")
        date_range = f"{self._table.begin_date} 至 {self._table.end_date}"
        self._last_refresh_label.setText(date_range)

        self._grid_container.updateGeometry()
