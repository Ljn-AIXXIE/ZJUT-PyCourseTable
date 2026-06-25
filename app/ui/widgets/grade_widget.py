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


class GradeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grade_items: list[dict] = []
        self._build_ui()
        self._init_from_cache()

    def _build_ui(self):
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()

        title = QLabel("期末成绩查询")
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
        if ok and "grade_inf" in cache:
            self._render_grades(cache["grade_inf"].get("items", []))

    def _on_refresh_clicked(self):
        self._refresh_btn.setEnabled(False)

        async def do_refresh():
            return await api.fetch_grade_info_async()

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
                    content="登录或获取成绩信息失败，请检查学号和密码",
                    duration=5000,
                    position=InfoBarPosition.TOP,
                    parent=self.window(),
                )
                return

            ok2, cache = api.load_cache()
            if ok2 and "grade_inf" in cache:
                self._render_grades(cache["grade_inf"].get("items", []))

            InfoBar.success(
                title="刷新成功",
                content="成绩信息已更新",
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

    def _render_grades(self, items: list[dict]):
        self._grade_items = items
        self._clear_list()

        if not items:
            empty_label = QLabel("暂无成绩信息")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: gray; font-size: 14px; padding: 32px;")
            self._list_layout.addWidget(empty_label)

        for grade in items:
            kcmc = grade.get("kcmc", "未知课程")
            cj = grade.get("cj", "")
            jd = grade.get("jd", "")
            xf = grade.get("xf", "")
            jsxm = grade.get("jsxm", "")
            kcxzmc = grade.get("kcxzmc", "")
            khfsmc = grade.get("khfsmc", "")

            card = SettingCard(
                FluentIcon.CERTIFICATE,
                kcmc,
                f"成绩: {cj}  ·  绩点: {jd}  ·  学分: {xf}  ·  {kcxzmc}  ·  {khfsmc}  ·  教师: {jsxm}",
                self._list_container,
            )
            self._list_layout.addWidget(card)

        self._list_layout.addStretch()
