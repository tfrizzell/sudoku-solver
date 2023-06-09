# sudoku-solver
Sudoku puzzle solver written as a python refresher

## Usage

```sh
Syntax: python3 sudoku.py
```

Once running, you will be prompted to enter your puzzle. Use zero (0) to denote an empty square. Whitespace is optional.

## Example

```sh
$ python sudoku.py 
Enter your Sudoku board below, using zero (0) to represent empty squares.
(Enter an empty line or press Ctrl+D or Crtl+Z to save)

9 0 2 0 0 0 1 0 0
0 4 0 2 0 7 0 3 0
0 0 0 0 5 0 0 0 0
0 8 0 0 6 0 0 0 0
0 0 1 5 0 8 3 0 0
0 0 0 0 4 0 0 5 0
0 0 4 0 0 0 0 0 7
0 7 0 8 0 3 0 2 0
0 0 0 0 0 6 0 0 0

┌───────┬───────┬───────┐
│ 9 5 2 │ 6 3 4 │ 1 7 8 │
│ 1 4 6 │ 2 8 7 │ 5 3 9 │
│ 8 3 7 │ 1 5 9 │ 2 6 4 │
├───────┼───────┼───────┤
│ 4 8 5 │ 3 6 2 │ 7 9 1 │
│ 7 6 1 │ 5 9 8 │ 3 4 2 │
│ 2 9 3 │ 7 4 1 │ 8 5 6 │
├───────┼───────┼───────┤
│ 3 1 4 │ 9 2 5 │ 6 8 7 │
│ 6 7 9 │ 8 1 3 │ 4 2 5 │
│ 5 2 8 │ 4 7 6 │ 9 1 3 │
└───────┴───────┴───────┘
Solve time: 0.1036 seconds
```
