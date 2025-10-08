import pygame
import random
import math
from typing import Tuple
from src.untils.constants import (
    ENEMY_SPEED, ENEMY_SIZE, ENEMY_DAMAGE, ENEMY_COOLDOWN,
    TILE_SIZE, CELL_WALL, RED, ORANGE
)

class Enemy:
    def __init__(self, x: int, y: int):
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.size = ENEMY_SIZE
        self.speed = ENEMY_SPEED
        self.damage = ENEMY_DAMAGE

        # Movement
        self.velocity_x = 0
        self.velocity_y = 0

        # AI behavior
        self.patrol_target = None
        self.direction_timer = 0
        self.direction_change_time = random.uniform(1.0, 3.0)

        # Attack cooldown
        self.attack_cooldown = 0

        # Visual
        self.color = RED
        self.pulse = 0  # Animation pulse

    # ==================== UPDATE ====================
    def update(self, dt: float, maze: list, player_pos: Tuple[float, float]):
        """Update enemy movement, AI, and cooldowns."""
        self.pulse += dt * 5

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Calculate distance to player
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance_to_player = math.hypot(dx, dy)

        # Chase player if within range
        chase_range = TILE_SIZE * 8
        if distance_to_player < chase_range:
            self._chase_player(player_pos)
        else:
            self._patrol(dt)

        # Update position with collision
        new_x = self.x + self.velocity_x * self.speed * dt
        new_y = self.y + self.velocity_y * self.speed * dt

        if not self._check_collision(new_x, self.y, maze):
            self.x = new_x
        else:
            self.velocity_x *= -1  # Bounce

        if not self._check_collision(self.x, new_y, maze):
            self.y = new_y
        else:
            self.velocity_y *= -1

        # Update grid position
        self.grid_x = int(self.x // TILE_SIZE)
        self.grid_y = int(self.y // TILE_SIZE)

    # ==================== AI ====================
    def _chase_player(self, player_pos: Tuple[float, float]):
        """Move towards the player."""
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.velocity_x = dx / distance
            self.velocity_y = dy / distance

    def _patrol(self, dt: float):
        """Wander randomly when player is far away."""
        self.direction_timer += dt

        if self.direction_timer >= self.direction_change_time:
            angle = random.uniform(0, 2 * math.pi)
            self.velocity_x = math.cos(angle)
            self.velocity_y = math.sin(angle)

            self.direction_timer = 0
            self.direction_change_time = random.uniform(1.0, 3.0)

    # ==================== COLLISION ====================
    def _check_collision(self, x: float, y: float, maze: list) -> bool:
        """Check for wall collisions."""
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

    # ==================== PLAYER INTERACTION ====================
    def check_collision_with_player(self, player) -> bool:
        """Return True if colliding with player."""
        distance = math.hypot(self.x - player.x, self.y - player.y)
        return distance < (self.size + player.size) / 2

    def can_attack(self) -> bool:
        """Check if the enemy can attack."""
        return self.attack_cooldown <= 0

    def attack(self, player):
        """Deal damage to the player."""
        if self.can_attack():
            player.take_damage(self.damage)
            self.attack_cooldown = ENEMY_COOLDOWN

    # ==================== RENDER ====================
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render enemy with pulsing animation."""
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Pulsing size
        pulse_size = int(math.sin(self.pulse) * 2 + self.size // 2)

        # Outer glow
        pygame.draw.circle(screen, ORANGE, (screen_x, screen_y), pulse_size + 2, 2)

        # Main body
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), pulse_size)

        # Eyes
        eye_offset = self.size // 4
        pygame.draw.circle(screen, (255, 255, 255),
                           (screen_x - eye_offset // 2, screen_y - eye_offset // 2), 3)
        pygame.draw.circle(screen, (255, 255, 255),
                           (screen_x + eye_offset // 2, screen_y - eye_offset // 2), 3)
