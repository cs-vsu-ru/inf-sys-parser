import re
from collections import defaultdict
from typing import Any

from app.lessons.entites.cell import CellEntity
from app.lessons.models import Lesson
from app.lessons.services.cells_fixer import CellsFixer
from app.lessons.services.converters.cell import CellConverter
from app.lessons.services.xlsx.parser import XlsxParser


class Parser:
    def __init__(self):
        self.xlsx_parser = XlsxParser()
        self.cell_converter = CellConverter()
        self.fixer = CellsFixer()
        self.lesson_manager = Lesson.objects
        self.errors: list[dict[str, Any]] = []
        self._cell_format_mismatch_count: int = 0
        self._cell_format_mismatch_samples: list[dict[str, Any]] = []
        # Limit on how many "unexpected cell format" examples we keep.
        # Increase this when you need to inspect additional problematic cells.
        self._cell_format_mismatch_samples_limit: int = 5000

    def _excel_col_letters(self, col: int) -> str:
        """
        Converts 1-based column index to Excel letters.
        Example: 1 -> A, 26 -> Z, 27 -> AA, 63 -> BK.
        """
        if col <= 0:
            return ''
        letters: list[str] = []
        while col > 0:
            col, rem = divmod(col - 1, 26)
            letters.append(chr(ord('A') + rem))
        letters.reverse()
        return ''.join(letters)

    def _excel_cell_ref(self, row: int | None, col: int | None) -> str | None:
        if row is None or col is None:
            return None
        return f"{self._excel_col_letters(col)}{row}"

    def _reset_errors(self) -> None:
        self.errors = []
        self._cell_format_mismatch_count = 0
        self._cell_format_mismatch_samples = []

    def _add_error(
            self,
            *,
            row: int | None,
            col: int | None,
            field: str,
            message: str,
    ) -> None:
        self.errors.append(
            {
                'row': row,
                'col': col,
                'field': field,
                'message': message,
            }
        )

    def parse(self, filename: str = 'schedule.xlsx') -> list[Lesson]:
        self._reset_errors()
        lessons: list[Lesson] = []
        data, course_map, group_map, indexed_groups = self._prepare_data(filename)
        for row in range(len(data[0])):
            if row > 3 and (row - 3) % 17:
                cells: list[CellEntity] = []
                for sheet in 0, 1:
                    # для некоторых листов может не существовать строки с таким индексом
                    try:
                        row_list = data[sheet][row]
                    except IndexError:
                        self._add_error(
                            row=row + 1,
                            col=None,
                            field='row',
                            message=f'row index {row} is out of range for sheet {sheet}',
                        )
                        continue
                    cells.extend(
                        self._create_cells(
                            row, row_list, course_map[sheet], group_map[sheet], sheet
                        )
                    )
                cells_map = self.fixer.fix(cells)
                row_lessons = self.cell_converter.convert_to_lessons(
                    cells_map, indexed_groups
                )
                if not self._complete_row_lessons(row_lessons, row):
                    continue
                lessons.extend(row_lessons)
        if self._cell_format_mismatch_count:
            # Вместо сотен однотипных ошибок по "не той структуре ячейки"
            # возвращаем несколько примеров и общий счётчик.
            if self._cell_format_mismatch_samples:
                self.errors.extend(self._cell_format_mismatch_samples)
            skipped = self._cell_format_mismatch_count - len(
                self._cell_format_mismatch_samples
            )
            if skipped > 0:
                self._add_error(
                    row=None,
                    col=None,
                    field='cell_format_skipped',
                    message=f'skipped {skipped} additional cells with unexpected format',
                )
        return lessons

    def _prepare_data(self, filename: str) -> tuple:
        data = []
        course_map = []
        group_map = []
        indexed_groups = []
        for sheet in 0, 1:
            # индекс строки в списке данных 0-ориентированный, поэтому для отчёта по строкам
            # переводим его в 1-ориентированный (как в Excel)
            data.append(self.xlsx_parser.parse(filename, sheet))
            course_map.append(self._map_courses(data[sheet][0], sheet))
            group_map.append(self._map_groups(data[sheet][1], sheet))
            indexed_groups.append(
                self._index_groups(course_map[sheet], group_map[sheet])
            )
        return data, course_map, group_map, indexed_groups

    def _extract_course_number(self, course: str) -> int:
        return int(course.strip().split()[0])

    def _map_courses(
            self, courses_row: list[str], sheet: int
    ) -> dict[int, int]:
        course_map = {}
        for column, course in enumerate(courses_row):
            if column > 1:
                if course is None:
                    continue
                if isinstance(course, str) and not course.strip():
                    continue
                try:
                    course_map[column] = self._extract_course_number(str(course))
                except Exception as exc:
                    # строка с курсами — первая строка (индекс 0) соответствующего листа
                    self._add_error(
                        row=1,
                        col=column + 1,
                        field='course',
                        message=f'cannot parse course value "{course}": {exc}',
                    )
        return course_map

    def _map_groups(
            self, groups_row: list[str], sheet: int
    ) -> dict[int, tuple[str, int]]:
        group_map: dict[int, tuple[str, int]] = {}
        current_group: str | None = None
        current_subgroup: int | None = None
        for column, group in enumerate(groups_row):
            if column > 1:
                try:
                    group = group.strip() if isinstance(group, str) else str(group)
                except Exception as exc:
                    # строка с группами — вторая строка (индекс 1) соответствующего листа
                    self._add_error(
                        row=2,
                        col=column + 1,
                        field='group',
                        message=f'cannot parse group value "{group}": {exc}',
                    )
                    continue
                if not group:
                    continue
                if group == current_group:
                    current_subgroup = (current_subgroup or 0) + 1
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
            try:
                course = course_map[column]
            except KeyError:
                self._add_error(
                    row=None,
                    col=column + 1,
                    field='course_map',
                    message='course not mapped for group column',
                )
                continue
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
                # Пропускаем заведомо "пустые" ячейки (в шаблоне иногда бывают пробелы/переводы строк)
                if cell_text is None:
                    continue
                if isinstance(cell_text, str) and not cell_text.strip():
                    continue
                # Не пытаемся парсить колонки, которых нет в соответствующих мапах
                if column not in course_map or column not in group_map:
                    continue
                if cell_text:
                    try:
                        cell = self._create_cell(
                            cell_text, row, column, course_map, group_map, sheet
                        )
                    except ValueError as exc:
                        # Чаще всего это "непохожий на занятие" контент (часть шаблона/пустоты).
                        # Чтобы не раздувать ошибки, ограничиваем количество примеров.
                        self._cell_format_mismatch_count += 1
                        if len(self._cell_format_mismatch_samples) < self._cell_format_mismatch_samples_limit:
                            cell_ref = self._excel_cell_ref(row + 1, column + 1)
                            prefix = f'{cell_ref}: ' if cell_ref else ''
                            self._cell_format_mismatch_samples.append(
                                {
                                    'row': row + 1,
                                    'col': column + 1,
                                    'field': 'cell',
                                    'message': prefix + str(exc),
                                }
                            )
                        continue
                    except Exception as exc:
                        # Ошибка в конкретной ячейке не должна прерывать обработку строки
                        cell_ref = self._excel_cell_ref(row + 1, column + 1)
                        prefix = f'{cell_ref}: ' if cell_ref else ''
                        self._add_error(
                            row=row + 1,
                            col=column + 1,
                            field='cell',
                            message=prefix + (str(exc) or exc.__class__.__name__),
                        )
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
        if not isinstance(cell_text, str):
            cell_text = str(cell_text)
        cell_text = re.sub(r'(\s|\n_){2,}', ' ', cell_text)
        if len(cell_text.split(' ')) < 5:
            raise ValueError(
                f'unexpected cell format: expected >=5 parts, got {len(cell_text.split(" "))}'
            )
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
        try:
            weekday = self._get_weekday(row)
            number = self._get_number(row)
            is_denominator = self._get_is_denominator(row)
        except Exception as exc:
            # если не удалось определить общие параметры строки, пропускаем все занятия этой строки
            self._add_error(
                row=row + 1,
                col=None,
                field='lesson_meta',
                message=str(exc),
            )
            return False
        for row_lesson in row_lessons:
            row_lesson.weekday = weekday
            row_lesson.number = number
            row_lesson.is_denominator = is_denominator
        return True
