
import pygame
from typing import Tuple
from src.untils.constants import (
    PLAYER_SPEED, PLAYER_MAX_HEALTH, PLAYER_SIZE,
    TILE_SIZE, CELL_WALL, SKINS
)


class Player:
    """Represents the player character."""

    def __init__(self, x: int, y: int, skin_id: int = 1):
        """
        Initialize player.

        Args:
            x: Starting x position (grid coordinates)
            y: Starting y position (grid coordinates)
            skin_id: Selected skin ID
        """
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED

        # Health system
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH

        # Skin
        self.skin_id = skin_id
        self.color = self._get_skin_color()

        # Movement
        self.velocity_x = 0
        self.velocity_y = 0

        # Collision cooldown (to prevent multiple hits)
        self.damage_cooldown = 0
        self.invulnerable_time = 0.5  # 0.5 seconds of invulnerability after hit

    def _get_skin_color(self) -> Tuple[int, int, int]:
        """Get color for current skin."""
        for skin in SKINS:
            if skin['id'] == self.skin_id:
                return skin['color']
        return SKINS[0]['color']  # Default

    def set_skin(self, skin_id: int):
        """Change player skin."""
        self.skin_id = skin_id
        self.color = self._get_skin_color()

    def handle_input(self, keys: pygame.key.ScancodeWrapper):
        """
        Handle keyboard input for player movement.

        Args:
            keys: Pygame key state
        """
        self.velocity_x = 0
        self.velocity_y = 0

        # Arrow keys or WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = 1

        # Normalize diagonal movement
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x *= 0.707  # sqrt(2)/2
            self.velocity_y *= 0.707

    def update(self, dt: float, maze: list):
        """
        Update player state.

        Args:
            dt: Delta time in seconds
            maze: Current maze grid
        """
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        # Calculate new position
        new_x = self.x + self.velocity_x * self.speed * dt
        new_y = self.y + self.velocity_y * self.speed * dt

        # Check collision with walls
        if not self._check_collision(new_x, self.y, maze):
            self.x = new_x
        if not self._check_collision(self.x, new_y, maze):
            self.y = new_y

        # Update grid position
        self.grid_x = int(self.x / TILE_SIZE)
        self.grid_y = int(self.y / TILE_SIZE)

    def _check_collision(self, x: float, y: float, maze: list) -> bool:
        """
        Check if position collides with walls.

        Args:
            x: X position to check
            y: Y position to check
            maze: Current maze grid

        Returns:
            True if collision detected, False otherwise
        """
        # Check all four corners of player hitbox
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

            # Check bounds
            if grid_y < 0 or grid_y >= len(maze) or grid_x < 0 or grid_x >= len(maze[0]):
                return True

            # Check if wall
            if maze[grid_y][grid_x] == CELL_WALL:
                return True

        return False

    def take_damage(self, damage: int):
        """
        Apply damage to player.

        Args:
            damage: Amount of damage to apply
        """
        if self.damage_cooldown <= 0:
            self.health -= damage
            self.damage_cooldown = self.invulnerable_time
            if self.health < 0:
                self.health = 0

    def heal(self, amount: int):
        """Heal player by amount."""
        self.health = min(self.health + amount, self.max_health)

    def is_alive(self) -> bool:
        """Check if player is alive."""
        return self.health > 0

    def reset_position(self, x: int, y: int):
        """Reset player to starting position."""
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.velocity_x = 0
        self.velocity_y = 0

    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Render player to screen.

        Args:
            screen: Pygame surface to render to
            camera_offset: Camera offset (x, y)
        """
        # Flash when invulnerable
        if self.damage_cooldown > 0 and int(self.damage_cooldown * 10) % 2 == 0:
            return

        # Draw player as circle
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size // 2)

        # Draw direction indicator (small dot)
        if self.velocity_x != 0 or self.velocity_y != 0:
            indicator_x = screen_x + int(self.velocity_x * self.size // 2)
            indicator_y = screen_y + int(self.velocity_y * self.size // 2)
            pygame.draw.circle(screen, (255, 255, 255), (indicator_x, indicator_y), 3)