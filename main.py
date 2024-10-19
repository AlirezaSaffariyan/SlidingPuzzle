import sys
from collections import deque
import random
from time import sleep
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QComboBox,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer

ALGORITHMS = ["Select an algorithm", "BFS", "Bidirectional"]


class CustomMessageBox(QMessageBox):
    def __init__(self, title, message):
        super().__init__()
        self.setWindowTitle(title)
        self.setText(message)

        font = self.font()
        font.setPointSize(15)
        self.setFont(font)

        self.addButton(QMessageBox.Ok)


class PuzzleAlgorithms:
    def __init__(self, size, tiles, empty_tile):
        self.size = size
        self.tiles = tiles
        self.empty_tile = empty_tile

    def bfs(self):
        # Flatten the tiles to create an initial state
        initial_state = [tile for row in self.tiles for tile in row]
        initial_empty_tile = self.get_empty_tile_coordinates(initial_state)

        # Queue for BFS
        queue = deque([(initial_state, [])])
        visited = set()
        visited.add(tuple(initial_state))

        while queue:
            current_state, path = queue.popleft()
            empty_y, empty_x = self.get_empty_tile_coordinates(current_state)

            if self.bullshit_check_win(current_state):
                return path

            # Explore possible moves
            for move in self.can_move_to((empty_y, empty_x)):
                new_state = current_state[:]
                self.move_to(new_state, move)
                new_empty_tile = self.get_empty_tile_coordinates(new_state)
                new_state_tuple = tuple(new_state)

                if new_state_tuple not in visited:
                    visited.add(new_state_tuple)
                    new_path = path + [new_empty_tile]
                    queue.append((new_state, new_path))

        return None  # If no solution is found

    def bidirectional(self):
        # Goal State
        goal_state = list(range(1, self.size**2)) + [None]

        # Initial state
        initial_state = [tile for row in self.tiles for tile in row]
        initial_empty_tile = self.get_empty_tile_coordinates(initial_state)

        # Initialize BFS for forward and backward search
        queue_start = deque([(initial_state, [initial_empty_tile])])  # (state, path)
        queue_goal = deque([(goal_state, [(2, 2)])])  # (goal state, empty path)

        visited_start = {tuple(initial_state): []}
        visited_goal = {tuple(goal_state): []}

        while queue_start and queue_goal:
            # Expand from the start
            current_state_start, path_start = queue_start.popleft()
            empty_start = self.get_empty_tile_coordinates(current_state_start)

            # Check for a solution
            if tuple(current_state_start) in visited_goal:
                # Merge paths
                path_goal = visited_goal[tuple(current_state_start)]
                return (
                    path_start + path_goal[::-1]
                )  # Complete path from forward and backward

            # Explore possible moves
            for move in self.can_move_to(empty_start):
                new_state_start = current_state_start[:]
                new_state_start = self.move_to(new_state_start, move)
                new_empty_tile_start = self.get_empty_tile_coordinates(new_state_start)
                new_state_tuple_start = tuple(new_state_start)

                if new_state_tuple_start not in visited_start:
                    visited_start[new_state_tuple_start] = path_start + [
                        new_empty_tile_start
                    ]
                    queue_start.append(
                        (new_state_start, visited_start[new_state_tuple_start])
                    )

            # Expand from the goal
            current_state_goal, path_goal = queue_goal.popleft()
            empty_goal = self.get_empty_tile_coordinates(current_state_goal)

            # Check for a solution
            if tuple(current_state_goal) in visited_start:
                # Merge paths
                path_start = visited_start[tuple(current_state_goal)]
                return (
                    path_goal[::-1] + path_start
                )  # Complete path from backward and forward

            # Explore possible moves backwards
            for move in self.can_move_to(empty_goal):
                new_state_goal = current_state_goal[:]
                self.move_to(new_state_goal, move)
                new_empty_tile_goal = self.get_empty_tile_coordinates(new_state_goal)
                new_state_tuple_goal = tuple(new_state_goal)

                if new_state_tuple_goal not in visited_goal:
                    visited_goal[new_state_tuple_goal] = path_goal + [
                        new_empty_tile_goal
                    ]
                    queue_goal.append(
                        (new_state_goal, visited_goal[new_state_tuple_goal])
                    )

        return None  # If no solution is found

    def get_empty_tile_coordinates(self, state: list):
        empty_i = state.index(None)
        y = empty_i // self.size
        x = empty_i % self.size
        return (y, x)

    def bullshit_check_win(self, state):
        expected = list(range(1, self.size**2)) + [None]
        return state == expected

    def can_move_to(self, target: tuple) -> list[str]:
        target_y, target_x = target

        moves: list[str] = []

        if target_x > 0:
            moves.append("l")
        if target_x < self.size - 1:
            moves.append("r")

        if target_y > 0:
            moves.append("u")
        if target_y < self.size - 1:
            moves.append("d")

        return moves

    def move_to(self, state: list, directions: str):
        for direction in directions:
            index = state.index(None)
            new_index = index

            if direction == "l":
                new_index = index - 1
            elif direction == "r":
                new_index = index + 1
            elif direction == "u":
                new_index = index - self.size
            elif direction == "d":
                new_index = index + self.size

            state[index], state[new_index] = state[new_index], state[index]
        return state


