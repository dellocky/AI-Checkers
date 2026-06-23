#Class of globals to unify data, currently enables runtime changing of the difficulty but could be modified
#to provide functionality for setttings that also change the screen size or offset params


class Settings:
    FPS = 60
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 720
    WINDOW_NAME = "Checkers"

    BOARD_SIZE = 8
    TILE_SIZE = 70
    BOARD_OFFSET_X = (SCREEN_WIDTH - BOARD_SIZE * TILE_SIZE) // 2
    BOARD_OFFSET_Y = 120

    LIGHT_SQUARE = (222, 184, 135)
    DARK_SQUARE = (139, 90, 43)
    HIGHLIGHT = (100, 200, 100, 120)
    SELECTED = (255, 255, 0, 120)
    TEXT_COLOR = (255, 255, 255)
    MENU_SELECTED = (0, 255, 0)
    MENU_NORMAL = (255, 255, 255)
    BACKGROUND = (30, 30, 40)

    WHITE_PIECE = (240, 240, 240)
    BLACK_PIECE = (30, 30, 30)
    PIECE_OUTLINE = (20, 20, 20)
    KING_MARK = (255, 215, 0)

    DIFFICULTY_DEPTHS = {
        "easy": 2,
        "medium": 4,
        "hard": 6,
    }


settings = Settings()
