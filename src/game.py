
import pygame
from typing import Optional, List
from src.player import Player
from src.enemy import Enemy
from src.maze_generator import MazeGenerator
from src.database import DatabaseManager
from src.ui import UIManager
from src.editor import MazeEditor
from src.untils.constants import *


class Game:
    """Main game controller."""

    def __init__(self, screen: pygame.Surface):
        """
        Initialize game.

        Args:
            screen: Main pygame display surface
        """
        self.screen = screen
        self.should_quit = False

        # Database
        self.db = DatabaseManager()

        # UI Manager
        self.ui = UIManager(screen)

        # Game state
        self.state = STATE_MENU
        self.current_user = None

        # Gameplay
        self.level = 1
        self.score = 0
        self.time_elapsed = 0
        self.maze = None
        self.player = None
        self.enemies = []
        self.maze_width = MIN_MAZE_SIZE
        self.maze_height = MIN_MAZE_SIZE

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Editor
        self.editor = None

        # Fonts
        self.font = pygame.font.Font(None, UI_FONT_SIZE)
        self.small_font = pygame.font.Font(None, UI_SMALL_FONT_SIZE)
        self.large_font = pygame.font.Font(None, UI_LARGE_FONT_SIZE)

    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events.

        Args:
            event: Pygame event
        """
        if self.state == STATE_MENU:
            self._handle_menu_event(event)
        elif self.state == STATE_LOGIN:
            self._handle_login_event(event)
        elif self.state == STATE_REGISTER:
            self._handle_register_event(event)
        elif self.state == STATE_PLAYING:
            self._handle_playing_event(event)
        elif self.state == STATE_PAUSED:
            self._handle_paused_event(event)
        elif self.state == STATE_GAME_OVER:
            self._handle_game_over_event(event)
        elif self.state == STATE_LEVEL_COMPLETE:
            self._handle_level_complete_event(event)
        elif self.state == STATE_LEADERBOARD:
            self._handle_leaderboard_event(event)
        elif self.state == STATE_EDITOR:
            if self.editor:
                self.editor.handle_event(event)
        elif self.state == STATE_SKIN_SELECT:
            self._handle_skin_select_event(event)

    def update(self, dt: float):
        """
        Update game state.

        Args:
            dt: Delta time in seconds
        """
        if self.state == STATE_PLAYING:
            self._update_playing(dt)
        elif self.state == STATE_EDITOR:
            if self.editor:
                self.editor.update(dt)

    def render(self):
        """Render current game state."""
        self.screen.fill(BLACK)

        if self.state == STATE_MENU:
            self._render_menu()
        elif self.state == STATE_LOGIN:
            self._render_login()
        elif self.state == STATE_REGISTER:
            self._render_register()
        elif self.state == STATE_PLAYING:
            self._render_playing()
        elif self.state == STATE_PAUSED:
            self._render_paused()
        elif self.state == STATE_GAME_OVER:
            self._render_game_over()
        elif self.state == STATE_LEVEL_COMPLETE:
            self._render_level_complete()
        elif self.state == STATE_LEADERBOARD:
            self._render_leaderboard()
        elif self.state == STATE_EDITOR:
            if self.editor:
                self.editor.render()
        elif self.state == STATE_SKIN_SELECT:
            self._render_skin_select()

    def cleanup(self):
        """Cleanup resources."""
        self.db.close()

    # ==================== Game State Methods ====================

    def start_new_game(self):
        """Start a new game from level 1."""
        self.level = 1
        self.score = 0
        self.time_elapsed = 0
        self._generate_level()
        self.state = STATE_PLAYING

    def _generate_level(self):
        """Generate a new level with increasing difficulty."""
        # Calculate maze size based on level
        self.maze_width = min(MIN_MAZE_SIZE + (self.level - 1) * MAZE_SIZE_INCREMENT, MAX_MAZE_SIZE)
        self.maze_height = min(MIN_MAZE_SIZE + (self.level - 1) * MAZE_SIZE_INCREMENT, MAX_MAZE_SIZE)

        # Generate maze
        generator = MazeGenerator(self.maze_width, self.maze_height)

        # Alternate between algorithms
        if self.level % 2 == 1:
            self.maze = generator.generate_dfs()
        else:
            self.maze = generator.generate_prim()

        # Add enemies based on level
        enemy_count = BASE_ENEMY_COUNT + (self.level - 1) * ENEMY_COUNT_INCREMENT
        generator.add_enemies(enemy_count)

        # Initialize player at start position
        start_pos = self._find_cell_type(CELL_START)
        if start_pos:
            skin_id = self.current_user['skin'] if self.current_user else 1
            self.player = Player(start_pos[0], start_pos[1], skin_id)

        # Initialize enemies
        self.enemies = []
        enemy_positions = self._find_all_cell_type(CELL_ENEMY)
        for ex, ey in enemy_positions:
            self.enemies.append(Enemy(ex, ey))

    def next_level(self):
        """Progress to next level."""
        self.level += 1
        self.score += SCORE_PER_LEVEL
        self._generate_level()
        self.state = STATE_PLAYING

    def _find_cell_type(self, cell_type: int) -> Optional[tuple]:
        """Find first cell of given type."""
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                if self.maze[y][x] == cell_type:
                    return (x, y)
        return None

    def _find_all_cell_type(self, cell_type: int) -> List[tuple]:
        """Find all cells of given type."""
        cells = []
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                if self.maze[y][x] == cell_type:
                    cells.append((x, y))
        return cells

    # ==================== Update Methods ====================

    def _update_playing(self, dt: float):
        """Update playing state."""
        if not self.player or not self.maze:
            return

        # Update timer
        self.time_elapsed += dt

        # Handle input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # Update player
        self.player.update(dt, self.maze)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.maze, (self.player.x, self.player.y))

            # Check collision with player
            if enemy.check_collision_with_player(self.player):
                enemy.attack(self.player)

        # Update camera to follow player
        self._update_camera()

        # Check win condition (reached exit)
        exit_pos = self._find_cell_type(CELL_EXIT)
        if exit_pos and self.player.grid_x == exit_pos[0] and self.player.grid_y == exit_pos[1]:
            self.state = STATE_LEVEL_COMPLETE

        # Check lose condition (health depleted)
        if not self.player.is_alive():
            self._save_score()
            self.state = STATE_GAME_OVER

    def _update_camera(self):
        """Update camera to follow player."""
        # Center camera on player
        target_x = self.player.x - SCREEN_WIDTH // 2
        target_y = self.player.y - (SCREEN_HEIGHT - UI_PANEL_HEIGHT) // 2

        # Clamp camera to maze bounds
        max_x = len(self.maze[0]) * TILE_SIZE - SCREEN_WIDTH
        max_y = len(self.maze) * TILE_SIZE - (SCREEN_HEIGHT - UI_PANEL_HEIGHT)

        self.camera_x = max(0, min(target_x, max_x))
        self.camera_y = max(0, min(target_y, max_y))

    def _save_score(self):
        """Save current score to database."""
        if self.current_user:
            self.db.save_score(
                self.current_user['id'],
                self.score,
                self.level,
                self.time_elapsed
            )

    # ==================== Event Handlers ====================

    def _handle_menu_event(self, event: pygame.event.Event):
        """Handle menu events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if self.current_user:
                    self.start_new_game()
                else:
                    self.state = STATE_LOGIN
            elif event.key == pygame.K_2:
                self.state = STATE_LEADERBOARD
            elif event.key == pygame.K_3:
                if self.current_user:
                    self.editor = MazeEditor(self.screen, self.db, self.current_user)
                    self.state = STATE_EDITOR
                else:
                    self.state = STATE_LOGIN
            elif event.key == pygame.K_4:
                if self.current_user:
                    self.state = STATE_SKIN_SELECT
                else:
                    self.state = STATE_LOGIN
            elif event.key == pygame.K_5:
                if self.current_user:
                    self.current_user = None
                else:
                    self.state = STATE_LOGIN
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.should_quit = True

    def _handle_login_event(self, event: pygame.event.Event):
        """Handle login screen events."""
        # Simplified - in real implementation, would have text input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            elif event.key == pygame.K_1:
                # Demo: Auto-login as guest
                result = self.db.login_user("guest", "guest")
                if not result:
                    self.db.register_user("guest", "guest")
                    result = self.db.login_user("guest", "guest")
                self.current_user = result
                self.state = STATE_MENU
            elif event.key == pygame.K_2:
                self.state = STATE_REGISTER

    def _handle_register_event(self, event: pygame.event.Event):
        """Handle registration events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_LOGIN

    def _handle_playing_event(self, event: pygame.event.Event):
        """Handle playing state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.state = STATE_PAUSED

    def _handle_paused_event(self, event: pygame.event.Event):
        """Handle paused state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.state = STATE_PLAYING
            elif event.key == pygame.K_q:
                self.state = STATE_MENU

    def _handle_game_over_event(self, event: pygame.event.Event):
        """Handle game over events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.start_new_game()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.state = STATE_MENU

    def _handle_level_complete_event(self, event: pygame.event.Event):
        """Handle level complete events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.next_level()

    def _handle_leaderboard_event(self, event: pygame.event.Event):
        """Handle leaderboard events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

    def _handle_skin_select_event(self, event: pygame.event.Event):
        """Handle skin selection events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            elif pygame.K_1 <= event.key <= pygame.K_6:
                skin_id = event.key - pygame.K_0
                if skin_id <= len(SKINS):
                    self.current_user['skin'] = skin_id
                    self.db.update_user_skin(self.current_user['id'], skin_id)

    # ==================== Render Methods ====================

    def _render_menu(self):
        """Render main menu."""
        title = self.large_font.render("MAZE ADVENTURE", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        menu_items = [
            "1. Start Game",
            "2. Leaderboard",
            "3. Maze Editor",
            "4. Select Skin",
            "5. " + ("Logout" if self.current_user else "Login"),
            "ESC. Quit"
        ]

        y = 250
        for item in menu_items:
            text = self.font.render(item, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 50

        if self.current_user:
            user_text = self.small_font.render(
                f"Logged in as: {self.current_user['username']}",
                True, GREEN
            )
            self.screen.blit(user_text, (20, SCREEN_HEIGHT - 40))

    def _render_login(self):
        """Render login screen."""
        title = self.large_font.render("LOGIN", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        text1 = self.font.render("1. Login as Guest", True, WHITE)
        text2 = self.font.render("2. Register New Account", True, WHITE)
        text3 = self.font.render("ESC. Back to Menu", True, GRAY)

        self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, 250))
        self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, 320))
        self.screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, 450))

    def _render_register(self):
        """Render registration screen."""
        title = self.large_font.render("REGISTER", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        info = self.small_font.render("Registration feature - press ESC to go back", True, GRAY)
        self.screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 300))

    def _render_playing(self):
        """Render playing state."""
        if not self.maze or not self.player:
            return

        # Render maze
        self._render_maze()

        # Render enemies
        for enemy in self.enemies:
            enemy.render(self.screen, (self.camera_x, self.camera_y))

        # Render player
        self.player.render(self.screen, (self.camera_x, self.camera_y))

        # Render UI
        self._render_ui()

    def _render_maze(self):
        """Render the maze."""
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y

                # Skip tiles outside screen
                if (screen_x < -TILE_SIZE or screen_x > SCREEN_WIDTH or
                        screen_y < -TILE_SIZE or screen_y > SCREEN_HEIGHT - UI_PANEL_HEIGHT):
                    continue

                cell = self.maze[y][x]

                if cell == CELL_WALL:
                    pygame.draw.rect(self.screen, DARK_GRAY,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, GRAY,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
                elif cell == CELL_EXIT:
                    pygame.draw.rect(self.screen, GREEN,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif cell == CELL_START:
                    pygame.draw.rect(self.screen, BLUE,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

    def _render_ui(self):
        """Render UI elements."""
        # UI Panel background
        pygame.draw.rect(self.screen, DARK_GRAY,
                         (0, SCREEN_HEIGHT - UI_PANEL_HEIGHT, SCREEN_WIDTH, UI_PANEL_HEIGHT))

        # Health bar
        health_text = self.small_font.render("Health:", True, WHITE)
        self.screen.blit(health_text, (20, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 10))

        health_bar_width = 200
        health_bar_height = 20
        health_percent = self.player.health / self.player.max_health

        pygame.draw.rect(self.screen, RED,
                         (20, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 35, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, GREEN,
                         (20, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 35,
                          int(health_bar_width * health_percent), health_bar_height))
        pygame.draw.rect(self.screen, WHITE,
                         (20, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 35, health_bar_width, health_bar_height), 2)

        # Score and Level
        score_text = self.font.render(f"Score: {self.score}", True, YELLOW)
        level_text = self.font.render(f"Level: {self.level}", True, CYAN)
        time_text = self.small_font.render(f"Time: {int(self.time_elapsed)}s", True, WHITE)

        self.screen.blit(score_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 10))
        self.screen.blit(level_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 40))
        self.screen.blit(time_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 30))

    def _render_paused(self):
        """Render paused overlay."""
        self._render_playing()

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Paused text
        text = self.large_font.render("PAUSED", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        text2 = self.font.render("Press P or ESC to Resume", True, GRAY)
        self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        text3 = self.font.render("Press Q to Quit to Menu", True, GRAY)
        self.screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def _render_game_over(self):
        """Render game over screen."""
        title = self.large_font.render("GAME OVER", True, RED)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        score_text = self.font.render(f"Final Score: {self.score}", True, YELLOW)
        level_text = self.font.render(f"Reached Level: {self.level}", True, CYAN)

        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 300))

        restart_text = self.font.render("Press R to Restart", True, GREEN)
        menu_text = self.font.render("Press Q for Menu", True, GRAY)

        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 450))

    def _render_level_complete(self):
        """Render level complete screen."""
        title = self.large_font.render("LEVEL COMPLETE!", True, GREEN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        level_text = self.font.render(f"Level {self.level} Completed!", True, CYAN)
        score_text = self.font.render(f"Score: {self.score}", True, YELLOW)

        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 250))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

        continue_text = self.font.render("Press SPACE to Continue", True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 400))

    def _render_leaderboard(self):
        """Render leaderboard."""
        title = self.large_font.render("LEADERBOARD", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Get leaderboard data
        leaderboard = self.db.get_leaderboard(10)

        y = 150
        if leaderboard:
            for i, (username, score, level, time_played) in enumerate(leaderboard):
                rank_text = f"{i + 1}. {username} - Score: {score} - Level: {level}"
                text = self.font.render(rank_text, True, WHITE if i > 0 else YELLOW)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
                y += 40
        else:
            text = self.font.render("No scores yet!", True, GRAY)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))

        back_text = self.small_font.render("Press ESC to go back", True, GRAY)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 50))

    def _render_skin_select(self):
        """Render skin selection screen."""
        title = self.large_font.render("SELECT SKIN", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        y = 150
        for skin in SKINS:
            prefix = ">> " if self.current_user and self.current_user['skin'] == skin['id'] else "   "
            text = self.font.render(f"{prefix}{skin['id']}. {skin['name']}", True, skin['color'])
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 50

        instruction = self.small_font.render("Press 1-6 to select skin, ESC to go back", True, GRAY)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 50))