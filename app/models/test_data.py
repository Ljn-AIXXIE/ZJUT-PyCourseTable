"""
Temporary test data for debugging the course table rendering.
Usage:
    from app.models.test_data import create_test_table
    table_widget.set_table(create_test_table())
"""

from app.models.course import CourseModel, CourseTableModel

DAYS = ["一", "二", "三", "四", "五", "六", "日"]


def _course(name, day, time_range, place, teacher, class_type, score, hours, campus="朝晖"):
    start, end = time_range
    return CourseModel(
        course_name=name,
        place=place,
        time_of_day=f"{start}-{end}",
        day_of_week=str(day),
        name_of_day_of_week=f"星期{DAYS[day - 1]}",
        class_name=f"{name}教学班",
        class_composition="计算机2201,计算机2202",
        class_type=class_type,
        score=score,
        total_hours=hours,
        teacher_name=teacher,
        campus=campus,
    )


def create_test_table() -> CourseTableModel:
    courses = [
        # Monday
        _course("高等数学", 1, (1, 2), "教401", "张老师", "必修", "5", "80"),
        _course("大学英语", 1, (3, 4), "教301", "李老师", "必修", "4", "64"),
        _course("数据结构", 1, (6, 8), "教201", "王老师", "必修", "4", "64"),

        # Tuesday
        _course("操作系统", 2, (1, 2), "教101", "赵老师", "必修", "4", "64"),
        _course("计算机网络", 2, (3, 5), "教202", "钱老师", "必修", "3", "48"),
        _course("体育", 2, (6, 7), "体育馆", "孙老师", "必修", "1", "32"),

        # Wednesday
        _course("高等数学", 3, (1, 2), "教401", "张老师", "必修", "5", "80"),
        _course("数据库原理", 3, (3, 4), "教303", "周老师", "必修", "3", "48"),
        _course("软件工程", 3, (6, 8), "教204", "吴老师", "必修", "3", "48"),

        # Thursday
        _course("操作系统", 4, (1, 2), "教101", "赵老师", "必修", "4", "64"),
        _course("编译原理", 4, (3, 5), "教305", "郑老师", "选修", "2", "32"),
        _course("大学英语", 4, (6, 7), "教301", "李老师", "必修", "4", "64"),

        # Friday
        _course("计算机网络", 5, (1, 2), "教202", "钱老师", "必修", "3", "48"),
        _course("数据结构", 5, (3, 4), "教201", "王老师", "必修", "4", "64"),
        _course("形势与政策", 5, (6, 7), "教501", "冯老师", "必修", "1", "16"),

        # Saturday (optional — test weekend toggle)
        _course("创新实践", 6, (1, 4), "实验楼A", "陈老师", "选修", "2", "32"),
    ]

    return CourseTableModel(
        begin_date="2026-02-17",
        end_date="2026-07-05",
        courses=courses,
        week_time=12,
    )
