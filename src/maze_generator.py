
import random
from typing import List, Tuple
from src.untils.constants import (
    CELL_WALL, CELL_PATH, CELL_START, CELL_EXIT, CELL_ENEMY
)


class MazeGenerator:
    """Generates random mazes using DFS or Prim's algorithm."""

    def __init__(self, width: int, height: int):
        """
        Initialize maze generator.

        Args:
            width: Maze width (must be odd)
            height: Maze height (must be odd)
        """
        # Ensure dimensions are odd
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.maze = [[CELL_WALL for _ in range(self.width)] for _ in range(self.height)]

    def generate_dfs(self) -> List[List[int]]:
        """
        Generate maze using Depth-First Search (DFS) algorithm.

        Returns:
            2D list representing the maze
        """
        # Start from position (1, 1)
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = CELL_PATH

        # DFS stack
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]

            # Get unvisited neighbors (2 cells away)
            neighbors = self._get_unvisited_neighbors(x, y)

            if neighbors:
                # Choose random neighbor
                nx, ny = random.choice(neighbors)

                # Remove wall between current and neighbor
                wall_x = x + (nx - x) // 2
                wall_y = y + (ny - y) // 2
                self.maze[wall_y][wall_x] = CELL_PATH
                self.maze[ny][nx] = CELL_PATH

                stack.append((nx, ny))
            else:
                stack.pop()

        # Set start and exit
        self._set_start_and_exit()

        return self.maze

    def generate_prim(self) -> List[List[int]]:
        """
        Generate maze using Prim's algorithm.

        Returns:
            2D list representing the maze
        """
        # Start from random position
        start_x = random.randrange(1, self.width, 2)
        start_y = random.randrange(1, self.height, 2)
        self.maze[start_y][start_x] = CELL_PATH

        # List of walls to consider
        walls = self._get_surrounding_walls(start_x, start_y)

        while walls:
            # Pick random wall
            wall_x, wall_y = random.choice(walls)
            walls.remove((wall_x, wall_y))

            # Check if wall separates visited and unvisited cells
            neighbors = self._get_wall_neighbors(wall_x, wall_y)
            visited = [n for n in neighbors if self.maze[n[1]][n[0]] == CELL_PATH]
            unvisited = [n for n in neighbors if self.maze[n[1]][n[0]] == CELL_WALL]

            if len(visited) == 1 and len(unvisited) == 1:
                # Remove wall
                self.maze[wall_y][wall_x] = CELL_PATH

                # Mark unvisited cell as path
                ux, uy = unvisited[0]
                self.maze[uy][ux] = CELL_PATH

                # Add new walls
                new_walls = self._get_surrounding_walls(ux, uy)
                for w in new_walls:
                    if w not in walls and self.maze[w[1]][w[0]] == CELL_WALL:
                        walls.append(w)

        # Set start and exit
        self._set_start_and_exit()

        return self.maze

    def _get_unvisited_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get unvisited neighbors 2 cells away in cardinal directions."""
        neighbors = []
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Up, Right, Down, Left

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 < nx < self.width - 1 and
                    0 < ny < self.height - 1 and
                    self.maze[ny][nx] == CELL_WALL):
                neighbors.append((nx, ny))

        return neighbors

    def _get_surrounding_walls(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get walls surrounding a cell."""
        walls = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        for dx, dy in directions:
            wx, wy = x + dx, y + dy
            if (0 < wx < self.width - 1 and
                    0 < wy < self.height - 1):
                walls.append((wx, wy))

        return walls

    def _get_wall_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get cells on either side of a wall."""
        neighbors = []

        # Check if horizontal or vertical wall
        if x % 2 == 0:  # Vertical wall
            if x > 0:
                neighbors.append((x - 1, y))
            if x < self.width - 1:
                neighbors.append((x + 1, y))
        else:  # Horizontal wall
            if y > 0:
                neighbors.append((x, y - 1))
            if y < self.height - 1:
                neighbors.append((x, y + 1))

        return neighbors

    def _set_start_and_exit(self):
        """Set start position at top-left and exit at bottom-right."""
        # Find suitable start position (top-left area)
        for y in range(1, self.height // 3):
            for x in range(1, self.width // 3):
                if self.maze[y][x] == CELL_PATH:
                    self.maze[y][x] = CELL_START
                    break
            else:
                continue
            break

        # Find suitable exit position (bottom-right area)
        for y in range(self.height - 2, 2 * self.height // 3, -1):
            for x in range(self.width - 2, 2 * self.width // 3, -1):
                if self.maze[y][x] == CELL_PATH:
                    self.maze[y][x] = CELL_EXIT
                    return

    def add_enemies(self, count: int):
        """
        Add enemy spawn points to the maze.

        Args:
            count: Number of enemies to add
        """
        path_cells = []

        # Find all path cells (excluding start and exit)
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == CELL_PATH:
                    path_cells.append((x, y))

        # Randomly place enemies
        if path_cells:
            enemy_positions = random.sample(path_cells, min(count, len(path_cells)))
            for x, y in enemy_positions:
                self.maze[y][x] = CELL_ENEMY

    def get_maze(self) -> List[List[int]]:
        """Return the generated maze."""
        return self.maze