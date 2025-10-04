
import pygame
from typing import Tuple, Optional
from src.untils.constants import *


class Button:
    """Simple button class."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: Tuple[int, int, int] = BLUE):
        """
        Initialize button.

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            color: Button color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 40, 255) for c in color)
        self.is_hovered = False

    def update(self, mouse_pos: Tuple[int, int]):
        """Update button state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw button."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)


class UIManager:
    """Manages UI elements and rendering."""

    def __init__(self, screen: pygame.Surface):
        """
        Initialize UI Manager.

        Args:
            screen: Main pygame display surface
        """
        self.screen = screen
        self.font = pygame.font.Font(None, UI_FONT_SIZE)
        self.small_font = pygame.font.Font(None, UI_SMALL_FONT_SIZE)
        self.large_font = pygame.font.Font(None, UI_LARGE_FONT_SIZE)

    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int] = WHITE,
                  font: Optional[pygame.font.Font] = None, center: bool = False):
        """
        Draw text to screen.

        Args:
            text: Text to draw
            x: X position
            y: Y position
            color: Text color
            font: Font to use (default: self.font)
            center: Whether to center text at position
        """
        if font is None:
            font = self.font

        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))

    def draw_health_bar(self, x: int, y: int, width: int, height: int,
                        current: float, maximum: float):
        """
        Draw a health bar.

        Args:
            x: X position
            y: Y position
            width: Bar width
            height: Bar height
            current: Current health value
            maximum: Maximum health value
        """
        # Background (red)
        pygame.draw.rect(self.screen, RED, (x, y, width, height))

        # Foreground (green)
        health_width = int(width * (current / maximum))
        pygame.draw.rect(self.screen, GREEN, (x, y, health_width, height))

        # Border
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), 2)

    def draw_panel(self, x: int, y: int, width: int, height: int,
                   color: Tuple[int, int, int] = DARK_GRAY,
                   border_color: Tuple[int, int, int] = WHITE):
        """
        Draw a UI panel.

        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            color: Panel background color
            border_color: Border color
        """
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 2)

    def draw_grid(self, x: int, y: int, cols: int, rows: int,
                  cell_size: int, color: Tuple[int, int, int] = GRAY):
        """
        Draw a grid.

        Args:
            x: Starting X position
            y: Starting Y position
            cols: Number of columns
            rows: Number of rows
            cell_size: Size of each cell
            color: Grid line color
        """
        # Vertical lines
        for i in range(cols + 1):
            pygame.draw.line(self.screen, color,
                             (x + i * cell_size, y),
                             (x + i * cell_size, y + rows * cell_size))

        # Horizontal lines
        for i in range(rows + 1):
            pygame.draw.line(self.screen, color,
                             (x, y + i * cell_size),
                             (x + cols * cell_size, y + i * cell_size))

    def create_button(self, x: int, y: int, width: int, height: int,
                      text: str, color: Tuple[int, int, int] = BLUE) -> Button:
        """
        Create a button.

        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            color: Button color

        Returns:
            Button instance
        """
        return Button(x, y, width, height, text, color)