class SlidingPuzzle(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sliding Puzzle")

        self.size = 3
        self.tiles = []
        self.empty_tile = (self.size - 1, self.size - 1)

        self.layout = QVBoxLayout()

        self.puzzle_frame = QGridLayout()
        self.layout.addLayout(self.puzzle_frame)

        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(ALGORITHMS)
        # Add additional algorithms here when implemented
        self.layout.addWidget(self.algorithm_selector)

        self.solve_button = QPushButton("Solve Automatically")
        self.solve_button.clicked.connect(self.solve_automatically)
        self.solve_button.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.solve_button)

        self.shuffle_button = QPushButton("Shuffle")
        self.shuffle_button.clicked.connect(self.shuffle_tiles_and_redraw)
        self.shuffle_button.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.shuffle_button)

        self.setLayout(self.layout)

        self.create_tiles()
        self.shuffle_tiles()
        self.draw_tiles()

    def create_tiles(self):
        numbers = list(range(1, self.size**2)) + [None]
        self.tiles = [
            numbers[i : i + self.size] for i in range(0, len(numbers), self.size)
        ]

    def shuffle_tiles(self):
        for _ in range(1000):
            self.move_random_tile()

    def shuffle_tiles_and_redraw(self):
        self.shuffle_tiles()
        self.draw_tiles()

    def move_random_tile(self):
        y, x = self.empty_tile
        moves = []

        if y > 0:
            moves.append((y - 1, x))  # Up
        if y < self.size - 1:
            moves.append((y + 1, x))  # Down
        if x > 0:
            moves.append((y, x - 1))  # Left
        if x < self.size - 1:
            moves.append((y, x + 1))  # Right

        if moves:
            new_x, new_y = random.choice(moves)
            self.tiles[y][x], self.tiles[new_x][new_y] = (
                self.tiles[new_x][new_y],
                self.tiles[y][x],
            )
            self.empty_tile = (new_x, new_y)

    def draw_tiles(self):
        for i in reversed(range(self.size)):
            for j in range(self.size):
                tile = self.tiles[i][j]
                button = QPushButton(str(tile) if tile is not None else "")
                button.setFixedSize(150, 150)
                button.setFont(QFont("Arial", 15))
                if tile is not None:
                    button.clicked.connect(
                        lambda checked, x=i, y=j: self.move_tile(x, y)
                    )
                self.puzzle_frame.addWidget(button, i, j)

    def move_tile(self, x, y):
        empty_x, empty_y = self.empty_tile

        if (abs(empty_x - x) == 1 and empty_y == y) or (
            empty_x == x and abs(empty_y - y) == 1
        ):
            self.tiles[empty_x][empty_y], self.tiles[x][y] = (
                self.tiles[x][y],
                self.tiles[empty_x][empty_y],
            )
            self.empty_tile = (x, y)
            self.draw_tiles()
            if self.check_win():
                mbox = CustomMessageBox("Congratulations!", "You've solved the puzzle!")
                mbox.exec_()

    def check_win(self):
        expected = list(range(1, self.size**2)) + [None]
        current = [tile for row in self.tiles for tile in row]
        return current == expected

    def solve_automatically(self):
        selected_algorithm = self.algorithm_selector.currentText()
        alg = PuzzleAlgorithms(self.size, self.tiles, self.empty_tile)

        if selected_algorithm == "BFS":
            path = alg.bfs()
            if path is not None:
                self.animate_solution(path)
            else:
                mbox = CustomMessageBox(
                    "No Solution", "Unable to solve the puzzle automatically."
                )
                mbox.exec_()
        elif selected_algorithm == "Bidirectional":
            path = alg.bidirectional()
            if path is not None:
                self.animate_solution(path)
            else:
                mbox = CustomMessageBox(
                    "No Solution", "Unable to solve the puzzle automatically."
                )
                mbox.exec_()
        else:
            mbox = CustomMessageBox(
                "Select Algorithm", "Please select a valid algorithm."
            )
            mbox.exec_()

    def animate_solution(self, path):
        # Use QTimer to animate the solution
        self.move_sequence = path
        self.move_index = 0

        # Create a timer to handle the moves
        self.timer = QTimer()
        self.timer.timeout.connect(self.perform_move)
        self.timer.start(500)  # Move every half second (500 ms)

    def perform_move(self):
        if self.move_index < len(self.move_sequence):
            self.move_tile(*self.move_sequence[self.move_index])
            self.move_index += 1
        else:
            self.timer.stop()  # Stop the timer when all moves are done


if __name__ == "__main__":
    app = QApplication(sys.argv)
    puzzle = SlidingPuzzle()
    puzzle.show()
    sys.exit(app.exec_())
