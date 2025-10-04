
import pygame
import random
import math
from typing import Tuple
from src.untils.constants import (
    ENEMY_SPEED, ENEMY_SIZE, ENEMY_DAMAGE, ENEMY_COOLDOWN,
    TILE_SIZE, CELL_WALL, RED, ORANGE
)


class Enemy:
    """Represents an enemy character with simple AI."""

    def __init__(self, x: int, y: int):
        """
        Initialize enemy.

        Args:
            x: Starting x position (grid coordinates)
            y: Starting y position (grid coordinates)
        """
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

        # AI state
        self.patrol_target = None
        self.direction_timer = 0
        self.direction_change_time = random.uniform(1.0, 3.0)

        # Damage cooldown
        self.attack_cooldown = 0

        # Visual
        self.color = RED
        self.pulse = 0  # For animation

    def update(self, dt: float, maze: list, player_pos: Tuple[float, float]):
        """
        Update enemy state and AI.

        Args:
            dt: Delta time in seconds
            maze: Current maze grid
            player_pos: Player position (x, y)
        """
        self.pulse += dt * 5

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Simple AI: Chase player if close, otherwise patrol
        distance_to_player = math.sqrt(
            (self.x - player_pos[0]) ** 2 + (self.y - player_pos[1]) ** 2
        )

        chase_range = TILE_SIZE * 8  # 8 tiles

        if distance_to_player < chase_range:
            # Chase player
            self._chase_player(player_pos)
        else:
            # Patrol randomly
            self._patrol(dt)

        # Update position
        new_x = self.x + self.velocity_x * self.speed * dt
        new_y = self.y + self.velocity_y * self.speed * dt

        # Check collision with walls
        if not self._check_collision(new_x, self.y, maze):
            self.x = new_x
        else:
            self.velocity_x *= -1  # Bounce off walls

        if not self._check_collision(self.x, new_y, maze):
            self.y = new_y
        else:
            self.velocity_y *= -1

        # Update grid position
        self.grid_x = int(self.x / TILE_SIZE)
        self.grid_y = int(self.y / TILE_SIZE)

    def _chase_player(self, player_pos: Tuple[float, float]):
        """
        Move towards player.

        Args:
            player_pos: Player position (x, y)
        """
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            self.velocity_x = dx / distance
            self.velocity_y = dy / distance

    def _patrol(self, dt: float):
        """
        Random patrol movement.

        Args:
            dt: Delta time
        """
        self.direction_timer += dt

        if self.direction_timer >= self.direction_change_time:
            # Change direction
            angle = random.uniform(0, 2 * math.pi)
            self.velocity_x = math.cos(angle)
            self.velocity_y = math.sin(angle)

            self.direction_timer = 0
            self.direction_change_time = random.uniform(1.0, 3.0)

    def _check_collision(self, x: float, y: float, maze: list) -> bool:
        """
        Check if position collides with walls.

        Args:
            x: X position to check
            y: Y position to check
            maze: Current maze grid

        Returns:
            True if collision detected
        """
        half_size = self.size / 2
        corners = [
            (x - half_size, y - half_size),
            (x + half_size, y - half_size),
            (x - half_size, y + half_size),
            (x + half_size, y + half_size)
        ]

        for cx, cy in corners:
            grid_x = int(cx / TILE_SIZE)
            grid_y = int(cy / TILE_SIZE)

            if grid_y < 0 or grid_y >= len(maze) or grid_x < 0 or grid_x >= len(maze[0]):
                return True

            if maze[grid_y][grid_x] == CELL_WALL:
                return True

        return False

    def check_collision_with_player(self, player) -> bool:
        """
        Check collision with player.

        Args:
            player: Player object

        Returns:
            True if colliding
        """
        distance = math.sqrt(
            (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        )
        return distance < (self.size + player.size) / 2

    def can_attack(self) -> bool:
        """Check if enemy can attack (cooldown expired)."""
        return self.attack_cooldown <= 0

    def attack(self, player):
        """
        Attack player.

        Args:
            player: Player object
        """
        if self.can_attack():
            player.take_damage(self.damage)
            self.attack_cooldown = ENEMY_COOLDOWN

    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Render enemy to screen.

        Args:
            screen: Pygame surface
            camera_offset: Camera offset (x, y)
        """
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Pulsing effect
        pulse_size = int(math.sin(self.pulse) * 2 + self.size // 2)

        # Draw outer glow
        pygame.draw.circle(screen, ORANGE, (screen_x, screen_y), pulse_size + 2, 2)

        # Draw enemy
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), pulse_size)

        # Draw eyes
        eye_offset = self.size // 4
        pygame.draw.circle(screen, (255, 255, 255),
                           (screen_x - eye_offset // 2, screen_y - eye_offset // 2), 3)
        pygame.draw.circle(screen, (255, 255, 255),
                           (screen_x + eye_offset // 2, screen_y - eye_offset // 2), 3)