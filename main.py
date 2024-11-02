import heapq
import random
import sys
from collections import deque

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

ALGORITHMS = ["Select an algorithm", "BFS", "Bidirectional", "A*"]


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
        initial_state = [tile for row in self.tiles for tile in row]
        initial_empty_tile = self.get_empty_tile_coordinates(initial_state)

        queue = deque([(initial_state, [])])
        visited = set()
        visited.add(tuple(initial_state))

        while queue:
            current_state, path = queue.popleft()
            empty_y, empty_x = self.get_empty_tile_coordinates(current_state)

            if self.is_solved(current_state):
                return path

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
        # Flatten the initial state and generate goal state
        initial_state = [tile for row in self.tiles for tile in row]
        goal_state = list(range(1, self.size**2)) + [None]

        start_empty = self.get_empty_tile_coordinates(initial_state)

        # Initialize queues for forward and backward search
        forward_queue = deque([(initial_state, [start_empty])])
        backward_queue = deque([(goal_state, [(2, 2)])])

        forward_visited = {tuple(initial_state): []}
        backward_visited = {tuple(goal_state): []}

        while forward_queue and backward_queue:
            # Forward BFS step
            if forward_queue:
                f_state, f_path = forward_queue.popleft()
                f_empty_y, f_empty_x = self.get_empty_tile_coordinates(f_state)

                if tuple(f_state) in backward_visited:
                    return f_path[:-1] + backward_visited[tuple(f_state)][::-1]

                for move in self.can_move_to((f_empty_y, f_empty_x)):
                    new_state = f_state[:]
                    self.move_to(new_state, move)
                    new_empty_tile = self.get_empty_tile_coordinates(new_state)
                    new_state_tuple = tuple(new_state)

                    if new_state_tuple not in forward_visited:
                        new_path = f_path + [new_empty_tile]
                        forward_visited[new_state_tuple] = new_path
                        forward_queue.append((new_state, new_path))

            # Backward BFS step
            if backward_queue:
                b_state, b_path = backward_queue.popleft()
                b_empty_y, b_empty_x = self.get_empty_tile_coordinates(b_state)

                if tuple(b_state) in forward_visited:
                    return forward_visited[tuple(b_state)][:-1] + b_path[::-1]

                for move in self.can_move_to((b_empty_y, b_empty_x)):
                    new_state = b_state[:]
                    self.move_to(new_state, move)
                    new_empty_tile = self.get_empty_tile_coordinates(new_state)
                    new_state_tuple = tuple(new_state)

                    if new_state_tuple not in backward_visited:
                        new_path = b_path + [new_empty_tile]
                        backward_visited[new_state_tuple] = new_path
                        backward_queue.append((new_state, new_path))

        return None  # If no solution is found

    def heuristic(self, state, goal_state):
        distance = 0
        for i, tile in enumerate(state):
            if tile is None:
                continue  # Skip the empty tile
            if tile in goal_state:
                goal_index = goal_state.index(tile)
                goal_y, goal_x = divmod(goal_index, self.size)
                current_y, current_x = divmod(i, self.size)
                distance += abs(goal_y - current_y) + abs(goal_x - current_x)
            else:
                distance += self.size  # This could be adjusted based on requirements
        return distance

    def a_star(self):
        # Replace None with 0 to prevent:
        # TypeError: '<' not supported between instances of 'NoneType' and 'int'
        # While trying to compare list items for pushing to the heapq or popping from it
        initial_state = tuple(
            tile if tile is not None else 0 for row in self.tiles for tile in row
        )

        # Use 0 instead of None for the reason above
        # goal_state = tuple(range(1, self.size**2)) + (None,)
        goal_state = tuple(range(1, self.size**2)) + (0,)

        start_node = (initial_state, [self.empty_tile], 0)
        frontier = [(self.heuristic(initial_state, goal_state), start_node)]
        reached = {initial_state: start_node}

        while frontier:
            _, node = heapq.heappop(frontier)
            current_state, path, cost = node

            if current_state == goal_state:
                return path

            empty_y, empty_x = self.get_empty_tile_coordinates(current_state)

            for move in self.can_move_to((empty_y, empty_x)):
                new_state = list(current_state)
                self.move_to(new_state, move, empty=0)
                new_state = tuple(new_state)
                new_empty_tile = self.get_empty_tile_coordinates(new_state)
                new_path = path + [new_empty_tile]
                new_cost = cost + 1

                if new_state not in reached or new_cost < reached[new_state][2]:
                    reached[new_state] = (new_state, new_path, new_cost)
                    f = new_cost + self.heuristic(new_state, goal_state)
                    heapq.heappush(frontier, (f, (new_state, new_path, new_cost)))

        return None  # If no solution is found

    def get_empty_tile_coordinates(self, state: list):
        empty_i = state.index(0)
        y = empty_i // self.size
        x = empty_i % self.size
        return (y, x)

    def is_solved(self, state):
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

    def move_to(self, state: list, directions: str, empty=None):
        for direction in directions:
            index = state.index(empty)
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
        path = None

        if selected_algorithm == "BFS":
            path = alg.bfs()
        elif selected_algorithm == "Bidirectional":
            path = alg.bidirectional()
        elif selected_algorithm == "A*":
            path = alg.a_star()

        if path is not None:
            self.animate_solution(path)
        else:
            if selected_algorithm == "Select an algorithm":
                mbox = CustomMessageBox(
                    "Select Algorithm", "Please select a valid algorithm."
                )
                mbox.exec_()
            else:
                mbox = CustomMessageBox(
                    "No Solution", "Unable to solve the puzzle automatically."
                )
                mbox.exec_()

    def animate_solution(self, path):
        self.move_sequence = path
        self.move_index = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.perform_move)
        self.timer.start(500)

    def perform_move(self):
        if self.move_index < len(self.move_sequence):
            self.move_tile(*self.move_sequence[self.move_index])
            self.move_index += 1
        else:
            self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    puzzle = SlidingPuzzle()
    puzzle.show()
    sys.exit(app.exec_())
