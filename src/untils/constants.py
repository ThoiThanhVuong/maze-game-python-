"""
Constants and Configuration
============================
Central configuration file for all game constants and settings.
"""

# Window settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Maze Adventure Game"

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Maze settings
TILE_SIZE = 32
MIN_MAZE_SIZE = 15
MAX_MAZE_SIZE = 51  # Must be odd for maze generation
MAZE_SIZE_INCREMENT = 4  # Size increase per level

# Player settings
PLAYER_SPEED = 150  # pixels per second
PLAYER_MAX_HEALTH = 100
PLAYER_START_HEALTH = 100
PLAYER_SIZE = 24

# Enemy settings
ENEMY_SPEED = 80  # pixels per second
ENEMY_SIZE = 24
ENEMY_DAMAGE = 10
ENEMY_COOLDOWN = 1.0  # seconds between damage
BASE_ENEMY_COUNT = 2
ENEMY_COUNT_INCREMENT = 1  # Enemies added per level

# Game mechanics
SCORE_PER_MOVE = 1
SCORE_PER_LEVEL = 100
SCORE_TIME_BONUS = 10  # Score per second remaining
LEVEL_TIME_LIMIT = 300  # 5 minutes per level

# UI settings
UI_PANEL_HEIGHT = 80
UI_FONT_SIZE = 24
UI_SMALL_FONT_SIZE = 18
UI_LARGE_FONT_SIZE = 36

# Database settings
DB_NAME = "data/maze_game.db"

# Maze generation algorithms
MAZE_ALGO_DFS = "dfs"
MAZE_ALGO_PRIM = "prim"

# Game states
STATE_MENU = "menu"
STATE_LOGIN = "login"
STATE_REGISTER = "register"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_LEADERBOARD = "leaderboard"
STATE_EDITOR = "editor"
STATE_SKIN_SELECT = "skin_select"

# Character skins
SKINS = [
    {"id": 1, "name": "Blue Hero", "color": BLUE},
    {"id": 2, "name": "Red Warrior", "color": RED},
    {"id": 3, "name": "Green Ranger", "color": GREEN},
    {"id": 4, "name": "Yellow Mage", "color": YELLOW},
    {"id": 5, "name": "Purple Ninja", "color": PURPLE},
    {"id": 6, "name": "Cyan Knight", "color": CYAN},
]

# Editor constants
EDITOR_TILE_EMPTY = 0
EDITOR_TILE_WALL = 1
EDITOR_TILE_START = 2
EDITOR_TILE_EXIT = 3
EDITOR_TILE_ENEMY = 4

# Cell types
CELL_WALL = 1
CELL_PATH = 0
CELL_START = 2
CELL_EXIT = 3
CELL_ENEMY = 4