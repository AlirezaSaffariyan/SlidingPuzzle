# Sliding Puzzle Solver

## Overview

The **Sliding Puzzle Solver** is a Python-based application that allows users to solve sliding puzzles using various algorithms. The project is built using the PyQt5 framework for the graphical user interface (GUI) and includes implementations of popular search algorithms such as **BFS (Breadth-First Search)**, **Bidirectional Search**, and **A\***. The application supports two modes: **Normal Mode** and **Comparison Mode**, allowing users to either solve a single puzzle or compare the performance of different algorithms.

## Features

- **Normal Mode**: Solve a sliding puzzle manually or automatically using a selected algorithm.
- **Comparison Mode**: Compare the performance of multiple algorithms in solving the same puzzle.
- **Algorithms**:
  - **BFS (Breadth-First Search)**
  - **Bidirectional Search**
  - **A\*** (A-Star)
- **Customizable Puzzle Size**: The puzzle size can be adjusted (default is 3x3).
- **Shuffle Functionality**: Randomly shuffle the puzzle to create a new challenge.
- **Automatic Solving**: Besides being able to play the game by yourself, the app can automatically solve the puzzle using the selected algorithm.
- **Performance Metrics**: View detailed statistics such as execution time, nodes expanded, nodes stored, and number of moves for each algorithm.

## Installation

To run the Sliding Puzzle Solver, follow these steps:

1. **Clone the Repository**:

```bash
git clone https://github.com/your-username/sliding-puzzle-solver.git
cd sliding-puzzle-solver
```

2. **Install Dependencies**: Ensure you have Python 3.x installed. Then, install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

3. **Run the Application**: Execute the main script to start the application:

```bash
python sliding_puzzle.py
```

## Usage

### Normal Mode

- **Start the Application**: The application will open in **Normal Mode** by default.
- **Shuffle the Puzzle**: Click the **Shuffle** button to randomize the puzzle.
- **Solve Manually**: Click on the tiles adjacent to the empty space to move them.
- **Solve Automatically**:
  - Select an algorithm from the dropdown menu.
  - Click the **Solve Automatically** button to let the algorithm solve the puzzle.
  - Adjust the solving speed using the speed selector.

### Comparison Mode

- **Switch to Comparison Mode**: Click the **Comparison Mode** button on the main screen.
- **Select Algorithms**: Use the checkable combo box to select the algorithms you want to compare.
- **Compare Algorithms**: Click the **Compare Algorithms** button to run the selected algorithms and view their performance statistics.

### Code Structure

The project is organized into several Python files:

- `sliding_puzzle.py`: The main entry point of the application. Contains the GUI and logic for **Normal Mode**.
- `comparison_mode.py`: Contains the GUI and logic for **Comparison Mode**.
- `algorithms.py`: Implements the puzzle-solving algorithms (BFS, Bidirectional, A\*).
- `checkable_combo_box.py`: A custom PyQt5 widget for selecting multiple algorithms in **Comparison Mode**.
- `requirements.txt`: Lists the required Python packages (PyQt5).

### Algorithms

#### BFS (Breadth-First Search)

- **Description**: Explores all possible moves level by level until the goal state is reached.
- **Performance**: Guaranteed to find the shortest path but may be slow for larger puzzles due to high memory usage.

#### Bidirectional Search

- **Description**: Simultaneously searches from the initial state and the goal state, meeting in the middle.
- **Performance**: Often faster than BFS and uses less memory, but requires more complex implementation.

#### A\* (A-Star)

- **Description**: Uses a heuristic function to estimate the cost to reach the goal, prioritizing paths with lower estimated costs.
- **Performance**: Efficient and often finds the shortest path quickly, especially with a good heuristic.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
