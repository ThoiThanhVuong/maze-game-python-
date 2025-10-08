import pygame
import os

class SoundManager:
    def __init__(self, base_path="assets/sounds"):
        pygame.mixer.init()
        self.sounds = {
            "move": pygame.mixer.Sound(os.path.join(base_path, "Blip_sound.wav")),
            "select": pygame.mixer.Sound(os.path.join(base_path, "select-sound-user-interface.wav")),
            "explosion": pygame.mixer.Sound(os.path.join(base_path, "repetitive-explosion.wav")),
            "win": pygame.mixer.Sound(os.path.join(base_path, "win-sound.wav")),
            "game_over": pygame.mixer.Sound(os.path.join(base_path, "game_over_sound.wav")),
        }

        # Giảm âm lượng để nghe dễ chịu
        for sound in self.sounds.values():
            sound.set_volume(0.3)

    def play(self, name):
        """Phát âm thanh theo tên"""
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"[SoundManager] Warning: sound '{name}' not found!")
