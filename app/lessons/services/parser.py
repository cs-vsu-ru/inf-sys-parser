from collections import defaultdict
import re

from app.lessons.entites.cell import CellEntity
from app.lessons.models import Lesson
from app.lessons.services.converters.cell import CellConverter
from app.lessons.services.cells_fixer import CellsFixer
from app.lessons.services.xlsx.parser import XlsxParser


class Parser:
    def __init__(self):
        self.xlsx_parser = XlsxParser()
        self.cell_converter = CellConverter()
        self.fixer = CellsFixer()
        self.lesson_manager = Lesson.objects

    def parse(self, filename: str = 'schedule.xlsx') -> list[Lesson]:
        lessons = []
        data, course_map, group_map, indexed_groups = self._prepare_data(filename)
        for row in range(len(data[0])):
            if row > 3 and (row - 3) % 17:
                cells = []
                for sheet in 0, 1:
                    row_list = data[sheet][row]
                    cells.extend(
                        self._create_cells(
                            row, row_list, course_map[sheet], group_map[sheet], sheet
                        )
                    )
                cells_map = self.fixer.fix(cells)
                row_lessons = self.cell_converter.convert_to_lessons(
                    cells_map, indexed_groups
                )
                self._complete_row_lessons(row_lessons, row)
                lessons.extend(row_lessons)
        return lessons

    def _prepare_data(self, filename: str) -> tuple:
        data = []
        course_map = []
        group_map = []
        indexed_groups = []
        for sheet in 0, 1:
            data.append(self.xlsx_parser.parse(filename, sheet))
            course_map.append(self._map_courses(data[sheet][0]))
            group_map.append(self._map_groups(data[sheet][1]))
            indexed_groups.append(
                self._index_groups(course_map[sheet], group_map[sheet])
            )
        return data, course_map, group_map, indexed_groups

    def _extract_course_number(self, course: str) -> int:
        return int(course.strip().split()[0])

    def _map_courses(self, courses_row: list[str]) -> dict[int, int]:
        course_map = {}
        for column, course in enumerate(courses_row):
            if column > 1:
                course_map[column] = self._extract_course_number(course)
        return course_map

    def _map_groups(self, groups_row: list[str]) -> dict[int, tuple[str, int]]:
        group_map = {}
        current_group = None
        current_subgroup = None
        for column, group in enumerate(groups_row):
            if column > 1:
                group = group.strip()
                if group == current_group:
                    current_subgroup += 1
                else:
                    current_group = group
                    current_subgroup = 1
                group_map[column] = current_group, current_subgroup
        return group_map

    def _index_groups(
        self, course_map: dict[int, int], group_map: dict[int, tuple[str, int]]
    ) -> dict[int, dict[str, int]]:
        indexed_groups: dict[int, dict[str, int]] = defaultdict(dict)
        current_course = 1
        indexed_groups_on_course: dict[str, int] = defaultdict(int)
        for column, (group, subgroup) in group_map.items():
            course = course_map[column]
            if indexed_groups_on_course[group] < subgroup:
                indexed_groups_on_course[group] = subgroup
            if current_course != course:
                indexed_groups[current_course] = indexed_groups_on_course
                current_course = course
                indexed_groups_on_course = defaultdict(int)
                indexed_groups_on_course[group] = subgroup
        indexed_groups[current_course] = indexed_groups_on_course
        return indexed_groups

    def _create_cells(
        self, row: int, row_list, course_map, group_map, sheet
    ) -> list[CellEntity]:
        cells = []
        for column, cell_text in enumerate(row_list):
            if column > 1:
                if cell_text:
                    try:
                        cell = self._create_cell(
                            cell_text, row, column, course_map, group_map, sheet
                        )
                    except ValueError:
                        continue
                    cells.append(cell)
        return cells

    def _create_cell(
        self, cell_text: str, row, column, course_map, group_map, sheet
    ) -> CellEntity:
        cell_data: dict = self._parse_cell_text(cell_text)
        group, subgroup = group_map[column]
        cell_data['group'] = group
        cell_data['subgroup'] = subgroup
        cell_data['is_denominator'] = self._get_is_denominator(row)
        cell_data['course'] = course_map[column]
        cell_data['weekday'] = self._get_weekday(row)
        cell_data['number'] = self._get_number(row)
        cell_data['sheet'] = sheet
        return CellEntity(**cell_data)

    def _get_weekday(self, row: int) -> int:
        intervals = {
            (4, 19): 0,
            (21, 36): 1,
            (38, 53): 2,
            (55, 70): 3,
            (72, 87): 4,
            (89, 102): 5,
        }
        for interval, weekday in intervals.items():
            if interval[0] <= row <= interval[1]:
                return weekday
        raise ValueError(row)

    def _get_number(self, row: int) -> int:
        row -= 4
        if 98 < row < 0 or (row + 1) % 17 == 0:
            raise ValueError
        skips = row // 16
        result = (row - skips) // 2
        return result % 8

    def _get_is_denominator(self, row: int) -> bool:
        is_denominator = bool(row % 2)
        if 21 <= row <= 36 or 55 <= row <= 70 or 89 <= row <= 102:
            return not is_denominator
        return is_denominator

    def _parse_cell_text(self, cell_text: str) -> dict[str, str]:
        cell_text = re.sub(r'(\s|\n_){2,}', ' ', cell_text)
        if len(cell_text.split(' ')) < 5:
            raise ValueError
        cell_text, placement = cell_text.rsplit(' ', 1)
        cell_text, _, surname, initials = cell_text.rsplit(' ', 3)
        employee_name = f"{surname} {initials}"
        name = cell_text
        return {
            'employee_name': employee_name,
            'name': name,
            'placement': placement,
        }

    def _complete_row_lessons(self, row_lessons: list[Lesson], row: int) -> None:
        weekday = self._get_weekday(row)
        number = self._get_number(row)
        is_denominator = self._get_is_denominator(row)
        for row_lesson in row_lessons:
            row_lesson.weekday = weekday
            row_lesson.number = number
            row_lesson.is_denominator = is_denominator
