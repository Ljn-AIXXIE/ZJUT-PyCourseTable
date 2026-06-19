import asyncio

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)
from qfluentwidgets import (
    InfoBar,
    InfoBarPosition,
    MessageBox,
    FluentIcon,
    TransparentToolButton,
    PushButton,
    ComboBox,
    ScrollArea,
    isDarkTheme,
)

import app.api.interface as api
import app.settings
from app.utils import parse_course_date

from app.models.course import (
    CourseModel,
    CourseTableModel,
    CourseGraphicObject,
    create_course_graphics_of_day
)

DAYS_IN_WEEK = ["一", "二", "三", "四", "五", "六", "日"]

class _CourseBlock(QFrame):
    clicked = pyqtSignal(CourseModel)

    def __init__(self, graphic: CourseGraphicObject, light_mode: bool = False, text_color: str = "white"):
        super().__init__()

        self._course = graphic.course_data
        self.setFixedHeight(graphic.height)
        self.setCursor(Qt.CursorShape.PointingHandCursor if graphic.has_course else Qt.CursorShape.ArrowCursor)

        if not graphic.has_course:
            self.setStyleSheet("background: transparent;")
            return

        r, g, b, _ = graphic.color.getRgb()
        bg_alpha = 64 if light_mode else 200
        self.setStyleSheet(
            f"background: rgba({r},{g},{b},{bg_alpha}); "
            f"border: 1px solid rgba({r},{g},{b},255); "
            f"border-radius: 8px;"
        )

        inner = QVBoxLayout(self)
        inner.setContentsMargins(4, 4, 4, 4)
        inner.setSpacing(4)

        label_style = f"color: {text_color}; font-size: 13px; font-weight: 600; border: none; background: transparent;"

        place_label = QLabel(graphic.place if graphic.place else "")
        place_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        place_label.setStyleSheet(label_style)
        inner.addWidget(place_label)

        inner.addStretch()

        name_label = QLabel(graphic.course_name if graphic.course_name else "")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet(f"color: {text_color}; font-size: 14px; font-weight: 600; border: none; background: transparent;")
        inner.addWidget(name_label)

    def mousePressEvent(self, event):
        if self._course:
            self.clicked.emit(self._course)
        super().mousePressEvent(event)

class _DayColumn(QWidget):
    block_clicked = pyqtSignal(CourseModel)

    def __init__(self, day_index: int, table: CourseTableModel, color_dict: dict, light_mode: bool = False, text_color: str = "white", parent=None):
        super().__init__(parent)
        self.setMinimumWidth(48)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(8)

        graphics = create_course_graphics_of_day(day_index + 1, table, color_dict)
        for g in graphics:
            block = _CourseBlock(g, light_mode, text_color)
            if g.has_course:
                block.clicked.connect(self.block_clicked.emit)
            layout.addWidget(block)

        layout.addStretch()

