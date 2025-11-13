import tkinter as tk
from tkinter import messagebox

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.config(bg="#F0F0F0")

        self.initial_board = set()

        vcmd = (root.register(self.validate_input), '%P')

        self.entries = {}
        
        cell_colors = ["#FFFFFF", "#E8E8E8"]
        font_style_initial = ('Calibri', 18, 'bold')
        
        main_frame = tk.Frame(root, bd=3, relief="solid", bg="#333333")
        main_frame.pack(pady=20, padx=20)

        frames = [[tk.Frame(main_frame, borderwidth=1, relief="solid") for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                frames[r][c].grid(row=r, column=c)
        
        for row in range(9):
            for col in range(9):
                frame_row, frame_col = row // 3, col // 3
                entry_row, entry_col = row % 3, col % 3
                
                bg_color = cell_colors[(frame_row + frame_col) % 2]

                entry = tk.Entry(
                    frames[frame_row][frame_col], 
                    width=3, 
                    font=font_style_initial, 
                    justify='center',
                    bd=1,
                    relief="solid",
                    bg=bg_color,
                    fg="#000000",
                    highlightcolor="#4A90E2",
                    highlightthickness=2,
                    validate="key",
                    validatecommand=vcmd
                )
                entry.grid(row=entry_row, column=entry_col, sticky="nsew", ipady=5)
                entry.bind('<FocusIn>', self.on_focus_in)
                entry.bind('<FocusOut>', self.on_focus_out)
                self.entries[(row, col)] = entry
                
                entry.bind('<Up>', lambda e, r=row, c=col: self.move_focus(e, r - 1, c))
                entry.bind('<Down>', lambda e, r=row, c=col: self.move_focus(e, r + 1, c))
                entry.bind('<Left>', lambda e, r=row, c=col: self.move_focus(e, r, c - 1))
                entry.bind('<Right>', lambda e, r=row, c=col: self.move_focus(e, r, c + 1))

        button_frame = tk.Frame(root, bg="#F0F0F0")
        button_frame.pack(pady=10)
        
        button_style = {
            'font': ('Calibri', 14, 'bold'),
            'bg': '#4A90E2',
            'fg': 'white',
            'activebackground': '#357ABD',
            'activeforeground': 'white',
            'relief': 'raised',
            'bd': 2,
            'width': 10,
            'height': 2
        }

        solve_button = tk.Button(button_frame, text="Solve", command=self.solve_gui, **button_style)
        solve_button.pack(side="left", padx=15)

        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_board, **button_style)
        clear_button.pack(side="left", padx=15)

    def validate_input(self, P):
        return (P.isdigit() and len(P) <= 1 and P != '0') or P == ""

    def on_focus_in(self, event):
        event.widget.config(bg="#FFFACD")

    def on_focus_out(self, event):
        for (r, c), entry in self.entries.items():
            if entry == event.widget:
                frame_r, frame_c = r // 3, c // 3
                bg_color = ["#FFFFFF", "#E8E8E8"][(frame_r + frame_c) % 2]
                event.widget.config(bg=bg_color)
                break

    def move_focus(self, event, new_row, new_col):
        new_row = new_row % 9
        new_col = new_col % 9
        self.entries[(new_row, new_col)].focus_set()
        return "break"

    def clear_board(self):
        self.initial_board.clear()
        for (r, c), entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.config(fg="#000000", font=('Calibri', 18, 'bold'))

    def solve_gui(self):
        board = []
        self.initial_board.clear()
        try:
            for row in range(9):
                current_row = []
                for col in range(9):
                    val = self.entries[(row, col)].get()
                    if val == "":
                        current_row.append(0)
                    elif val.isdigit():
                        num = int(val)
                        current_row.append(num)
                        self.initial_board.add((row, col))
                    else:
                        messagebox.showerror("Input Error", "Cells must be empty or contain only 1-9 numbers.")
                        return
                board.append(current_row)
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")
            return

        initial_copy = [row[:] for row in board]
        for r, c in self.initial_board:
            num = initial_copy[r][c]
            initial_copy[r][c] = 0
            if not is_valid(initial_copy, num, (r, c)):
                messagebox.showerror("Invalid input", f"Initial state is invalid. Numbers {num} in cell ({r+1},{c+1}) violates Sudoku rules.")
                return
            initial_copy[r][c] = num

        solver = SudokuSolver(board)
        if solver.solve():
            solved_board = solver.board
            for row in range(9):
                for col in range(9):
                    self.entries[(row, col)].delete(0, tk.END)
                    self.entries[(row, col)].insert(0, str(solved_board[row][col]))
                    if (row, col) not in self.initial_board:
                        self.entries[(row, col)].config(fg="#0000FF", font=('Calibri', 18))
        else:
            messagebox.showinfo("Result", "There is no solution for the sudoku :(")


def is_valid(board, num, pos):
    row, col = pos
    # Check row
    for i in range(9):
        if board[row][i] == num and i != col:
            return False
    # Check column
    for i in range(9):
        if board[i][col] == num and i != row:
            return False
    # Check box
    box_x, box_y = col // 3, row // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False
    return True

def get_possible_values(board, row, col):
    """Повертає набір можливих значень для клітинки."""
    if board[row][col] != 0:
        return set()
    
    possible = set(range(1, 10))
    # Row and column
    for i in range(9):
        possible.discard(board[row][i])
        possible.discard(board[i][col])

    # 3x3 box
    box_row_start, box_col_start = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row_start, box_row_start + 3):
        for j in range(box_col_start, box_col_start + 3):
            possible.discard(board[i][j])
    return possible

