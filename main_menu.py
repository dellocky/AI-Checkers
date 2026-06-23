#GUI menus, messy implementation but works
import pygame
from sys import exit


class main_menu:
    def __init__(self, display, return_to_index=None):
        self.finish = False
        self.display = display
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 64)
        self.selected_rgb = (0, 255, 0)
        self.non_selected_rgb = (255, 255, 255)
        self.menu_items = ["Play", "Options", "Exit"]

    def run(self, event_list, delta_time, display):
        display.fill((0, 0, 0))
        title = self.title_font.render("Checkers", True, (255, 255, 255))
        display.blit(title, (display.get_width() // 2 - title.get_width() // 2, 80))

        mouse_pos = pygame.mouse.get_pos()

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, item in enumerate(self.menu_items):
                    text_surface = self.font.render(item, True, self.non_selected_rgb)
                    x = display.get_width() // 2 - text_surface.get_width() // 2
                    y = 220 + index * 70
                    rect = pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
                    if rect.collidepoint(event.pos):
                        if item == "Play":
                            self.finish = True
                            self.new_level = "game"
                        elif item == "Options":
                            self.finish = True
                            self.new_level = "options_menu"
                        elif item == "Exit":
                            pygame.quit()
                            exit()

        for index, item in enumerate(self.menu_items):
            text_surface_measure = self.font.render(item, True, self.non_selected_rgb)
            x = display.get_width() // 2 - text_surface_measure.get_width() // 2
            y = 220 + index * 70
            rect = pygame.Rect(x, y, text_surface_measure.get_width(), text_surface_measure.get_height())
            
            color = self.selected_rgb if rect.collidepoint(mouse_pos) else self.non_selected_rgb
            text_surface = self.font.render(item, True, color)
            display.blit(text_surface, (x, y))