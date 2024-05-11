from app.employees.models import Employee
from app.lessons.entites.cell import CellEntity
from app.lessons.models import Lesson
from app.lessons.services.converters.group import GroupConverter


class CellConverter:
    def __init__(self):
        self.group_converter = GroupConverter()

    def convert_to_lessons(
        self,
        cells_map: dict[Employee, list[CellEntity]],
        indexed_groups: list[dict[int, dict[str, int]]],
    ) -> list[Lesson]:
        lessons: list[Lesson] = []
        for employee, cells in cells_map.items():
            groups = self.group_converter.convert(cells, indexed_groups)
            name = cells[0].name
            placement = cells[0].placement
            lesson = Lesson(
                employee=employee, name=name, groups=groups, placement=placement
            )
            lessons.append(lesson)
        return lessons
