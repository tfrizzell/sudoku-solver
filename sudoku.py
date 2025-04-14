"""Solves a Sudoku board given through user input."""

import re
import time
from typing import Self


class Cell:
    """Provides the structure for a cell on a Sudoku board."""

    def __init__(self: Self, value: int | None = None):
        """Construct a new Sudoku board cell.

        :param value: The value belonging to the call
        :type value: int, optional
        """
        if value is not None and (value < 1 or value > 9):
            raise ValueError('value must be between 1 and 9')

        self._value = value
        self._possible_values = [value] if value is not None else list(range(1, 10))
        self._locked = value is not None

    def get_possible_values(self: Self) -> list[int]:
        """Get a list of values that could be written to this cell.

        :return: The list of values that could be written to this cell
        :rtype: list[int]
        """
        return [self._value] if self._value is not None else self._possible_values[:]

    def get_value(self: Self) -> int | None:
        """Get the value belonging to this cell.

        :return: The value beloging to this cell
        :rtype: int, optional
        """
        return self._value

    def has_value(self: Self) -> bool:
        """Checks to see if the cell has a value assigned.

        :return: `True` if the cell has a value, otherwise `False`
        :rtype: bool
        """
        return self._value is not None

    def is_locked(self: Self) -> bool:
        """Checks to see if the cell is locked. A cell is considered locked if it's given a value on initialization.

        :return: `True` if the cell is locked, otherwise `False`
        :rtype: bool
        """
        return self._locked

    def is_possible(self: Self, value: int) -> bool:
        """Checks to see whether the given value could be assigned to the cell.

        :param value: The value to test
        :type value: int
        :return: `True` if the value could be assigned to the cell, otherwise `False`
        :rtype: bool
        """
        return value in self._possible_values

    def remove_possible_value(self: Self, value: int) -> None:
        """Removes the given value from the list of the cell's possible values. No changes are made if the
        cell is locked.

        :param value: The value to be removed
        :type value: int
        """
        if not self._locked and value in self._possible_values:
            self._possible_values.remove(value)

            if len(self._possible_values) == 1:
                self._value = self._possible_values[0]

    def set_value(self: Self, value: int) -> None:
        """Sets the value of the cell. No changes are made if the cell is locked.

        :param value: The new value of the cell
        :type value: int
        """
        if not self._locked:
            self._value = value

    def to_string(self: Self) -> str:
        """Writes out the string representation of the cell.

        :return: The string representation of the cell
        :rtype: str
        """
        if self._value is None:
            return ' '

        if self._locked:
            return str(self._value)

        return '\033[94m' + str(self._value) + '\033[0m'


