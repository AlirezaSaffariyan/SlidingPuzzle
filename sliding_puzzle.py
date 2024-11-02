import random
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from algorithms import PuzzleAlgorithms

# List of available algorithms
ALGORITHMS = ["Select an algorithm", "BFS", "Bidirectional", "A*"]


class SlidingPuzzle(QWidget):
    """Main application class for the Sliding Puzzle game."""

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

        # Create a QSpinBox for selecting the solving speed
        # Lower value means faster (This is actually the delay between each move)
        self.speed_selector = QSpinBox()
        self.speed_selector.setMinimum(100)  # Maximum speed in ms
        self.speed_selector.setMaximum(1000)  # Minimum speed in ms
        self.speed_selector.setValue(500)  # Default value
        self.layout.addWidget(self.speed_selector)

        self.solve_button = QPushButton("Solve Automatically")
        self.solve_button.clicked.connect(self.solve_automatically)
        # self.solve_button.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.solve_button)

        self.shuffle_button = QPushButton("Shuffle")
        self.shuffle_button.clicked.connect(self.shuffle_tiles_and_redraw)
        # self.shuffle_button.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.shuffle_button)

        self.setLayout(self.layout)

        self.create_tiles()
        self.shuffle_tiles()
        self.draw_tiles()

    def create_tiles(self):
        """Create and initialize the tiles for the puzzle."""
        numbers = list(range(1, self.size**2)) + [None]
        self.tiles = [
            numbers[i : i + self.size] for i in range(0, len(numbers), self.size)
        ]

    def shuffle_tiles(self):
        """Shuffle the tiles by randomly moving them.
        This will prevent getting an unsolvable state.
        """
        for _ in range(1000):
            self.move_random_tile()

    def shuffle_tiles_and_redraw(self):
        """Shuffle the tiles and redraw the puzzle."""
        self.shuffle_tiles()
        self.draw_tiles()

    def move_random_tile(self):
        """Move a random tile into the empty space. Or move the empty space randomly. Think of it as you'd like:)"""
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
        """Draw the tiles on the grid."""
        for i in reversed(range(self.size)):
            for j in range(self.size):
                tile = self.tiles[i][j]
                button = QPushButton(str(tile) if tile is not None else "")
                button.setFixedSize(150, 150)
                # button.setFont(QFont("Arial", 15))
                if tile is not None:
                    button.clicked.connect(
                        lambda checked, x=i, y=j: self.move_tile(x, y)
                    )
                self.puzzle_frame.addWidget(button, i, j)

    def move_tile(self, x, y):
        """Move a tile to the empty space if possible."""
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
                mbox = QMessageBox()
                mbox.setIcon(QMessageBox.Information)
                mbox.setWindowTitle("Congratulations!")
                mbox.setText("You've solved the puzzle!")
                mbox.addButton(QMessageBox.Ok)
                mbox.exec_()

    def check_win(self):
        """Check if the current state of the puzzle is solved."""
        expected = list(range(1, self.size**2)) + [None]
        current = [tile for row in self.tiles for tile in row]
        return current == expected

    def solve_automatically(self):
        """Solve the puzzle automatically using the selected algorithm."""
        selected_algorithm = self.algorithm_selector.currentText()
        alg = PuzzleAlgorithms(self.size, self.tiles, self.empty_tile)
        path = None

        if selected_algorithm == "BFS":
            path = alg.bfs()
        elif selected_algorithm == "Bidirectional":
            path = alg.bidirectional()
        elif selected_algorithm == "A*":
            path = alg.a_star()

        # Get the speed from the spin box
        solving_speed = self.speed_selector.value()

        if path is not None:
            self.animate_solution(path, solving_speed)
        else:
            if selected_algorithm == "Select an algorithm":
                mbox = QMessageBox()
                mbox.setIcon(QMessageBox.Warning)
                mbox.setWindowTitle("Select Algorithm")
                mbox.setText("Please select a valid algorithm.")
                mbox.addButton(QMessageBox.Ok)
                mbox.exec_()
            else:
                mbox = QMessageBox()
                mbox.setIcon(QMessageBox.Critical)
                mbox.setWindowTitle("No Solution")
                mbox.setText("Unable to solve the puzzle automatically.")
                mbox.addButton(QMessageBox.Ok)
                mbox.exec_()

    def animate_solution(self, path, solving_speed):
        """Animate the solution path."""
        self.move_sequence = path
        self.move_index = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.perform_move)
        self.timer.start(solving_speed)

    def perform_move(self):
        """Perform a move from the solution path"""
        if self.move_index < len(self.move_sequence):
            self.move_tile(*self.move_sequence[self.move_index])
            self.move_index += 1
        else:
            self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont()
    font.setPointSize(20)
    app.setFont(font)
    puzzle = SlidingPuzzle()
    puzzle.show()
    sys.exit(app.exec_())
