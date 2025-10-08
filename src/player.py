import pygame
import os
from typing import Tuple, Optional
from src.untils.constants import (
    PLAYER_SPEED, PLAYER_MAX_HEALTH, PLAYER_SIZE,
    TILE_SIZE, CELL_WALL, SKINS
)
from src.untils.sound_manager import SoundManager

class Player:
    def __init__(
        self,
        x: int,
        y: int,
        skin_id: int = 1,
        custom_color: Optional[Tuple[int, int, int]] = None,
        custom_image_path: Optional[str] = None,
        skin_type: str = "preset",
        skin_value: str = "1"
    ):
        # ======= Vị trí và kích thước =======
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED

        # ======= Hệ thống máu =======
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH

        # ======= Thông tin skin =======
        self.skin_type = skin_type
        self.skin_value = skin_value
        self.skin_id = skin_id
        self.custom_color = custom_color
        self.custom_image_path = custom_image_path

        # Tạo skin ngay từ khi khởi tạo
        self.image = None
        self.color = (255, 255, 255)
        self._apply_skin()

        # ======= Di chuyển =======
        self.velocity_x = 0
        self.velocity_y = 0
        self.sound = SoundManager()

        # ======= Thời gian miễn thương =======
        self.damage_cooldown = 0
        self.invulnerable_time = 0.5  # seconds

    # ==================== SKIN ====================
    def _apply_skin(self):
        """Áp dụng loại skin hiện tại."""
        if self.skin_type == "preset":
            # Theo ID trong SKINS
            try:
                skin_id = int(self.skin_value)
                self.color = SKINS[skin_id - 1]["color"]
            except Exception:
                self.color = SKINS[0]["color"]
            self.image = None

        elif self.skin_type == "color":
            try:
                rgb = eval(self.skin_value) if isinstance(self.skin_value, str) else (255, 255, 255)
                self.color = tuple(map(int, rgb))
            except Exception:
                self.color = (255, 255, 255)
            self.image = None

        elif self.skin_type == "image":
            if self.custom_image_path and os.path.exists(self.custom_image_path):
                try:
                    img = pygame.image.load(self.custom_image_path).convert_alpha()
                    img = pygame.transform.scale(img, (self.size, self.size))
                    self.image = img
                except Exception as e:
                    print(f"[Warning] Could not load custom skin image: {e}")
                    self.image = None
            else:
                # Trường hợp skin_value là đường dẫn ảnh
                if os.path.exists(self.skin_value):
                    try:
                        img = pygame.image.load(self.skin_value).convert_alpha()
                        img = pygame.transform.scale(img, (self.size, self.size))
                        self.image = img
                    except Exception as e:
                        print(f"[Warning] Could not load custom skin image: {e}")
                        self.image = None
                else:
                    self.image = None
                    self.color = (255, 255, 255)

    def set_skin(self, skin_type="preset", skin_value="1"):
        """Thay đổi skin khi người chơi chọn ở menu."""
        self.skin_type = skin_type
        self.skin_value = skin_value
        self._apply_skin()

    # ==================== INPUT ====================
    def handle_input(self, keys: pygame.key.ScancodeWrapper):
        """Xử lý bàn phím để điều khiển nhân vật."""
        self.velocity_x = 0
        self.velocity_y = 0

        # Di chuyển bằng mũi tên hoặc WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = 1

        # Di chuyển chéo chậm lại cho mượt
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.sound.play("move")
            self.velocity_x *= 0.707
            self.velocity_y *= 0.707

    # ==================== UPDATE ====================
    def update(self, dt: float, maze: list):
        """Cập nhật trạng thái nhân vật."""
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        # Tính toán vị trí mới
        new_x = self.x + self.velocity_x * self.speed * dt
        new_y = self.y + self.velocity_y * self.speed * dt

        # Kiểm tra va chạm
        if not self._check_collision(new_x, self.y, maze):
            self.x = new_x
        if not self._check_collision(self.x, new_y, maze):
            self.y = new_y

        # Cập nhật vị trí trên grid
        self.grid_x = int(self.x // TILE_SIZE)
        self.grid_y = int(self.y // TILE_SIZE)

    def _check_collision(self, x: float, y: float, maze: list) -> bool:
        """Kiểm tra xem vị trí có va vào tường hay không."""
        half = self.size / 2
        corners = [
            (x - half, y - half),
            (x + half, y - half),
            (x - half, y + half),
            (x + half, y + half)
        ]

        for cx, cy in corners:
            gx = int(cx // TILE_SIZE)
            gy = int(cy // TILE_SIZE)

            if gy < 0 or gy >= len(maze) or gx < 0 or gx >= len(maze[0]):
                return True
            if maze[gy][gx] == CELL_WALL:
                return True
        return False

    # ==================== HEALTH ====================
    def take_damage(self, damage: int):
        """Gây sát thương cho nhân vật."""
        if self.damage_cooldown <= 0:
            self.health -= damage
            self.damage_cooldown = self.invulnerable_time
            self.health = max(self.health, 0)

    def heal(self, amount: int):
        """Hồi máu."""
        self.health = min(self.health + amount, self.max_health)

    def is_alive(self) -> bool:
        """Kiểm tra nhân vật còn sống không."""
        return self.health > 0

    def reset_position(self, x: int, y: int):
        """Đặt lại vị trí nhân vật khi bắt đầu hoặc chết."""
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.velocity_x = 0
        self.velocity_y = 0

    # ==================== RENDER ====================
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Hiển thị nhân vật (màu hoặc ảnh)."""
        # Nhấp nháy khi miễn thương
        if self.damage_cooldown > 0 and int(self.damage_cooldown * 10) % 2 == 0:
            return

        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Nếu có ảnh thì vẽ ảnh, không thì vẽ hình tròn màu
        if self.image:
            rect = self.image.get_rect(center=(screen_x, screen_y))
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size // 2)

        # Hiển thị hướng di chuyển
        if self.velocity_x != 0 or self.velocity_y != 0:
            indicator_x = screen_x + int(self.velocity_x * self.size // 2)
            indicator_y = screen_y + int(self.velocity_y * self.size // 2)
            pygame.draw.circle(screen, (255, 255, 255), (indicator_x, indicator_y), 3)