class Board:
    """Provides the structure for a Sudoku board."""

    def __init__(self: Self, cells: dict[int, int] | list[int] | None = None):
        """Constructs a new Sudoku board.

        :param cells: A list of cell values to initialize the board with.
        :type cells: dict[int, int] | list[int], optional
        """
        self._cells = list(map(lambda x: Cell(), range(81)))

        if cells is not None:
            for i in range(0, min(len(self._cells), len(cells))):
                if cells[i] is not None and cells[i] > 0 and cells[i] < 10:
                    self._cells[i] = Cell(cells[i])

    def is_solved(self: Self) -> bool:
        """Checks to see if the board has been solved successfully.

        :return: `True` if the board has been solved, otherwise `False`
        :rtype: bool
        """
        return (
            len(list(filter(lambda cell: cell.get_value() is None, self._cells))) == 0
            and self._validate_blocks()
            and self._validate_columns()
            and self._validate_rows()
        )

    def print(self: Self) -> None:
        """Prints the board to stdout."""
        print('┌───────┬───────┬───────┐')

        for y in range(9):
            print('│', end=' ')

            for x in range(9):
                print(self._cells[9 * y + x].to_string(), end=' ')

                if x in (2, 5):
                    print('│', end=' ')

            print('│')

            if y in (2, 5):
                print('├───────┼───────┼───────┤')

        print('└───────┴───────┴───────┘')

    def _remove_possible_value(self: Self, cells: list[Cell], value: int) -> None:
        """Removes the possible values in each of the given cells.

        :param cells: The cells to remove the value from
        :type cells: list[:class:`Cell`]
        :param value: The value to be removed
        :type value: int
        """
        for cell in cells:
            if cell.get_value() != value:
                cell.remove_possible_value(value)

    def _scan_block(self: Self, y: int, x: int) -> None:
        """Scans a 3x3 block of cells to remove known values from other cells.

        :param y: The y location marking the start of the block
        :type y: int
        :param x: The x location marking the start of the block
        :type x: int
        """
        self._scan_cells(
            list(
                map(
                    lambda x: self._cells[9 * y + x],
                    range(x - (x % 3), 3 + x - (x % 3)),
                )
            )
            + list(
                map(
                    lambda x: self._cells[9 * (y + 1) + x],
                    range(x - (x % 3), 3 + x - (x % 3)),
                )
            )
            + list(
                map(
                    lambda x: self._cells[9 * (y + 2) + x],
                    range(x - (x % 3), 3 + x - (x % 3)),
                )
            )
        )

    def _scan_blocks(self: Self) -> None:
        """Scans all 3x3 cell blocks to remove known values from other cells."""
        for y in range(0, 8, 3):
            for x in range(0, 8, 3):
                self._scan_block(y, x)

    def _scan_cells(self: Self, cells: list[Cell]) -> None:
        """Scans the list cells to remove known values from other cells.

        :param cells: The list of cells to remove known values from
        :type cells: list[:class:`Cell`]
        """
        for value in range(1, 10):
            if len([cell for cell in cells if cell.get_value() == value]) == 1:
                self._remove_possible_value(cells, value)
                continue

            possible = [cell for cell in cells if cell.is_possible(value)]

            if len(possible) == 1:
                possible[0].set_value(value)
                self._remove_possible_value(cells, value)

    def _scan_column(self: Self, x) -> None:
        """Scans a 9x1 column of cells to remove known values from other cells.

        :param x: The x location of the column
        :type x: int
        """
        self._scan_cells(list(map(lambda y: self._cells[9 * y + x], range(9))))

    def _scan_columns(self: Self) -> None:
        """Scans all 9x1 cell columns to remove known values from other cells."""
        for x in range(9):
            self._scan_column(x)

    def _scan_row(self: Self, y) -> None:
        """Scans a 1x9 row of cells to remove known values from other cells.

        :param y: The y location of the row
        :type y: int
        """
        self._scan_cells(list(map(lambda x: self._cells[9 * y + x], range(9))))

    def _scan_rows(self: Self) -> None:
        """Scans all 1x9 cell rows to remove known values from other cells."""
        for y in range(9):
            self._scan_row(y)

    def set_cell(self: Self, y: int, x: int, value: int) -> None:
        """Sets the value of a cell.

        :param y: The y location of the cell
        :type y: int
        :param x: The x location of the cell
        :type x: int
        :param value: The value of the cell
        :type value: int
        """
        self._cells[9 * y + x].set_value(value)

    def solve(self: Self) -> None:
        """Attempts to solve the Sudoku board."""
        count = 0

        while not self.is_solved() and count < 162:
            self._scan_blocks()
            self._scan_columns()
            self._scan_rows()
            count = count + 1

        if not self.is_solved():
            changeable = list(
                filter(
                    lambda cell: not cell.is_locked()
                    and cell.get_value() is None
                    and len(cell.get_possible_values()) > 1,
                    self._cells,
                )
            )
            changeable.sort(key=lambda cell: len(cell.get_possible_values()))

            for cell in changeable:
                for value in cell.get_possible_values():
                    # pylint: disable=cell-var-from-loop
                    test = Board(
                        list(
                            map(
                                lambda c: c.get_value() or 0 if c != cell else value,
                                self._cells,
                            )
                        )
                    )
                    # pylint: enable=cell-var-from-loop

                    test.solve()

                    if test.is_solved():
                        self._update(test._cells)  # pylint: disable=protected-access
                        return

    def _update(self: Self, cells: list[Cell]) -> None:
        """Updates the values of the cells.

        :param cells: The new values of the cells
        :type cells: list[:class:`Cell`]
        """
        for i, cell in enumerate(self._cells):
            if cell.get_value() is None:
                cell.set_value(cells[i].get_value())

    def _validate_block(self: Self, y: int, x: int) -> bool:
        """Verifies whether the 3x3 block of cells has been solved.

        :param y: The y location marking the start of the block
        :type y: int
        :param x: The x location marking the start of the block
        :type x: int
        :return: `True` if the block is valid, otherwise `False`
        :rtype: bool
        """
        return self._validate_cells(
            list(
                map(
                    lambda x: self._cells[9 * y + x],
                    range(x - (x % 3), 3 + x - (x % 3)),
                )
            )
            + list(
                map(
                    lambda x: self._cells[9 * (y + 1) + x],
                    range(x - (x % 3), 3 + x - (x % 3)),
                )
            )
            + list(
                map(
                    lambda x: self._cells[9 * (y + 2) + x],
                    range(x - (x % 3), 3 + x - (x % 3)),
                )
            )
        )

    def _validate_blocks(self: Self) -> bool:
        """Validates all 3x3 blocks of cells to see if they have been solved.

        :return: `True` if all blocks are solved, otherwise `False`
        :rtype: bool
        """
        for y in range(0, 8, 3):
            for x in range(0, 8, 3):
                if not self._validate_block(y, x):
                    return False

        return True

    def _validate_cells(self: Self, cells: list[Cell]) -> bool:
        """Validates a list of cells to see if it has been solved.

        :param cells: The list of cells to validate
        :type cells: list[:class:`Cell`]
        :return: `True` if the cells have been solved, otherwise `False`
        :rtype: bool
        """
        values = set(
            filter(
                lambda v: 0 < v < 10,
                set(map(lambda c: c.get_value() or 0, cells)),
            )
        )

        return len(values) == 9

    def _validate_column(self: Self, x: int) -> bool:
        """Verifies whether the 9x1 column of cells has been solved.

        :param x: The x location of the column
        :type x: int
        :return: `True` if the column is solved, otherwise `False`
        :rtype: bool
        """
        return self._validate_cells(list(map(lambda y: self._cells[9 * y + x], range(9))))

    def _validate_columns(self: Self) -> bool:
        """Validates all 9x1 columns of cells to see if they have been solved.

        :return: `True` if all columns are solved, otherwise `False`
        :rtype: bool
        """
        for x in range(9):
            if not self._validate_column(x):
                return False

        return True

    def _validate_row(self: Self, y: int) -> bool:
        """Verifies whether the 1x9 row of cells has been solved.

        :param y: The y location of the row
        :type y: int
        :return: `True` if the row is solved, otherwise `False`
        :rtype: bool
        """
        return self._validate_cells(list(map(lambda x: self._cells[9 * y + x], range(9))))

    def _validate_rows(self: Self) -> bool:
        """Validates all 1x9 rows of cells to see if they have been solved.

        :return: `True` if all rows are solved, otherwise `False`
        :rtype: bool
        """
        for y in range(9):
            if not self._validate_row(y):
                return False

        return True


print(
    'Enter your Sudoku board below, using zero (0) to represent empty squares.\n'
    '\033[2m(Enter an empty line or press Ctrl+D or Crtl+Z to save)\033[0m\n'
)

contents: str = ''

while True:
    try:
        line = input()
    except EOFError:
        break

    contents = contents + '\n' + line

    if contents.endswith('\n'):
        break

board = Board(
    list(
        map(
            int,
            list(re.sub(r'\D+', '', re.sub(r'-', '0', contents.strip()))),
        )
    )
)

start = time.time()

try:
    board.solve()
except KeyboardInterrupt:
    print('')

end = time.time()
board.print()

if board.is_solved():
    print(f'\033[2mSolve time: {end - start:.4f} seconds\033[0m')
else:
    print('\033[91m!!! Failed to solve puzzle !!!\033[0m')
    print(f'\033[2mExecution time: {end - start:.4f} seconds\033[0m')
