from dataclasses import dataclass, field

from PyQt6.QtGui import QColor

from app.utils import parse_course_week


COLORS: list[QColor] = [
    QColor("#f5c842"),  # yellow
    QColor("#f59e0b"),  # orange
    QColor("#3b82f6"),  # blue
    QColor("#8b5cf6"),  # purple
    QColor("#22c55e"),  # green
    QColor("#ef4444"),  # red
]
BASE_HEIGHT = 36


@dataclass
class CourseModel:
    course_name: str = ""         # kcmc
    place: str = ""               # cdmc
    time_of_day: str = ""         # jcs
    day_of_week: str = ""         # xqj
    name_of_day_of_week: str = ""  # xqjmc
    class_name: str = ""          # jxbmc
    class_composition: str = ""   # jxbzc
    class_type: str = ""          # kclb
    score: str = ""               # xf
    total_hours: str = ""         # kczxs
    week_range: str = ""          # zcd
    teacher_name: str = ""        # xm
    campus: str = ""              # xqmc

    @staticmethod
    def from_dict(data: dict) -> "CourseModel":
        return CourseModel(
            course_name=data.get("kcmc", ""),
            place=data.get("cdmc", ""),
            time_of_day=data.get("jcs", ""),
            day_of_week=str(data.get("xqj", "")),
            name_of_day_of_week=data.get("xqjmc", ""),
            class_name=data.get("jxbmc", ""),
            class_composition=data.get("jxbzc", ""),
            class_type=data.get("kclb", ""),
            score=str(data.get("xf", "")),
            total_hours=str(data.get("kczxs", "")),
            week_range=data.get("zcd", ""),
            teacher_name=data.get("xm", ""),
            campus=data.get("xqmc", ""),
        )


@dataclass
class CourseTableModel:
    begin_date: str = ""
    end_date: str = ""
    courses: list[CourseModel] = field(default_factory=list)
    week_time: int = 0
    year_time: int = 0

    @staticmethod
    def from_dict(data: dict) -> "CourseTableModel":
        rqazc_list = data.get("rqazcList", [])
        begin_date = rqazc_list[0]["rq"] if rqazc_list else ""
        end_date = rqazc_list[-1]["rq"] if rqazc_list else ""

        kb_list = data.get("kbList", [])
        courses = [CourseModel.from_dict(c) for c in kb_list]
        week_time = int(data.get("zs", 0))

        return CourseTableModel(
            begin_date=begin_date,
            end_date=end_date,
            courses=courses,
            week_time=week_time,
        )

    def for_week(self, ac_week: int) -> "CourseTableModel":
        filtered = [
            c for c in self.courses
            if ac_week in parse_course_week(c.week_range)
        ]
        return CourseTableModel(
            begin_date=self.begin_date,
            end_date=self.end_date,
            courses=filtered,
            week_time=ac_week,
            year_time=self.year_time,
        )


@dataclass
class CourseGraphicObject:
    color: QColor
    height: int = BASE_HEIGHT
    has_course: bool = False
    course_data: CourseModel | None = None
    place: str | None = None
    course_name: str | None = None


def get_time_info(course: CourseModel) -> tuple[int, int, int]:
    parts = course.time_of_day.split("-")
    start = int(parts[0])
    end = int(parts[1])
    length = end - start + 1
    return start, end, length


def create_course_graphics_of_day(
    day: int, table: CourseTableModel, color_dict: dict[str, QColor]
) -> list[CourseGraphicObject]:
    graphics: list[CourseGraphicObject] = []
    course_index = 0
    time = 1

    while time < 13:
        if course_index >= len(table.courses):
            graphics.append(CourseGraphicObject(color=QColor(0, 0, 0, 0)))
            time += 1
            continue

        course = table.courses[course_index]
        start, _, length = get_time_info(course)

        if int(course.day_of_week) < day:
            course_index += 1
            continue
        if int(course.day_of_week) > day:
            graphics.append(CourseGraphicObject(color=QColor(0, 0, 0, 0)))
            time += 1
            continue

        if start != time:
            graphics.append(CourseGraphicObject(color=QColor(0, 0, 0, 0)))
            time += 1
            continue

        if course.course_name not in color_dict:
            color_dict[course.course_name] = COLORS[len(color_dict) % len(COLORS)]

        block_height = BASE_HEIGHT * length + (length - 1) * 8
        graphics.append(
            CourseGraphicObject(
                color=color_dict[course.course_name],
                height=block_height,
                has_course=True,
                course_data=course,
                place=course.place,
                course_name=course.course_name,
            )
        )
        course_index += 1
        time += length

    return graphics
