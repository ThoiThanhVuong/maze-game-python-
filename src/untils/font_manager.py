import pygame
import os

# Khởi tạo font global
pygame.font.init()

# Đường dẫn tới font (tùy bạn lưu ở đâu)
FONT_PATH = os.path.join("assets", "fonts", "BeVietnamPro-Regular.ttf")

# Kích thước mặc định
DEFAULT_FONT_SIZE = 24

# Hàm lấy font
def get_font(size=DEFAULT_FONT_SIZE):
    """Trả về đối tượng font pygame hỗ trợ tiếng Việt."""
    return pygame.font.Font(FONT_PATH, size)
