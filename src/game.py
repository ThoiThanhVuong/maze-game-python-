
import pygame
from typing import Optional, List
from src.player import Player
from src.enemy import Enemy
from src.maze_generator import MazeGenerator
from src.database import DatabaseManager
from src.UI.UIManager import UIManager
from src.UI.InputBox import InputBox
from src.UI.SkinSelector import SkinSelectorUI
from src.editor import MazeEditor
from src.untils.constants import *
from src.untils.font_manager import get_font
from src.untils.sound_manager import SoundManager

class Game:
    """Main game controller."""

    def __init__(self, screen: pygame.Surface):
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
        self.font = get_font(UI_FONT_SIZE)
        self.small_font = get_font(UI_SMALL_FONT_SIZE)
        self.large_font = get_font(UI_LARGE_FONT_SIZE)
        # Âm thanh
        self.sounds = SoundManager()

        # Form đăng nhập / đăng ký
        self.state = STATE_MENU
        self.input_username = InputBox(SCREEN_WIDTH // 2 - 150, 220, 300, 40, self.font)
        self.input_password = InputBox(SCREEN_WIDTH // 2 - 150, 280, 300, 40, self.font, password=True)
        self.login_message = ''

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            self.state = STATE_LOGIN
            self.login_message = ""

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
            result = self.editor.handle_event(event)
            if result == "exit":
                self.state = STATE_MENU


    def update(self, dt: float):
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
        self.sounds.play("select")
        self.state = STATE_PLAYING

        if self.current_user:
            self.db.update_user_progress(self.current_user['id'],1)

    def _generate_level(self):
        """Generate a new level with increasing difficulty."""
        self.maze_width = min(MIN_MAZE_SIZE + (self.level - 1) * MAZE_SIZE_INCREMENT, MAX_MAZE_SIZE)
        self.maze_height = min(MIN_MAZE_SIZE + (self.level - 1) * MAZE_SIZE_INCREMENT, MAX_MAZE_SIZE)

        generator = MazeGenerator(self.maze_width, self.maze_height)
        self.maze = generator.generate_dfs() if self.level % 2 == 1 else generator.generate_prim()

        enemy_count = BASE_ENEMY_COUNT + (self.level - 1) * ENEMY_COUNT_INCREMENT
        generator.add_enemies(enemy_count)

        # --- Tính offset để căn giữa mê cung ---
        self.maze_width_px = len(self.maze[0]) * TILE_SIZE
        self.maze_height_px = len(self.maze) * TILE_SIZE
        self.maze_offset_x = (SCREEN_WIDTH - self.maze_width_px) // 2
        self.maze_offset_y = (SCREEN_HEIGHT - UI_PANEL_HEIGHT - self.maze_height_px) // 2

        # --- Tính hệ số scale nếu mê cung lớn hơn màn hình ---
        available_width = SCREEN_WIDTH * 0.9
        available_height = (SCREEN_HEIGHT - UI_PANEL_HEIGHT) * 0.9

        scale_x = available_width / self.maze_width_px
        scale_y = available_height / self.maze_height_px
        self.scale_factor = min(1.0, scale_x, scale_y)  # chỉ thu nhỏ, không phóng to

        # --- Tạo player ---
        start_pos = self._find_cell_type(CELL_START)
        if start_pos:
            if self.current_user:
                skin_type = self.current_user.get('skin_type', 'preset')
                skin_value = self.current_user.get('skin_value', '1')

                # Nếu preset thì lấy skin_id, còn color/image thì truyền giá trị để Player xử lý
                try:
                    skin_id = int(skin_value) if skin_type == 'preset' else 1
                except Exception:
                    skin_id = 1

                # Tạo player và truyền cả skin_type + skin_value để Player._apply_skin dùng đúng
                self.player = Player(
                    start_pos[0],
                    start_pos[1],
                    skin_id,
                    custom_color=None,
                    custom_image_path=None,
                    skin_type=skin_type,
                    skin_value=str(skin_value)
                )
            else:
                # Guest / không đăng nhập => skin mặc định
                self.player = Player(start_pos[0], start_pos[1], skin_id=1)

        # --- Tạo enemy ---
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
                    return x, y
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
                self.sounds.play("explosion")

        # Update camera to follow player
        self._update_camera()

        # Check win condition (reached exit)
        exit_pos = self._find_cell_type(CELL_EXIT)
        if exit_pos and self.player.grid_x == exit_pos[0] and self.player.grid_y == exit_pos[1]:
            self.sounds.play("win")
            if self.current_user:
                self.db.update_user_progress(self.current_user['id'], self.level)
            self.state = STATE_LEVEL_COMPLETE

        # Check lose condition (health depleted)
        if not self.player.is_alive():
            self.sounds.play("game_over")
            self._save_score()
            self.state = STATE_GAME_OVER

    def _update_camera(self):
        """Update camera to follow player when maze not scaled."""
        if self.scale_factor < 1.0:
            # Khi mê cung được thu nhỏ, camera không cần di chuyển
            self.camera_x = 0
            self.camera_y = 0
            return

        # Center camera on player (theo mê cung thật)
        target_x = self.player.x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        target_y = self.player.y * TILE_SIZE - (SCREEN_HEIGHT - UI_PANEL_HEIGHT) // 2 + TILE_SIZE // 2

        # Clamp camera trong mê cung
        max_x = max(0, self.maze_width_px - SCREEN_WIDTH)
        max_y = max(0, self.maze_height_px - (SCREEN_HEIGHT - UI_PANEL_HEIGHT))

        self.camera_x = max(0, min(target_x, max_x))
        self.camera_y = max(0, min(target_y, max_y))

    def _save_score(self):
        """Save current score to database."""
        if self.current_user:
            self.db.save_score(
                self.current_user['id'],
                self.score,
                self.level
            )

    def _render_login(self):
        """Render login form with link to register."""
        self.screen.fill(BLACK)

        # Tiêu đề
        title = self.large_font.render("ĐĂNG NHẬP", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # Ô nhập username & password
        self.input_username.draw(self.screen)
        self.input_password.draw(self.screen)

        # Nút hướng dẫn
        hint = self.small_font.render("Nhấn ENTER để đăng nhập | ESC để quay lại", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 350))

        # Liên kết đăng ký
        register_hint = self.small_font.render("Chưa có tài khoản? Nhấn R để đăng ký", True, YELLOW)
        self.screen.blit(register_hint, (SCREEN_WIDTH // 2 - register_hint.get_width() // 2, 380))

        # Thông báo lỗi/thành công
        msg = self.small_font.render(self.login_message, True, GREEN if "thành công" in self.login_message else RED)
        self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 420))

    def _render_register(self):
        self.screen.fill(BLACK)
        title = self.large_font.render("REGISTER", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        self.input_username.draw(self.screen)
        self.input_password.draw(self.screen)

        note = self.small_font.render("ENTER để đăng ký | ESC để quay lại", True, GRAY)
        self.screen.blit(note, (SCREEN_WIDTH // 2 - note.get_width() // 2, 350))

        msg = self.small_font.render(self.login_message, True, YELLOW)
        self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 390))
        msg = self.small_font.render(self.login_message, True, GREEN if "thành công" in self.login_message else RED)
        self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 420))

    def apply_skin_selection(self, skin_type, skin_value):
        """Cập nhật skin cho player và lưu vào DB."""
        if self.player:
            self.player.set_skin(skin_type, skin_value)

        if self.current_user:
            self.db.update_user_skin(
                user_id=self.current_user["id"],
                skin_type=skin_type,
                skin_value=str(skin_value)
            )
            # Cập nhật thông tin trong bộ nhớ
            self.current_user["skin_type"] = skin_type
            self.current_user["skin_value"] = str(skin_value)

            # backward-compat: giữ 'skin' như một số chỗ cũ có thể dùng
            if skin_type == 'preset':
                try:
                    self.current_user['skin'] = int(skin_value)
                except Exception:
                    self.current_user['skin'] = 1
            else:
                self.current_user['skin'] = None

    # ==================== Event Handlers ====================

    def _handle_menu_event(self, event: pygame.event.Event):
        """Handle menu events."""
        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            # 1. Continue hoặc Start Game
            if event.key == pygame.K_1:
                if self.current_user:
                    last_level = self.db.get_user_progress(self.current_user['id'])
                    if last_level > 0:
                        self.level = last_level
                        self._generate_level()
                        self.state = STATE_PLAYING
                    else:
                        self.start_new_game()
                else:
                    self.state = STATE_LOGIN

            # 2. New Game
            elif event.key == pygame.K_2:
                if self.current_user:
                    self.start_new_game()
                else:
                    self.state = STATE_LOGIN

            # 3. Leaderboard
            elif event.key == pygame.K_3:
                self.state = STATE_LEADERBOARD

            # 4. Maze Editor
            elif event.key == pygame.K_4:
                if self.current_user:
                    self.editor = MazeEditor(self.screen, self.db, self.current_user)
                    self.state = STATE_EDITOR
                else:
                    self.state = STATE_LOGIN

            # 5. Select Skin (tùy chỉnh hoặc chọn ảnh)
            elif event.key == pygame.K_5:
                if self.current_user:
                    SkinSelectorUI(self.screen, self.apply_skin_selection).run()
                else:
                    self.state = STATE_LOGIN

            # 6. Logout / Login
            elif event.key == pygame.K_6:
                if self.current_user:
                    # ----- Logout -----
                    self.current_user = None
                    self.level = 1
                    self.login_message = ""

                    # Reset form login
                    self.input_username.clear()
                    self.input_password.clear()


                else:
                    # ----- Mở form Login -----
                    self.input_username.clear()
                    self.input_password.clear()
                    self.state = STATE_LOGIN
                    self.login_message = ""

            # ESC hoặc Q: Thoát game
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.should_quit = True

    def _handle_login_event(self, event: pygame.event.Event):
        """Handle login form events."""
        self.input_username.handle_event(event)
        self.input_password.handle_event(event)

        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            if event.key == pygame.K_RETURN:
                username = self.input_username.text.strip()
                password = self.input_password.text.strip()
                if not username or not password:
                    self.login_message = "Vui lòng nhập đầy đủ thông tin!"
                    return

                result = self.db.login_user(username, password)
                if result:
                    # Lưu thông tin skin một cách nhất quán
                    self.current_user = {
                        'id': result['id'],
                        'username': result['username'],
                        'skin_type': result.get('skin_type', 'preset'),
                        'skin_value': result.get('skin_value', '1'),
                        'last_level': result.get('last_level', 0)
                    }

                    # backward-compat: giữ key 'skin' nếu là preset (một số code cũ có thể dùng)
                    if self.current_user['skin_type'] == 'preset':
                        try:
                            self.current_user['skin'] = int(self.current_user['skin_value'])
                        except Exception:
                            self.current_user['skin'] = 1
                    else:
                        self.current_user['skin'] = None

                    last_level = self.current_user.get('last_level', 0)
                    self.level = last_level + 1 if last_level > 0 else 1
                    self.state = STATE_MENU
                    self.login_message = f"Đăng nhập thành công, chào {username}!"

                    # Reset form login để tránh dữ liệu cũ
                    self.input_username.clear()
                    self.input_password.clear()

                else:
                    self.login_message = "Sai tài khoản hoặc mật khẩu!"

            elif event.key == pygame.K_r:
                # Reset form khi chuyển sang đăng ký
                self.input_username.clear()
                self.input_password.clear()
                self.state = STATE_REGISTER
                self.login_message = ""

            elif event.key == pygame.K_ESCAPE:
                # Reset form khi thoát về menu
                self.input_username.clear()
                self.input_password.clear()
                self.state = STATE_MENU
                self.login_message = ""

    def _handle_register_event(self, event: pygame.event.Event):
        """Xử lý sự kiện form đăng ký tài khoản."""
        self.input_username.handle_event(event)
        self.input_password.handle_event(event)

        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            if event.key == pygame.K_RETURN:
                username = self.input_username.text.strip()
                password = self.input_password.text.strip()

                if not username or not password:
                    self.login_message = "Vui lòng nhập đầy đủ tên và mật khẩu!"
                    return

                existing_user = self.db.get_user_by_username(username)
                if existing_user:
                    self.login_message = "Tên tài khoản đã tồn tại, vui lòng chọn tên khác!"
                    return

                success = self.db.register_user(username, password)
                if success:
                    self.login_message = f"Đăng ký thành công! Chào mừng {username}!"

                    # Chuyển về login sau 1.5 giây
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
                    # Reset form sau khi đăng ký thành công
                    self.input_username.clear()
                    self.input_password.clear()
                else:
                    self.login_message = "Lỗi khi đăng ký, vui lòng thử lại sau!"

            elif event.key == pygame.K_ESCAPE:
                # Reset form khi thoát về menu
                self.input_username.text = ""
                self.input_password.text = ""
                self.state = STATE_MENU
                self.login_message = ""

    def _handle_playing_event(self, event: pygame.event.Event):
        """Handle playing state events."""
        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.state = STATE_PAUSED

    def _handle_paused_event(self, event: pygame.event.Event):
        """Handle paused state events."""
        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                self.state = STATE_PLAYING
            elif event.key == pygame.K_q:
                self.state = STATE_MENU

    def _handle_game_over_event(self, event: pygame.event.Event):
        """Handle game over events."""
        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            if event.key == pygame.K_r:
                self.start_new_game()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.state = STATE_MENU

    def _handle_level_complete_event(self, event: pygame.event.Event):
        """Handle level complete events."""
        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.next_level()

    def _handle_leaderboard_event(self, event: pygame.event.Event):
        """Handle leaderboard events."""
        if event.type == pygame.KEYDOWN:
            self.sounds.play("select")
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

    # ==================== Render Methods ====================

    def _render_menu(self):
        """Render main menu."""
        title = self.large_font.render("MAZE ADVENTURE", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        menu_items = [
            "1. Continue Game" if self.current_user and self.db.get_user_progress(self.current_user['id']) > 0 else "1. Start Game",
            "2. New Game",
            "3. Leaderboard",
            "4. Maze Editor",
            "5. Select Skin",
            "6. " + ("Logout" if self.current_user else "Login"),
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

    def _render_playing(self):
        """Render playing state (centered maze or scaled to fit)."""
        if not self.maze or not self.player:
            return

        # Nếu scale < 1 thì dùng surface trung gian
        if self.scale_factor < 1.0:
            maze_surface = pygame.Surface((self.maze_width_px, self.maze_height_px))
            maze_surface.fill(BLACK)

            # Vẽ mê cung, player, enemy vào surface
            for y in range(len(self.maze)):
                for x in range(len(self.maze[y])):
                    cell = self.maze[y][x]
                    color = None
                    if cell == CELL_WALL:
                        color = DARK_GRAY
                    elif cell == CELL_EXIT:
                        color = GREEN
                    elif cell == CELL_START:
                        color = BLUE
                    if color:
                        pygame.draw.rect(
                            maze_surface,
                            color,
                            (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        )

            # Enemy
            for enemy in self.enemies:
                enemy.render(maze_surface, (0, 0))

            # Player
            self.player.render(maze_surface, (0, 0))

            # Scale surface để vừa màn hình
            scaled_surface = pygame.transform.smoothscale(
                maze_surface,
                (int(self.maze_width_px * self.scale_factor), int(self.maze_height_px * self.scale_factor))
            )

            # Căn giữa mê cung trong màn hình
            offset_x = (SCREEN_WIDTH - scaled_surface.get_width()) // 2
            offset_y = (SCREEN_HEIGHT - UI_PANEL_HEIGHT - scaled_surface.get_height()) // 2
            self.screen.blit(scaled_surface, (offset_x, offset_y))
        else:
            # --- Trường hợp mê cung nhỏ (hiển thị full kích thước + camera theo player) ---
            self._render_maze()

            for enemy in self.enemies:
                enemy.render(self.screen, (self.camera_x - self.maze_offset_x,
                                           self.camera_y - self.maze_offset_y))
            self.player.render(self.screen, (self.camera_x - self.maze_offset_x,
                                             self.camera_y - self.maze_offset_y))

        # Render UI
        self._render_ui()

    def _render_maze(self):
        """Render the maze centered on screen."""
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                screen_x = self.maze_offset_x + x * TILE_SIZE - self.camera_x
                screen_y = self.maze_offset_y + y * TILE_SIZE - self.camera_y

                # Skip tiles ngoài màn hình
                if (screen_x < -TILE_SIZE or screen_x > SCREEN_WIDTH or
                        screen_y < -TILE_SIZE or screen_y > SCREEN_HEIGHT - UI_PANEL_HEIGHT):
                    continue

                cell = self.maze[y][x]

                if cell == CELL_WALL:
                    pygame.draw.rect(self.screen, DARK_GRAY, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, GRAY, (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
                elif cell == CELL_EXIT:
                    pygame.draw.rect(self.screen, GREEN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif cell == CELL_START:
                    pygame.draw.rect(self.screen, BLUE, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

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

        self.screen.blit(score_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 10))
        self.screen.blit(level_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - UI_PANEL_HEIGHT + 40))

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
            for i, (username, score, level) in enumerate(leaderboard):
                rank_text = f"{i + 1}. {username} - Score: {score} - Level: {level}"
                text = self.font.render(rank_text, True, WHITE if i > 0 else YELLOW)
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
                y += 40
        else:
            text = self.font.render("No scores yet!", True, GRAY)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))

        back_text = self.small_font.render("Press ESC to go back", True, GRAY)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 50))
