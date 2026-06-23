#GUI menus, messy implementation but works

import pygame
from config import load_config, save_config, VALID_DIFFICULTIES


class difficulty_menu:
    def __init__(self, display):
        self.finish = False
        self.display = display
        self.font = pygame.font.Font(None, 24)
        self.selected_rgb = (0, 255, 0)
        self.non_selected_rgb = (255, 255, 255)
        self.menu_items = ["Difficulty"]
        self.dropdown_open = None
        self.difficulty_options = list(VALID_DIFFICULTIES)
        self.current_difficulty = load_config()["difficulty"]

    def run(self, event_list, delta_time, display):
        display.fill((0, 0, 20))
        menu_x = display.get_width() // 3
        menu_y = 40
        mouse_pos = pygame.mouse.get_pos()

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dropdown_open is None:
                    for index, item in enumerate(self.menu_items):
                        text_surface = self.font.render(f"{item}: {self.current_difficulty.title()}", True, self.non_selected_rgb)
                        x = menu_x - text_surface.get_width() // 2
                        y = menu_y + index * 40
                        rect = pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
                        if rect.collidepoint(event.pos):
                            self.dropdown_open = "difficulty"
                elif self.dropdown_open == "difficulty":
                    dropdown_x = menu_x
                    dropdown_y = menu_y + 28
                    for index, option in enumerate(self.difficulty_options):
                        text_surface = self.font.render(option.title(), True, self.non_selected_rgb)
                        x = dropdown_x - text_surface.get_width() // 2
                        y = dropdown_y + index * 24
                        rect = pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
                        if rect.collidepoint(event.pos):
                            self.current_difficulty = option
                            config = load_config()
                            config["difficulty"] = self.current_difficulty
                            save_config(config)
                            self.dropdown_open = None

        for index, item in enumerate(self.menu_items):
            text_surface_measure = self.font.render(f"{item}: {self.current_difficulty.title()}", True, self.non_selected_rgb)
            x = menu_x - text_surface_measure.get_width() // 2
            y = menu_y + index * 40
            rect = pygame.Rect(x, y, text_surface_measure.get_width(), text_surface_measure.get_height())
            
            color = self.selected_rgb if (self.dropdown_open is None and rect.collidepoint(mouse_pos)) else self.non_selected_rgb
            text_surface = self.font.render(f"{item}: {self.current_difficulty.title()}", True, color)
            display.blit(text_surface, (x, y))


        if self.dropdown_open == "difficulty":
            dropdown_x = menu_x
            dropdown_y = menu_y + 28
            for index, option in enumerate(self.difficulty_options):
                text_surface_measure = self.font.render(option.title(), True, self.non_selected_rgb)
                x = dropdown_x - text_surface_measure.get_width() // 2
                y = dropdown_y + index * 24
                rect = pygame.Rect(x, y, text_surface_measure.get_width(), text_surface_measure.get_height())
                
                color = self.selected_rgb if rect.collidepoint(mouse_pos) else self.non_selected_rgb
                text_surface = self.font.render(option.title(), True, color)
                display.blit(text_surface, (x, y))