import os

import pygame
import sys
from src.game import Game
from src.untils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE


def main():
    """
    Main entry point for the Maze Game application.
    Initializes pygame and starts the game loop.
    """
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()

    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # Set window icon
    icon_path = os.path.join("assets", "image", "maze-game.ico")
    if os.path.exists(icon_path):
        pygame.display.set_icon(pygame.image.load(icon_path))

    # Create clock for FPS control
    clock = pygame.time.Clock()

    # Initialize the game
    game = Game(screen)

    # Main game loop
    running = True
    while running:
        # Handle events (Input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        # Update game state (Update)
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        game.update(dt)

        # Render to screen (Render)
        game.render()

        # Update display
        pygame.display.flip()

        # Check game conditions (Check)
        if game.should_quit:
            running = False

    # Cleanup
    game.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()