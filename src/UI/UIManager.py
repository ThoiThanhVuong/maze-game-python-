import pygame
from typing import Tuple, Optional
from src.untils.constants import *
class UIManager:
    """Manages UI elements and rendering."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, UI_FONT_SIZE)
        self.small_font = pygame.font.Font(None, UI_SMALL_FONT_SIZE)
        self.large_font = pygame.font.Font(None, UI_LARGE_FONT_SIZE)

    def draw_text(self, text: str, x: int, y: int,
                  color: Tuple[int, int, int] = WHITE,
                  font: Optional[pygame.font.Font] = None,
                  center: bool = False):
        if font is None:
            font = self.font
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))
