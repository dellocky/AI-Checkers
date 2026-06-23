#Main loop, initalizes the menu manager and handles the indow itself

import sys
from time import time

import pygame

from level_manager import level_manager
from settings import settings


class game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.previous_time = time()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.WINDOW_NAME)
        self.display = self.screen
        self.level_manager = level_manager(self.display)

    def run(self):
        while True:
            current_time = time()
            delta_time = current_time - self.previous_time
            self.previous_time = current_time

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.display.fill(settings.BACKGROUND)
            self.level_manager.run(event_list, delta_time, self.display)
            pygame.display.update()
            self.clock.tick(settings.FPS)


if __name__ == "__main__":
    Game = game()
    Game.run()
