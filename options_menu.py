#GUI menus, messy implementation but works
import pygame
from difficulty_menu import difficulty_menu


class options_menu:
    def __init__(self, display):
        self.finish = False
        self.display = display
        self.font = pygame.font.Font(None, 36)
        self.selected_rgb = (0, 255, 0)
        self.non_selected_rgb = (255, 255, 255)
        self.menu_items = ["Difficulty", "Back"]
        self.sub_menus = {
            "Difficulty": difficulty_menu,
            "Back": None,
        }
        self.border_width = 5
        self.sub_menu_surface = pygame.Surface(
            (
                int(display.get_width() / 2) - self.border_width,
                display.get_height() - (self.border_width * 2),
            )
        )
        self.current_sub_menu = self.sub_menus["Difficulty"](self.sub_menu_surface)

    def run(self, event_list, delta_time, display):
        display.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, item in enumerate(self.menu_items):
                    text_surface = self.font.render(item, True, self.non_selected_rgb)
                    x = display.get_width() // 4 - text_surface.get_width() // 2
                    y = 40 + index * 40
                    rect = pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
                    if rect.collidepoint(event.pos):
                        if item == "Back":
                            self.finish = True
                            self.new_level = "main_menu"
                            self.return_to_index = 1

        for index, item in enumerate(self.menu_items):
            text_surface_measure = self.font.render(item, True, self.non_selected_rgb)
            x = display.get_width() // 4 - text_surface_measure.get_width() // 2
            y = 40 + index * 40
            rect = pygame.Rect(x, y, text_surface_measure.get_width(), text_surface_measure.get_height())
            
            color = self.selected_rgb if rect.collidepoint(mouse_pos) else self.non_selected_rgb
            text_surface = self.font.render(item, True, color)
            display.blit(text_surface, (x, y))

        if self.current_sub_menu is not None:
            # Offset positions so events and hover logic match the shifted coordinates on the sub-surface area
            offset_x = display.get_width() // 2
            offset_y = self.border_width
            
            adjusted_events = []
            for event in event_list:
                if hasattr(event, "pos"):
                    new_pos = (event.pos[0] - offset_x, event.pos[1] - offset_y)
                    adjusted_events.append(pygame.event.Event(event.type, {**event.dict, "pos": new_pos}))
                else:
                    adjusted_events.append(event)

            # Safely intercept get_pos so the submenu's independent hover detection lines up perfectly
            orig_get_pos = pygame.mouse.get_pos
            pygame.mouse.get_pos = lambda: (orig_get_pos()[0] - offset_x, orig_get_pos()[1] - offset_y)
            
            self.current_sub_menu.run(adjusted_events, delta_time, self.sub_menu_surface)
            
            pygame.mouse.get_pos = orig_get_pos
            
            display.blit(self.sub_menu_surface, (offset_x, offset_y))