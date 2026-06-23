#GUI menu selction logic
from main_menu import main_menu
from options_menu import options_menu
from game_view import game_view


class level_manager:
    def __init__(self, display):
        self.level_classes = {
            "main_menu": main_menu,
            "options_menu": options_menu,
            "game": game_view,
        }
        self.display = display
        self.current_level_name = "main_menu"
        self.current_level = self.create_level("main_menu")

    def create_level(self, level_name, **kwargs):
        return self.level_classes[level_name](self.display, **kwargs)

    def run(self, event_list, delta_time, display):
        self.current_level.run(event_list, delta_time, display)
        if getattr(self.current_level, "finish", False):
            next_level_name = getattr(self.current_level, "new_level", None)
            extra_kwargs = {}
            if self.current_level_name == "options_menu" and next_level_name == "main_menu":
                extra_kwargs = {"return_to_index": getattr(self.current_level, "return_to_index", 1)}
            elif self.current_level_name == "game" and next_level_name == "main_menu":
                extra_kwargs = {"return_to_index": 0}
            self.current_level = self.create_level(next_level_name, **extra_kwargs)
            self.current_level_name = next_level_name
