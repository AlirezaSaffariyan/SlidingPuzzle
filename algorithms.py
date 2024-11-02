import heapq
from collections import deque


class PuzzleAlgorithms:
    """Class to handle puzzle algorithms.

    Implemented algorithms:
        - BFS
        - Bidirectional
        - A*
    """

    def __init__(self, size, tiles, empty_tile):
        self.size = size
        self.tiles = tiles
        self.empty_tile = empty_tile

    def bfs(self):
        """Performs a breadth-first search to solve the puzzle."""
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
        """Performs a bidirectional search to solve the puzzle."""

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
        """Calculate the heuristic distance from the current state to the goal state."""
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
        """Performs the A* search algorithm to solve the puzzle."""

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

            empty_y, empty_x = self.get_empty_tile_coordinates(current_state, empty=0)

            for move in self.can_move_to((empty_y, empty_x)):
                new_state = list(current_state)
                self.move_to(new_state, move, empty=0)
                new_state = tuple(new_state)
                new_empty_tile = self.get_empty_tile_coordinates(new_state, empty=0)
                new_path = path + [new_empty_tile]
                new_cost = cost + 1

                if new_state not in reached or new_cost < reached[new_state][2]:
                    reached[new_state] = (new_state, new_path, new_cost)
                    f = new_cost + self.heuristic(new_state, goal_state)
                    heapq.heappush(frontier, (f, (new_state, new_path, new_cost)))

        return None  # If no solution is found

    def get_empty_tile_coordinates(self, state: list, empty=None):
        """Get the coordinates of the empty tile (represented by 0 or None)."""
        empty_i = state.index(empty)
        y = empty_i // self.size
        x = empty_i % self.size
        return (y, x)

    def is_solved(self, state):
        """Check if the puzzle is in the solved state."""
        expected = list(range(1, self.size**2)) + [None]
        return state == expected

    def can_move_to(self, target: tuple) -> list[str]:
        """Get a list of possible moves from the current empty tile position."""
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
        """Move the empty tile in the specified direction."""
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
