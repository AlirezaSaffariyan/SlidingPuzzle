import random
import sys
import time
import threading
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from algorithms import PuzzleAlgorithms
from checkable_combo_box import CheckableComboBox


ALGORITHMS = ["BFS", "Bidirectional", "A*"]


class AlgorithmRunner(QObject):
    finished = pyqtSignal(str, str, int, int)

    def __init__(self, algorithm, size, tiles, empty_tile):
        super().__init__()
        self.algorithm = algorithm
        self.size = size
        self.tiles = tiles
        self.empty_tile = empty_tile

    def run(self):
        """Run the selected algorithm and emit the statistics."""
        alg = PuzzleAlgorithms(self.size, self.tiles, self.empty_tile)

        nodes_expanded = 0
        nodes_stored = 0

        start_time = time.time()

        if self.algorithm == "BFS":
            path, nodes_expanded, nodes_stored = alg.bfs()
        elif self.algorithm == "Bidirectional":
            path, nodes_expanded, nodes_stored = alg.bidirectional()
        elif self.algorithm == "A*":
            path, nodes_expanded, nodes_stored = alg.a_star()

        end_time = time.time()

        if self.algorithm == "BFS":
            moves = len(path)
        elif self.algorithm == "Bidirectional" or self.algorithm == "A*":
            moves = len(path) - 1

        execution_time = end_time - start_time

        statistics = f"    Time: {execution_time:.4f}s\n"
        statistics += f"    Nodes Expanded: {nodes_expanded}\n"
        statistics += f"    Nodes Stored: {nodes_stored}\n"
        statistics += f"    moves: {moves}\n"

        # Emit the finished signal with the algorithm name and statistics data
        self.finished.emit(self.algorithm, statistics, nodes_expanded, nodes_stored)


class SlidingPuzzleComparison(QWidget):
    """Main application class for the Sliding Puzzle game in comparison mode."""

    def __init__(self, size: int):
        super().__init__()
        self.results = []  # List to hold the results of each algorithm comparison

        self.setWindowTitle("Sliding Puzzle - Comparison Mode")

        self.size = size
        self.tiles = []
        self.empty_tile = (self.size - 1, self.size - 1)

        self.layout = QVBoxLayout()

        self.puzzle_frame = QGridLayout()
        self.layout.addLayout(self.puzzle_frame)

        self.algorithm_selector = CheckableComboBox()
        self.algorithm_selector.addItems(ALGORITHMS)
        self.layout.addWidget(self.algorithm_selector)

        self.solve_button = QPushButton("Compare Algorithms")
        self.solve_button.clicked.connect(self.compare_algorithms)
        self.layout.addWidget(self.solve_button)

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
        """Shuffle the tiles by randomly moving them."""
        for _ in range(10000):
            self.move_random_tile()

    def move_random_tile(self):
        """Move a random tile into the empty space."""
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
            new_y, new_x = random.choice(moves)
            self.tiles[y][x], self.tiles[new_y][new_x] = (
                self.tiles[new_y][new_x],
                self.tiles[y][x],
            )
            self.empty_tile = (new_y, new_x)

    def draw_tiles(self):
        """Draw the tiles on the grid."""
        for i in reversed(range(self.size)):
            for j in range(self.size):
                tile = self.tiles[i][j]
                button = QPushButton(str(tile) if tile is not None else "")
                button.setFixedSize(100, 100)
                self.puzzle_frame.addWidget(button, i, j)

    def draw_tiles(self):
        """Draw the tiles on the grid."""
        for i in reversed(range(self.size)):
            for j in range(self.size):
                tile = self.tiles[i][j]
                button = QPushButton(str(tile) if tile is not None else "")
                button.setFixedSize(100, 100)
                self.puzzle_frame.addWidget(button, i, j)

    def compare_algorithms(self):
        """Compare different algorithms for solving the puzzle."""
        selected_algorithms = self.algorithm_selector.currentText()
        algorithms_to_compare = selected_algorithms.split(", ")

        for alg in algorithms_to_compare:
            runner = AlgorithmRunner(alg, self.size, self.tiles, self.empty_tile)
            runner.finished.connect(self.show_algorithm_statistics)
            threading.Thread(
                target=runner.run
            ).start()  # Start the algorithm in a new thread

    def show_algorithm_statistics(
        self, algorithm, statistics, nodes_expanded, nodes_stored
    ):
        """Store results of the algorithm run for later display."""
        result_string = f"{algorithm} Statistics:\n{statistics}\n"
        self.results.append(result_string)  # Store results

        # Now check if all algorithms have been processed and display results if yes
        if len(self.results) == len(self.algorithm_selector.currentText().split(", ")):
            all_results = "\n".join(self.results)
            mbox = QMessageBox()
            mbox.setIcon(QMessageBox.Information)
            mbox.setWindowTitle("Algorithms Comparison Results")
            mbox.setText(all_results)
            mbox.addButton(QMessageBox.Ok)
            mbox.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    puzzle = SlidingPuzzleComparison()
    puzzle.show()
    sys.exit(app.exec_())
