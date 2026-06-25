import asyncio

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from qfluentwidgets import (
    InfoBar,
    InfoBarPosition,
    FluentIcon,
    TransparentToolButton,
    ScrollArea,
    SettingCard,
)

import app.api.interface as api


class ExamWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._exam_items: list[dict] = []
        self._build_ui()
        self._init_from_cache()

    def _build_ui(self):
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()

        title = QLabel("期末考试信息")
        title.setStyleSheet("font-size: 24px; font-weight: 600;")

        self._refresh_btn = TransparentToolButton(FluentIcon.SYNC, self)
        self._refresh_btn.clicked.connect(self._on_refresh_clicked)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._refresh_btn)
        root.addLayout(header)

        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.viewport().setStyleSheet("background: transparent;")

        self._list_container = QWidget()
        self._list_container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 8, 0, 0)
        self._list_layout.setSpacing(4)
        self._list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self._list_container)

        root.addWidget(scroll)

    def _init_from_cache(self):
        ok, cache = api.load_cache()
        if ok and "exam_inf" in cache:
            self._render_exams(cache["exam_inf"].get("items", []))

    def _on_refresh_clicked(self):
        self._refresh_btn.setEnabled(False)

        async def do_refresh():
            return await api.fetch_exam_info_async()

        def on_done(task):
            ok, err = task.result()
            self._refresh_btn.setEnabled(True)

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
                    content="登录或获取考试信息失败，请检查学号和密码",
                    duration=5000,
                    position=InfoBarPosition.TOP,
                    parent=self.window(),
                )
                return

            ok2, cache = api.load_cache()
            if ok2 and "exam_inf" in cache:
                self._render_exams(cache["exam_inf"].get("items", []))

            InfoBar.success(
                title="刷新成功",
                content="考试信息已更新",
                duration=2000,
                position=InfoBarPosition.TOP,
                parent=self.window(),
            )

        task = asyncio.ensure_future(do_refresh())
        task.add_done_callback(on_done)

    def _clear_list(self):
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_exams(self, items: list[dict]):
        self._exam_items = items
        self._clear_list()

        if not items:
            empty_label = QLabel("暂无考试信息")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: gray; font-size: 14px; padding: 32px;")
            self._list_layout.addWidget(empty_label)

        for exam in items:
            kcmc = exam.get("kcmc", "未知课程")
            kssj = exam.get("kssj", "")
            cdmc = exam.get("cdmc", "")
            zwh = exam.get("zwh", "")
            ksfs = exam.get("ksfs", "")
            kkxy = exam.get("kkxy", "")

            card = SettingCard(
                FluentIcon.EDUCATION,
                kcmc,
                f"{kssj}  ·  {cdmc}  ·  座位号: {zwh}  ·  {ksfs}  ·  {kkxy}",
                self._list_container,
            )
            self._list_layout.addWidget(card)

        self._list_layout.addStretch()
