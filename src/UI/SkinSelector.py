import pygame
import tkinter as tk
from tkinter import colorchooser, filedialog
from src.untils.font_manager import get_font
from src.untils.constants import SKINS


class SkinSelectorUI:
    """Màn hình chọn skin: chọn số, màu, hoặc hình ảnh."""

    def __init__(self, screen, on_select_callback=None):
        self.screen = screen
        self.on_select_callback = on_select_callback
        self.running = True
        self.result = None
        self.selected_index = 0  # chỉ số skin hiện tại (0–5)

        # Font toàn cục
        self.font_small = get_font(22)
        self.font_medium = get_font(28)
        self.font_large = get_font(36)

    def run(self):
        """Hiển thị giao diện chọn skin và trả về kết quả."""
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_6:
                        # Nhấn phím 1–6 để di chuyển con trỏ “>>”
                        self.selected_index = event.key - pygame.K_1
                    elif event.key == pygame.K_RETURN:
                        # Xác nhận lựa chọn
                        selected_skin = SKINS[self.selected_index]
                        self.result = {
                            "skin_type": "preset",
                            "skin_value": str(selected_skin["id"]),
                        }
                        self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse(event.pos)

            self._render()
            pygame.display.flip()
            clock.tick(30)

        if self.result and self.on_select_callback:
            self.on_select_callback(**self.result)
        return self.result

    def _handle_mouse(self, pos):
        """Xử lý click vào nút màu hoặc ảnh."""
        # Nút chọn màu
        if self.color_btn.collidepoint(pos):
            root = tk.Tk()
            root.withdraw()
            color_result = colorchooser.askcolor(title="Chọn màu cho nhân vật")
            root.destroy()

            if color_result and color_result[0]:
                rgb = tuple(int(c) for c in color_result[0]) # type: ignore
                self.result = {"skin_type": "color", "skin_value": str(rgb)}
                self.running = False

        # Nút chọn ảnh
        elif self.image_btn.collidepoint(pos):
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(
                title="Chọn ảnh nhân vật",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")],
            )
            root.destroy()
            if path:
                self.result = {"skin_type": "image", "skin_value": path}
                self.running = False

    def _render(self):
        """Vẽ giao diện chọn skin."""
        self.screen.fill((0, 0, 0))

        # Tiêu đề
        title = self.font_large.render("CHỌN SKIN", True, (255, 255, 0))
        self.screen.blit(title, (640 - title.get_width() // 2, 80))

        # Danh sách skin
        start_y = 200
        for i, skin in enumerate(SKINS):
            name = skin["name"]
            color = skin["color"]

            # Nếu là skin đang chọn → thêm ký hiệu >>
            prefix = ">> " if i == self.selected_index else "   "
            text_surface = self.font_medium.render(f"{prefix}{i + 1}. {name}", True, color)

            text_x = 580 - text_surface.get_width() // 2
            text_y = start_y + i * 50
            self.screen.blit(text_surface, (text_x, text_y))

            # Ô màu preview bên phải
            color_rect = pygame.Rect(text_x + text_surface.get_width() + 20, text_y + 5, 30, 30)
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), color_rect, 2)

        # Nút chọn Màu / Ảnh
        self.color_btn = pygame.Rect(480, 520, 120, 40)
        self.image_btn = pygame.Rect(680, 520, 160, 40)
        pygame.draw.rect(self.screen, (120, 180, 255), self.color_btn, border_radius=8)
        pygame.draw.rect(self.screen, (100, 255, 120), self.image_btn, border_radius=8)

        color_text = self.font_small.render("🎨 Màu", True, (0, 0, 0))
        image_text = self.font_small.render("📁 Ảnh", True, (0, 0, 0))
        self.screen.blit(
            color_text,
            (
                self.color_btn.centerx - color_text.get_width() // 2,
                self.color_btn.centery - color_text.get_height() // 2,
            ),
        )
        self.screen.blit(
            image_text,
            (
                self.image_btn.centerx - image_text.get_width() // 2,
                self.image_btn.centery - image_text.get_height() // 2,
            ),
        )

        # Hướng dẫn điều khiển
        hint_text = self.font_small.render(
            "Nhấn phím 1–6 để chọn | ENTER để xác nhận | ESC để quay lại",
            True,
            (180, 180, 180),
        )
        self.screen.blit(hint_text, (640 - hint_text.get_width() // 2, 600))
