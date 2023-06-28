import re
import time

class Board:
    def __init__(self, cells=None):
        self._cells = list(map(lambda x: Cell(), range(81)))

        if cells is not None:
            for i in range(0, min(len(self._cells), len(cells))):
                if cells[i] is not None and cells[i] > 0 and cells[i] < 10:
                    self._cells[i] = Cell(cells[i])

    def is_solved(self):
        return len(list(filter(lambda cell: cell.get_value() is None, self._cells))) == 0 \
            and self._validate_blocks() \
            and self._validate_columns() \
            and self._validate_rows()

    def print(self):
        print("┌───────┬───────┬───────┐")

        for y in range(9):
            print("│", end=" ")

            for x in range(9):
                print(self._cells[9 * y + x].to_string(), end=" ")

                if x == 2 or x == 5:
                    print("│", end=" ")

            print("│")

            if y == 2 or y == 5:
                print("├───────┼───────┼───────┤")

        print("└───────┴───────┴───────┘")

    def _remove_possible_value(self, cells, value):
        for cell in cells:
            if cell.get_value() != value:
                cell.remove_possible_value(value)

    def _scan_block(self, y, x):
        self._scan_cells(list(map(lambda x: self._cells[9 * y + x], range(x - (x % 3), 3 + x - (x % 3)))) + list(map(lambda x: self._cells[9 * (y + 1) + x], range(x - (x % 3), 3 + x - (x % 3)))) + list(map(lambda x: self._cells[9 * (y + 2) + x], range(x - (x % 3), 3 + x - (x % 3)))))

    def _scan_blocks(self):
        for y in range(0, 8, 3):
            for x in range(0, 8, 3):
                self._scan_block(y, x)

    def _scan_cells(self, cells):
        for value in range(1, 10):
            if len([cell for cell in cells if cell.get_value() == value]) == 1:
                self._remove_possible_value(cells, value)
                continue

            possible = [cell for cell in cells if cell.is_possible(value)]

            if len(possible) == 1:
                possible[0].set_value(value)
                self._remove_possible_value(cells, value)

    def _scan_column(self, x):
        self._scan_cells(list(map(lambda y: self._cells[9 * y + x], range(9))))

    def _scan_columns(self):
        for x in range(9):
            self._scan_column(x)

    def _scan_row(self, y):
        self._scan_cells(list(map(lambda x: self._cells[9 * y + x], range(9))))

    def _scan_rows(self):
        for y in range(9):
            self._scan_row(y)

    def set_cell(self, y, x, value):
        self._cells[9 * y + x].set_value(value)

    def solve(self):
        count = 0

        while not self.is_solved() and count < 162:
            self._scan_blocks()
            self._scan_columns()
            self._scan_rows()
            count = count + 1

        if not self.is_solved():
            changeable = list(filter(lambda cell: not cell.is_locked() and cell.get_value() is None and len(cell.get_possible_values()) > 1, self._cells))
            changeable.sort(key=lambda cell: len(cell.get_possible_values()))

            for cell in changeable:
                for value in cell.get_possible_values():
                    test = Board(list(map(lambda c: c.get_value() or 0 if c != cell else value, self._cells)))
                    test.solve()

                    if test.is_solved():
                        self._update(test._cells)
                        return

    def _update(self, cells):
        for i in range(len(self._cells)):
            if self._cells[i].get_value() is None:
                self._cells[i].set_value(cells[i].get_value())

    def _validate_block(self, y, x):
        return self._validate_cells(list(map(lambda x: self._cells[9 * y + x], range(x - (x % 3), 3 + x - (x % 3)))) + list(map(lambda x: self._cells[9 * (y + 1) + x], range(x - (x % 3), 3 + x - (x % 3)))) + list(map(lambda x: self._cells[9 * (y + 2) + x], range(x - (x % 3), 3 + x - (x % 3)))))

    def _validate_blocks(self):
        for y in range(0, 8, 3):
            for x in range(0, 8, 3):
                if not self._validate_block(y, x):
                    return False
                
        return True

    def _validate_cells(self, cells):
        values = set(filter(lambda v: v > 0 and v < 10, set(map(lambda c: c.get_value() or 0, cells))))
        return len(values) == 9

    def _validate_column(self, x):
        return self._validate_cells(list(map(lambda y: self._cells[9 * y + x], range(9))))

    def _validate_columns(self):
        for x in range(9):
            if not self._validate_column(x):
                return False
            
        return True

    def _validate_row(self, y):
        return self._validate_cells(list(map(lambda x: self._cells[9 * y + x], range(9))))

    def _validate_rows(self):
        for y in range(9):
            if not self._validate_row(y):
                return False
            
        return True



class Cell:
    def __init__(self, value=None):
        self._value = value
        self._possible_values = [value] if value is not None else [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self._locked = True if value is not None else False

    def get_possible_values(self):
        return self._possible_values[:]

    def get_value(self):
        return self._value

    def has_value(self):
        return self._value is not None

    def is_locked(self):
        return self._locked

    def is_possible(self, value):
        return value in self._possible_values

    def remove_possible_value(self, value):
        if not self._locked and value in self._possible_values:
            self._possible_values.remove(value)

            if len(self._possible_values) == 1:
                self._value = self._possible_values[0]

    def set_value(self, value):
        if not self._locked:
            self._value = value
            self._possible_values = [value]

    def to_string(self):
        if self._value is None:
            return " "
        elif self._locked:
            return str(self._value)
        else:
            return "\033[94m" + str(self._value) + "\033[0m"



print("Enter your Sudoku board below, using zero (0) to represent empty squares.\n\033[2m(Enter an empty line or press Ctrl+D or Crtl+Z to save)\033[0m\n")
contents = ""

while True:
    try:
        line = input()
    except EOFError:
        break

    contents = contents + "\n" + line

    if contents.endswith("\n"):
        break

board = Board(list(map(lambda v: int(v), list(re.sub("\D+", "", contents.strip())))))
start = time.time()

try:
    board.solve()
except KeyboardInterrupt:
    print("")

end = time.time()
board.print()

if board.is_solved():
    print("\033[2mSolve time: %.4f seconds\033[0m" % (end - start))
else:
    print("\033[91m!!! Failed to solve puzzle !!!\033[0m")
    print("\033[2mExecution time: %.4f seconds\033[0m" % (end - start))
