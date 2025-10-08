import pygame
from src.untils.constants import *
class InputBox:
    """Textbox để nhập username / password."""

    def __init__(self, x, y, w, h, font, password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = ''
        self.font = font
        self.active = False
        self.password = password
        self.txt_surface = self.font.render('', True, WHITE)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click vào trong ô thì active
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20:
                    self.text += event.unicode
            self._update_text()
        return False

    def _update_text(self):
        display_text = '*' * len(self.text) if self.password else self.text
        self.txt_surface = self.font.render(display_text, True, WHITE)

    def clear(self):
        self.text = ""
        self._update_text()
        self.active = False
        self.color = self.color_inactive

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
