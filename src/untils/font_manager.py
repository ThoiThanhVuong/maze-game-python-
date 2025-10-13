import pygame
import os
import sys

pygame.font.init()

DEFAULT_FONT_SIZE = 24

def resource_path(relative_path):
    """Trả về đường dẫn chính xác khi chạy bằng file .exe hoặc khi chạy bình thường"""
    try:
        base_path = sys._MEIPASS  # Khi chạy trong file exe (PyInstaller)
    except Exception:
        base_path = os.path.abspath(".")  # Khi chạy trong IDE hoặc terminal
    return os.path.join(base_path, relative_path)

def get_font(size=DEFAULT_FONT_SIZE):
    """Trả về đối tượng font pygame hỗ trợ tiếng Việt."""
    font_path = resource_path(os.path.join("assets", "fonts", "BeVietnamPro-Regular.ttf"))
    return pygame.font.Font(font_path, size)