class SudokuSolver:
    def __init__(self, board):
        self.board = [row[:] for row in board]

    def solve(self):
        if not self.initial_propagation():
            return False
        return self.solve_recursive()

    def initial_propagation(self):
        #Forward checking
        stalled = False
        while not stalled:
            stalled = True
            for r in range(9):
                for c in range(9):
                    if self.board[r][c] == 0:
                        possible = get_possible_values(self.board, r, c)
                        if not possible:
                            return False # Конфлікт
                        if len(possible) == 1:
                            val = possible.pop()
                            self.board[r][c] = val
                            stalled = False
        return True

    def find_best_empty_cell_mrv(self):
        #Minimum remaining values (MRV)
        min_len = 10
        best_cell = None
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    num_possible = len(get_possible_values(self.board, r, c))
                    if num_possible < min_len:
                        min_len = num_possible
                        best_cell = (r, c)
        return best_cell

    def get_lcv_ordered_values(self, row, col):
        #Least constraining values (LCV)
        possible_values = get_possible_values(self.board, row, col)
        
        def count_constraints(val):
            constraints = 0
            # Row
            for c in range(9):
                if self.board[row][c] == 0 and val in get_possible_values(self.board, row, c):
                    constraints += 1
            # Column
            for r in range(9):
                if self.board[r][col] == 0 and val in get_possible_values(self.board, r, col):
                    constraints += 1
            # Box
            box_row_start, box_col_start = 3 * (row // 3), 3 * (col // 3)
            for r in range(box_row_start, box_row_start + 3):
                for c in range(box_col_start, box_col_start + 3):
                     if self.board[r][c] == 0 and val in get_possible_values(self.board, r, c):
                        constraints += 1
            return constraints
            
        return sorted(list(possible_values), key=count_constraints)

    def solve_recursive(self):
        cell = self.find_best_empty_cell_mrv()
        if not cell:
            return True
        
        row, col = cell
        
        ordered_values = self.get_lcv_ordered_values(row, col)

        for val in ordered_values:
            if is_valid(self.board, val, (row, col)):
                self.board[row][col] = val
                if self.solve_recursive():
                    return True
                self.board[row][col] = 0 # Backtrack
        
        return False

if __name__ == "__main__":
    main_window = tk.Tk()
    app = SudokuGUI(main_window)
    main_window.mainloop()