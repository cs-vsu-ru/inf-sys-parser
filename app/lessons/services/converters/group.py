from collections import defaultdict
import re

from app.lessons.entites.cell import CellEntity


class GroupConverter:
    def convert(
        self, cells: list[CellEntity], indexed_groups: list[dict[int, dict[str, int]]]
    ) -> str:
        texts = []
        for sheet in 0, 1:
            cells_on_sheet = list(
                    filter(lambda cell: cell.sheet == sheet, cells)
                )
            for course, indexed_groups_on_course in indexed_groups[sheet].items():
                cells_on_course = list(
                    filter(lambda cell: cell.course == course, cells_on_sheet)
                )
                if cells_on_course:
                    text_on_course = self._convert_on_course(
                        cells_on_course, indexed_groups_on_course
                    )
                    master_course = 'маг' if sheet else ''
                    texts.append(f"{text_on_course} {course}к {master_course}")
        return ', '.join(texts)

    def _convert_on_course(
        self,
        cells_on_course: list[CellEntity],
        indexed_groups_on_course: dict[str, int],
    ) -> str:
        groups_on_course = self._group_cells(cells_on_course)
        full_groups, partial_groups, non_numeric_groups = self._classify_groups(
            groups_on_course, indexed_groups_on_course
        )

        full_groups = self._combine_consecutive_groups(full_groups)
        partial_groups.sort(key=float)
        non_numeric_groups.sort()

        all_groups = full_groups + partial_groups + non_numeric_groups
        has_group_space = len(all_groups) > 1 or len(non_numeric_groups)

        text = ','.join(map(str, all_groups)) + f"{' ' if has_group_space else ''}г"
        return text

    def _extract_group_number(self, group: str) -> str:
        match = re.search(r'(\d+)\s+группа', group)
        if match:
            return match.group(1)
        return group

    def _group_cells(self, cells_on_course: list[CellEntity]) -> dict[str, list[int]]:
        groups: dict[str, list[int]] = defaultdict(list)
        for cell in cells_on_course:
            groups[cell.group].append(cell.subgroup)
        return groups

    def _classify_groups(
        self,
        groups_on_course: dict[str, list[int]],
        indexed_groups_on_course: dict[str, int],
    ) -> tuple[list[int], list[str], list[str]]:
        full_groups = []
        partial_groups = []
        non_numeric_groups = []

        for group, subgroups in groups_on_course.items():
            max_subgroups = indexed_groups_on_course[group]
            group = self._extract_group_number(group)
            if len(subgroups) == max_subgroups:
                try:
                    group_num = int(group)
                    full_groups.append(group_num)
                except ValueError:
                    non_numeric_groups.append(group)
            else:
                try:
                    group_num = int(group)
                    for subgroup in subgroups:
                        partial_groups.append(f"{group_num}.{subgroup}")
                except ValueError:
                    for subgroup in subgroups:
                        non_numeric_groups.append(f"{group}.{subgroup}")

        return full_groups, partial_groups, non_numeric_groups

    def _combine_consecutive_groups(self, full_groups: list[int]) -> list[str]:
        full_groups.sort()
        ranges = []
        for group in full_groups:
            if ranges and group == ranges[-1][-1] + 1:
                ranges[-1][-1] = group
            else:
                ranges.append([group, group])
        return [
            f"{start}-{end}" if start != end else str(start) for start, end in ranges
        ]
