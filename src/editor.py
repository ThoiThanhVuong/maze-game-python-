"""
Maze Editor
===========
Allows players to create and save custom mazes.
"""

import pygame
from src.untils.constants import *
from src.database import DatabaseManager


class MazeEditor:
    """Maze editor for creating custom mazes."""

    def __init__(self, screen: pygame.Surface, db: DatabaseManager, user: dict):
        """
        Initialize maze editor.

        Args:
            screen: Pygame display surface
            db: Database manager
            user: Current user data
        """
        self.screen = screen
        self.db = db
        self.user = user

        # Editor state
        self.grid_width = 21
        self.grid_height = 21
        self.cell_size = 30
        self.grid = [[EDITOR_TILE_EMPTY for _ in range(self.grid_width)]
                     for _ in range(self.grid_height)]

        # Current tool
        self.current_tool = EDITOR_TILE_WALL

        # Grid offset for scrolling
        self.offset_x = 100
        self.offset_y = 100

        # UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Mouse state
        self.is_drawing = False

        # Initialize with border walls
        self._create_border()

    def _create_border(self):
        """Create walls around the border."""
        for y in range(self.grid_height):
            self.grid[y][0] = EDITOR_TILE_WALL
            self.grid[y][self.grid_width - 1] = EDITOR_TILE_WALL

        for x in range(self.grid_width):
            self.grid[0][x] = EDITOR_TILE_WALL
            self.grid[self.grid_height - 1][x] = EDITOR_TILE_WALL

    def handle_event(self, event: pygame.event.Event):
        """
        Handle input events.

        Args:
            event: Pygame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.is_drawing = True
                self._paint_cell(event.pos)
            elif event.button == 3:  # Right click
                self._erase_cell(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_drawing = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_drawing:
                self._paint_cell(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.current_tool = EDITOR_TILE_WALL
            elif event.key == pygame.K_2:
                self.current_tool = EDITOR_TILE_EMPTY
            elif event.key == pygame.K_3:
                self.current_tool = EDITOR_TILE_START
            elif event.key == pygame.K_4:
                self.current_tool = EDITOR_TILE_EXIT
            elif event.key == pygame.K_5:
                self.current_tool = EDITOR_TILE_ENEMY
            elif event.key == pygame.K_c:
                self._clear_grid()
            elif event.key == pygame.K_s:
                self._save_maze()
            elif event.key == pygame.K_l:
                self._load_maze()

    def _paint_cell(self, mouse_pos: tuple):
        """Paint a cell at mouse position."""
        grid_x = (mouse_pos[0] - self.offset_x) // self.cell_size
        grid_y = (mouse_pos[1] - self.offset_y) // self.cell_size

        if (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            # Don't allow overwriting borders
            if (grid_x == 0 or grid_x == self.grid_width - 1 or
                    grid_y == 0 or grid_y == self.grid_height - 1):
                return

            # Special handling for start/exit (only one of each)
            if self.current_tool == EDITOR_TILE_START:
                self._clear_tile_type(EDITOR_TILE_START)
            elif self.current_tool == EDITOR_TILE_EXIT:
                self._clear_tile_type(EDITOR_TILE_EXIT)

            self.grid[grid_y][grid_x] = self.current_tool

    def _erase_cell(self, mouse_pos: tuple):
        """Erase a cell at mouse position."""
        grid_x = (mouse_pos[0] - self.offset_x) // self.cell_size
        grid_y = (mouse_pos[1] - self.offset_y) // self.cell_size

        if (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            # Don't allow erasing borders
            if (grid_x == 0 or grid_x == self.grid_width - 1 or
                    grid_y == 0 or grid_y == self.grid_height - 1):
                return

            self.grid[grid_y][grid_x] = EDITOR_TILE_EMPTY

    def _clear_tile_type(self, tile_type: int):
        """Clear all tiles of a specific type."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == tile_type:
                    self.grid[y][x] = EDITOR_TILE_EMPTY

    def _clear_grid(self):
        """Clear the entire grid."""
        self.grid = [[EDITOR_TILE_EMPTY for _ in range(self.grid_width)]
                     for _ in range(self.grid_height)]
        self._create_border()

    def _save_maze(self):
        """Save the current maze to database."""
        # Validate maze (must have start and exit)
        has_start = any(EDITOR_TILE_START in row for row in self.grid)
        has_exit = any(EDITOR_TILE_EXIT in row for row in self.grid)

        if not has_start or not has_exit:
            print("Error: Maze must have both START and EXIT tiles!")
            return

        # Generate name based on timestamp
        import time
        name = f"Custom_Maze_{int(time.time())}"

        # Save to database
        maze_id = self.db.save_custom_maze(name, self.grid, self.user['id'])
        print(f"Maze saved with ID: {maze_id}")

    def _load_maze(self):
        """Load a maze from database."""
        # Get user's mazes
        mazes = self.db.get_custom_mazes(self.user['id'])

        if mazes:
            # Load the most recent maze
            maze_id, name, data, created_by, username = mazes[0]
            loaded_grid = self.db.load_custom_maze(maze_id)

            if loaded_grid:
                self.grid = loaded_grid
                self.grid_height = len(loaded_grid)
                self.grid_width = len(loaded_grid[0])
                print(f"Loaded maze: {name}")
        else:
            print("No saved mazes found!")

    def update(self, dt: float):
        """
        Update editor state.

        Args:
            dt: Delta time
        """
        pass

    def render(self):
        """Render the editor."""
        self.screen.fill(BLACK)

        # Draw grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                screen_x = self.offset_x + x * self.cell_size
                screen_y = self.offset_y + y * self.cell_size

                # Get tile color
                tile = self.grid[y][x]
                if tile == EDITOR_TILE_WALL:
                    color = GRAY
                elif tile == EDITOR_TILE_START:
                    color = BLUE
                elif tile == EDITOR_TILE_EXIT:
                    color = GREEN
                elif tile == EDITOR_TILE_ENEMY:
                    color = RED
                else:
                    color = BLACK

                # Draw cell
                pygame.draw.rect(self.screen, color,
                                 (screen_x, screen_y, self.cell_size, self.cell_size))

                # Draw grid lines
                pygame.draw.rect(self.screen, DARK_GRAY,
                                 (screen_x, screen_y, self.cell_size, self.cell_size), 1)

        # Draw UI
        self._render_ui()

    def _render_ui(self):
        """Render UI elements."""
        # Title
        title = self.font.render("MAZE EDITOR", True, CYAN)
        self.screen.blit(title, (20, 20))

        # Tool selection
        tools = [
            (1, "Wall", GRAY),
            (2, "Path", WHITE),
            (3, "Start", BLUE),
            (4, "Exit", GREEN),
            (5, "Enemy", RED)
        ]

        y = 60
        for key, name, color in tools:
            prefix = ">> " if self.current_tool == key - 1 else "   "
            text = self.small_font.render(f"{prefix}{key}. {name}", True, color)
            self.screen.blit(text, (20, y))
            y += 25

        # Instructions
        instructions = [
            "Left Click: Paint",
            "Right Click: Erase",
            "C: Clear Grid",
            "S: Save Maze",
            "L: Load Maze",
            "ESC: Exit Editor"
        ]

        y = SCREEN_HEIGHT - 180
        for instruction in instructions:
            text = self.small_font.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(text, (20, y))
            y += 25