class CourseTableWidget(QWidget):
    course_clicked = pyqtSignal(CourseModel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._table: CourseTableModel | None = None
        self._first_date: str = ""
        self._color_dict: dict[str, QColor] = {}
        self._build_ui()
        self._init_from_cache()

        if app.settings.get().value("autoRefresh") == "true":
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: asyncio.ensure_future(self._do_auto_refresh()))

    def _build_ui(self):
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)

        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.viewport().setStyleSheet("background: transparent;")

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QHBoxLayout(self._grid_container)
        self._grid_layout.setContentsMargins(2, 0, 2, 0)
        self._grid_layout.setSpacing(2)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self._grid_container)
        root.addWidget(scroll, 1)

        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 8, 0, 0)

        s = app.settings.get()

        self._week_combo = ComboBox()
        self._week_combo.addItems([str(i) for i in range(1, 19)])
        self._week_combo.setCurrentText(s.value("acWeek"))
        self._week_combo.currentTextChanged.connect(self._on_week_changed)

        jump_btn = TransparentToolButton(FluentIcon.CALENDAR, self)
        jump_btn.clicked.connect(self._on_jump_to_current_week)

        self._last_refresh_label = QLabel()
        self._last_refresh_label.setStyleSheet("color: gray; font-size: 14px;")

        refresh_btn = PushButton("刷新课表")
        refresh_btn.clicked.connect(self._on_refresh_clicked)

        footer_layout.addWidget(refresh_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(jump_btn)
        footer_layout.addSpacing(8)
        footer_layout.addWidget(self._week_combo)
        footer_layout.addStretch()
        footer_layout.addWidget(self._last_refresh_label)

        root.addWidget(footer)

    def _init_from_cache(self):
        ok, cache = api.load_cache()
        if ok:
            self._set_table(
                CourseTableModel.from_dict(cache["course_inf"]),
                cache.get("first_date", ""),
            )

    def _on_refresh_clicked(self):
        btn = self.sender()
        asyncio.ensure_future(self._do_refresh(btn))

    async def _do_refresh(self, refresh_btn):
        refresh_btn.setEnabled(False)
        dialog = MessageBox("提示", "正在刷新课表...", self.window())
        dialog.yesButton.setEnabled(False)
        dialog.hideCancelButton()
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.show()

        ok, err = await api.run_async()

        if not ok:
            dialog.contentLabel.setText(err.traceback_str)
            dialog.yesButton.setEnabled(True)
        else:
            dialog.close()
        
        refresh_btn.setEnabled(True)

        if err is not None:
            InfoBar.error(
                title="刷新失败",
                content=str(err),
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self.window(),
            )
            return

        if not ok:
            InfoBar.error(
                title="刷新失败",
                content="登录或获取课表数据失败，请检查学号和密码",
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self.window(),
            )
            return

        ok2, cache = api.load_cache()
        if ok2:
            self._set_table(
                CourseTableModel.from_dict(cache["course_inf"]),
                cache.get("first_date", ""),
            )
            self._rebuild_grid()

    async def _do_auto_refresh(self):
        ok, err = await api.run_async()
        if err is not None:
            InfoBar.error(
                title="自动刷新失败",
                content=str(err),
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self.window(),
            )
            return
        if not ok:
            return
        ok2, cache = api.load_cache()
        if ok2:
            self._set_table(
                CourseTableModel.from_dict(cache["course_inf"]),
                cache.get("first_date", ""),
            )
            if self.isVisible():
                self._rebuild_grid()

    def showEvent(self, event):
        super().showEvent(event)
        self._rebuild_grid()

    def _set_table(self, table: CourseTableModel, first_date: str = ""):
        self._table = table
        self._first_date = first_date
        self._color_dict.clear()

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                CourseTableWidget._clear_layout(item.layout())
            if item.widget():
                item.widget().deleteLater()

    def _on_week_changed(self, text: str):
        app.settings.get().setValue("acWeek", text)
        self._rebuild_grid()

    def _on_jump_to_current_week(self):
        if not self._first_date:
            return
        from datetime import datetime
        first = datetime.strptime(self._first_date, "%Y-%m-%d")
        delta = (datetime.now() - first).days
        if delta < 0:
            return
        week = delta // 7 + 1
        max_week = self._week_combo.count()
        if 1 <= week <= max_week:
            self._week_combo.setCurrentText(str(week))

    def _rebuild_grid(self):
        if self._table is None:
            return

        s = app.settings.get()

        current_week = int(s.value("acWeek") or "1")
        show_weekend = s.value("showWeekendCourses") == "true"
        light_mode = s.value("enableLightBlock") == "true"
        text_color = ("white" if isDarkTheme() else "black") if light_mode else "white"
        end_day = 7 if show_weekend else 5

        week_table = self._table.for_week(current_week)

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

            col = _DayColumn(i, week_table, self._color_dict, light_mode, text_color)
            col.block_clicked.connect(self.course_clicked.emit)
            day_wrapper.addWidget(col)

            self._grid_layout.addLayout(day_wrapper, 1)

        if self._first_date:
            monday = parse_course_date(self._first_date, current_week, 1)
            sunday = parse_course_date(self._first_date, current_week, 7)
            self._last_refresh_label.setText(f"{monday} 至 {sunday}")
        else:
            self._last_refresh_label.setText(
                f"{self._table.begin_date} 至 {self._table.end_date}"
            )

        self._grid_container.updateGeometry()
