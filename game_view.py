import pygame
from board import CheckersGame, Move, NUMBER_TO_COLOR_CONVERT, is_dark_square
from ai import CheckersAI
from config import load_config
from settings import settings

# This is the main view of the game shows covers pretty much all of the game logic aside for the AI calculations
class game_view:
    def __init__(self, display, return_to_index=None):
        self.finish = False
        self.display = display
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)

        self.game = CheckersGame()
        self.ai = CheckersAI(load_config()["difficulty"])
        self.ai_pending = False
        self.status_message = "Drag a white piece to move."

        self.selected_pos = None
        self.legal_moves = []
        self.highlight_squares = set()
        self.dragging = False
        self.drag_pos = None
        self.drag_piece = None
        self.drag_origin = None

    #find the pixel lovation for each the tile locations
    def board_to_pixel(self, board_pos):
        x = settings.BOARD_OFFSET_X + board_pos[0] * settings.TILE_SIZE
        y = settings.BOARD_OFFSET_Y + board_pos[1] * settings.TILE_SIZE
        return x, y

    #inverese
    def pixel_to_board(self, pixel_pos):
        x = (pixel_pos[0] - settings.BOARD_OFFSET_X) // settings.TILE_SIZE
        y = (pixel_pos[1] - settings.BOARD_OFFSET_Y) // settings.TILE_SIZE
        if 0 <= x < settings.BOARD_SIZE and 0 <= y < settings.BOARD_SIZE:
            return (x, y)
        return None

    #centers the piece
    def piece_center(self, board_pos):
        x, y = self.board_to_pixel(board_pos)
        return x + settings.TILE_SIZE // 2, y + settings.TILE_SIZE // 2

    #deselects the currently selected piece
    def clear_selection(self):
        self.selected_pos = None
        self.legal_moves = []
        self.highlight_squares = set()
        self.dragging = False
        self.drag_pos = None
        self.drag_piece = None
        self.drag_origin = None

    #shows the playable moves of the player on the current turn
    def refresh_legal_moves(self, start_pos):
        self.selected_pos = start_pos
        self.legal_moves = self.game.get_legal_moves(start_pos)
        self.highlight_squares = {move.end for move in self.legal_moves}

    #allows continous jumps, more so for the the teriminal version of the game
    def select_continue_piece(self):
        if self.game.must_continue_from is not None:
            self.refresh_legal_moves(self.game.must_continue_from)
            self.status_message = "Continue your jump."

    #follows through with the move the player selects and checks for winners
    def apply_human_move(self, move):
        if not self.game.apply_move(move):
            return False

        if self.game.winner is not None:
            winner = NUMBER_TO_COLOR_CONVERT[self.game.winner].title()
            self.status_message = f"{winner} wins! Press Esc for menu."
            self.clear_selection()
            return True

        if self.game.must_continue_from is not None:
            self.select_continue_piece()
            return True

        self.clear_selection()
        self.status_message = "AI is thinking..."
        self.ai_pending = True
        return True

    #runs the ai calulations of the current board state to look for and play the best move that the model can find
    def run_ai_turn(self):
        self.ai.set_difficulty(load_config()["difficulty"])
        move = self.ai.get_best_move(self.game)
        if move:
            self.game.apply_move(move)

        if self.game.winner is not None:
            winner = NUMBER_TO_COLOR_CONVERT[self.game.winner].title()
            self.status_message = f"{winner} wins! Press Esc for menu."
        elif self.game.turn == CheckersGame.HUMAN_PLAYER:
            self.status_message = "Your turn. Drag a white piece."
        else:
            self.status_message = "AI is thinking..."
            self.ai_pending = True

    #translates the mouse move to check if its a legal move
    def move_for_drop(self, start_pos, end_pos):
        for move in self.legal_moves:
            if move.start == start_pos and move.end == end_pos:
                return move
        return None

    #drag logic, for clicking and dragging the pieces
    def handle_mouse_down(self, event):
        if self.game.winner is not None:
            return
        if self.game.turn != CheckersGame.HUMAN_PLAYER:
            return

        board_pos = self.pixel_to_board(event.pos)
        if board_pos is None:
            return

        if self.game.must_continue_from is not None:
            if board_pos != self.game.must_continue_from:
                return
            piece = self.game.board[board_pos]
            if piece:
                self.dragging = True
                self.drag_origin = board_pos
                self.drag_piece = piece
                self.drag_pos = event.pos
                self.refresh_legal_moves(board_pos)
            return

        piece = self.game.board[board_pos]
        if not piece or piece.get_player() != CheckersGame.HUMAN_PLAYER:
            self.clear_selection()
            return

        self.dragging = True
        self.drag_origin = board_pos
        self.drag_piece = piece
        self.drag_pos = event.pos
        self.refresh_legal_moves(board_pos)

    #release the drag
    def handle_mouse_up(self, event):
        if not self.dragging or self.drag_origin is None:
            return

        board_pos = self.pixel_to_board(event.pos)
        move = None
        if board_pos is not None:
            move = self.move_for_drop(self.drag_origin, board_pos)

        self.dragging = False
        self.drag_pos = None

        if move:
            self.apply_human_move(move)
        elif self.game.must_continue_from is None:
            self.clear_selection()
            if self.selected_pos == self.drag_origin:
                self.refresh_legal_moves(self.drag_origin)
        else:
            self.select_continue_piece()

        self.drag_piece = None
        self.drag_origin = None

    #seach for inputs
    def handle_events(self, event_list):
        for event in event_list:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.finish = True
                self.new_level = "main_menu"
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.handle_mouse_up(event)
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.drag_pos = event.pos

    #renders the GUI view of the board object
    def draw_board(self, display):
        for row in range(settings.BOARD_SIZE):
            for col in range(settings.BOARD_SIZE):
                pos = (col, row)
                x, y = self.board_to_pixel(pos)
                color = settings.DARK_SQUARE if is_dark_square(pos) else settings.LIGHT_SQUARE
                rect = pygame.Rect(x, y, settings.TILE_SIZE, settings.TILE_SIZE)
                pygame.draw.rect(display, color, rect)

                if pos in self.highlight_squares:
                    highlight = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
                    highlight.fill(settings.HIGHLIGHT)
                    display.blit(highlight, (x, y))

                if pos == self.selected_pos and not self.dragging:
                    selected = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
                    selected.fill(settings.SELECTED)
                    display.blit(selected, (x, y))

    #renders piece to the board
    def draw_piece(self, display, piece, board_pos, alpha=255):
        center = self._piece_cener(board_pos)
        radius = settings.TILE_SIZE // 2 - 8
        fill = settings.WHITE_PIECE if piece.get_player() == CheckersGame.HUMAN_PLAYER else settings.BLACK_PIECE

        if alpha < 255:
            piece_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(piece_surface, (*fill, alpha), (radius, radius), radius)
            pygame.draw.circle(piece_surface, (*settings.PIECE_OUTLINE, alpha), (radius, radius), radius, 2)
            display.blit(piece_surface, (center[0] - radius, center[1] - radius))
        else:
            pygame.draw.circle(display, fill, center, radius)
            pygame.draw.circle(display, settings.PIECE_OUTLINE, center, radius, 2)

        if piece.is_king():
            crown_rect = pygame.Rect(center[0] - 8, center[1] - 8, 16, 16)
            pygame.draw.rect(display, settings.KING_MARK, crown_rect, 2) #draw kings with there special mark

    #renders all pieces on the board to there proper centered space
    def draw_pieces(self, display):
        for row in range(settings.BOARD_SIZE):
            for col in range(settings.BOARD_SIZE):
                pos = (col, row)
                piece = self.game.board[pos]
                if not piece:
                    continue
                if self.dragging and pos == self.drag_origin:
                    continue
                self.draw_piece(display, piece, pos)

        if self.dragging and self.drag_piece and self.drag_pos:
            radius = settings.TILE_SIZE // 2 - 8
            pygame.draw.circle(display, settings.WHITE_PIECE, self.drag_pos, radius)
            pygame.draw.circle(display, settings.PIECE_OUTLINE, self.drag_pos, radius, 2)
            if self.drag_piece.is_king():
                crown_rect = pygame.Rect(self.drag_pos[0] - 8, self.drag_pos[1] - 8, 16, 16)
                pygame.draw.rect(display, settings.KING_MARK, crown_rect, 2)

    #main loop
    def run(self, event_list, delta_time, display):
        if self.ai_pending and self.game.turn == CheckersGame.AI_PLAYER and self.game.winner is None:
            self.ai_pending = False
            self.run_ai_turn()

        if self.game.must_continue_from is not None and not self.legal_moves and self.game.winner is None:
            self.select_continue_piece()

        self.handle_events(event_list)

        display.fill(settings.BACKGROUND)
        title = self.font.render("Checkers vs AI", True, settings.TEXT_COLOR)
        display.blit(title, (20, 20))

        difficulty = load_config()["difficulty"].title()
        info = self.small_font.render(f"Difficulty: {difficulty}  |  Esc: Main Menu", True, settings.TEXT_COLOR)
        display.blit(info, (20, 55))

        status = self.small_font.render(self.status_message, True, settings.TEXT_COLOR)
        display.blit(status, (20, 85))

        self.draw_board(display)
        self.draw_pieces(display)
