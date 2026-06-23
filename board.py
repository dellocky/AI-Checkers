"""
Created by Kyle Dellock
6/16/2026

Checkers board logic and CLI debug interface.
Reuses the ChessBoard framework for grid storage, copying, and turn handling.
"""

from sys import exit

PLAYERS = 2
BOARD_SIZE = 8

COLOR_TO_NUMBER_CONVERT = {
    "white": 0,
    "black": 1,
}

NUMBER_TO_COLOR_CONVERT = {
    0: "white",
    1: "black",
}

KING_DIRECTIONS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
FORWARD_DIRECTIONS = {
    0: [(-1, -1), (1, -1)],
    1: [(-1, 1), (1, 1)],
}
PROMOTION_ROW = {0: 0, 1: BOARD_SIZE - 1}


def vector_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def is_dark_square(pos):
    return (pos[0] + pos[1]) % 2 == 1


def in_bounds(pos, columns):
    return 0 <= pos[0] < columns and 0 <= pos[1] < columns


class Move:
    def __init__(self, start, steps):
        self.start = start
        self.steps = steps

    @property
    def end(self):
        return self.steps[-1]

    def __repr__(self):
        return f"Move({self.start} -> {self.steps})"

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.start == other.start and self.steps == other.steps


class CheckerPiece:
    def __init__(self, player, pos, king=False):
        if isinstance(player, str):
            self.player = COLOR_TO_NUMBER_CONVERT[player]
        else:
            self.player = player
        self.pos = pos
        self.king = king
        self.name = "king" if king else "man"

    def __str__(self):
        prefix = NUMBER_TO_COLOR_CONVERT[self.player][0].upper()
        return f"{prefix}{'K' if self.king else 'M'}"

    def __repr__(self):
        return str(self)

    def get_player(self):
        return self.player

    def get_name(self):
        return self.name

    def get_pos(self):
        return self.pos

    def is_king(self):
        return self.king

    def get_directions(self):
        if self.king:
            return KING_DIRECTIONS
        return FORWARD_DIRECTIONS[self.player]


class ChessBoard:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.grid = [[0 for _ in range(columns)] for _ in range(rows)]
        self.piece_map = {0: set(), 1: set()}

    def copy(self):
        copy_board = ChessBoard(self.rows, self.columns)
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    new_piece = CheckerPiece(cell.get_player(), cell.get_pos(), cell.is_king())
                    copy_board[(x, y)] = new_piece
                    copy_board.piece_map[new_piece.get_player()].add(new_piece)
        return copy_board

    def __str__(self):
        horizontal_length = (self.columns + 1) * 3 - 2
        horizontal_line = "".join(["-" for _ in range(horizontal_length)]) + "\n"

        def make_row_line(row):
            return_string = "|"
            for cell in row:
                if cell:
                    return_string += str(cell)
                else:
                    return_string += "  "
                return_string += "|"
            return return_string + "\n"

        grid_representation = horizontal_line
        for row in self.grid:
            grid_representation += make_row_line(row)
            grid_representation += horizontal_line
        return grid_representation

    def __setitem__(self, pos, value):
        try:
            self.grid[pos[1]][pos[0]] = value
        except IndexError as exc:
            raise IndexError(f"Index {pos} out of range") from exc

    def __getitem__(self, pos):
        if not isinstance(pos, (tuple, list)):
            raise TypeError("Index must be list or tuple")
        try:
            return self.grid[pos[1]][pos[0]]
        except IndexError as exc:
            raise IndexError(f"Index {pos} out of range") from exc

    def create_piece(self, piece, pos, player, king=False):
        self[pos] = piece(player, pos, king)
        self.piece_map[player].add(self[pos])

    def get_grid(self):
        return self.grid

    def piece_count(self, player):
        return len(self.piece_map[player])

    #logic for jumping over pieces
    def single_jumps(self, piece):
        jumps = []
        for direction in piece.get_directions():
            middle = vector_add(piece.pos, direction)
            landing = vector_add(middle, direction)
            if not in_bounds(middle, self.columns) or not in_bounds(landing, self.columns):
                continue
            if not is_dark_square(landing):
                continue
            middle_piece = self[middle]
            landing_piece = self[landing]
            if middle_piece and middle_piece.get_player() != piece.get_player() and not landing_piece:
                jumps.append((middle, landing))
        return jumps

    #recursive function, finds the paths for muliple jumps in a row
    def capture_paths(self, piece, current_path, captured_positions):
        paths = []
        had_jump = False
        for middle, landing in self.single_jumps(piece):
            if middle in captured_positions:
                continue
            had_jump = True
            captured_piece = self[middle]
            original_pos = piece.pos
            original_king = piece.king

            self[original_pos] = 0
            self[middle] = 0
            self.piece_map[captured_piece.get_player()].remove(captured_piece)
            self[landing] = piece
            piece.pos = landing
            if not piece.king and landing[1] == PROMOTION_ROW[piece.get_player()]:
                piece.king = True
                piece.name = "king"

            next_path = current_path + [landing]
            further_paths = self.capture_paths(
                piece,
                next_path,
                captured_positions | {middle},
            )
            if further_paths:
                paths.extend(further_paths)
            else:
                paths.append(next_path)

            self[landing] = 0
            piece.pos = original_pos
            piece.king = original_king
            piece.name = "king" if original_king else "man"
            self[original_pos] = piece
            self[middle] = captured_piece
            self.piece_map[captured_piece.get_player()].add(captured_piece)

        if not had_jump and current_path:
            paths.append(current_path)
        return paths

    #finds the moves that are just moving a piece a single space forward
    def simple_moves(self, piece):
        moves = []
        for direction in piece.get_directions():
            destination = vector_add(piece.pos, direction)
            if not in_bounds(destination, self.columns):
                continue
            if not is_dark_square(destination):
                continue
            if not self[destination]:
                moves.append([destination])
        return moves

    #gets every move of a piece
    def get_piece_moves(self, piece):
        capture_paths = self.capture_paths(piece, [], set())
        simple_paths = self.simple_moves(piece)
        moves = [Move(piece.pos, path) for path in capture_paths]
        moves.extend([Move(piece.pos, path) for path in simple_paths])
        return moves

    #gets every move of a every piece
    def get_all_moves(self, turn):
        capture_moves = []
        quiet_moves = []
        for piece in list(self.piece_map[turn]):
            for move in self.get_piece_moves(piece):
                if len(move.steps) == 1 and abs(move.start[0] - move.end[0]) == 1:
                    quiet_moves.append(move)
                else:
                    capture_moves.append(move)

        return capture_moves + quiet_moves

    def apply_move(self, move):
        piece = self[move.start]
        if not piece:
            return 0

        current_pos = move.start
        for destination in move.steps:
            if abs(destination[0] - current_pos[0]) == 2:
                middle = (
                    (current_pos[0] + destination[0]) // 2,
                    (current_pos[1] + destination[1]) // 2,
                )
                captured = self[middle]
                if captured:
                    self.piece_map[captured.get_player()].remove(captured)
                    self[middle] = 0

            self[current_pos] = 0
            self[destination] = piece
            piece.pos = destination
            current_pos = destination

            if not piece.king and destination[1] == PROMOTION_ROW[piece.get_player()]:
                piece.king = True
                piece.name = "king"

        return 1

    def get_moves(self, turn):
        move_set = {}
        for move in self.get_all_moves(turn):
            move_set.setdefault(move.start, []).append(move.end)
        return move_set

#object to hold game state
class CheckersGame:
    HUMAN_PLAYER = 0
    AI_PLAYER = 1

    def __init__(self):
        self.board = ChessBoard(BOARD_SIZE, BOARD_SIZE)
        self.turn = self.HUMAN_PLAYER
        self.winner = None
        self.must_continue_from = None
        self.setup_board()

    #initalizes board
    def setup_board(self):
        for row in range(3):
            for col in range(BOARD_SIZE):
                pos = (col, row)
                if is_dark_square(pos):
                    self.board.create_piece(CheckerPiece, pos, self.AI_PLAYER)
        for row in range(5, 8):
            for col in range(BOARD_SIZE):
                pos = (col, row)
                if is_dark_square(pos):
                    self.board.create_piece(CheckerPiece, pos, self.HUMAN_PLAYER)

    #restarts the game
    def reset(self):
        self.board = ChessBoard(BOARD_SIZE, BOARD_SIZE)
        self.turn = self.HUMAN_PLAYER
        self.winner = None
        self.must_continue_from = None
        self.setup_board()

    #add a checker to the board
    def create_piece(self, piece, pos, player, king=False):
        self.board.create_piece(piece, pos, player, king)

    #display for console mode
    def display(self):
        print()
        if self.winner is not None:
            print(f"{NUMBER_TO_COLOR_CONVERT[self.winner]} wins!")
        else:
            print(f"It's {NUMBER_TO_COLOR_CONVERT[self.turn]}'s turn")
        print(self.board)

    #legacy logic, used to differentiate between regular and capture moves, still works but a little reduntant
    def get_legal_moves(self, start_pos=None):
        if self.winner is not None:
            return []

        if self.must_continue_from is not None:
            piece = self.board[self.must_continue_from]
            if not piece:
                self.must_continue_from = None
                return self.board.get_all_moves(self.turn)
            moves = self.board.get_piece_moves(piece)
            capture_moves = [
                move
                for move in moves
                if len(move.steps) > 1 or abs(move.start[0] - move.end[0]) == 2
            ]
            return capture_moves if capture_moves else moves

        all_moves = self.board.get_all_moves(self.turn)
        if start_pos is None:
            return all_moves
        return [move for move in all_moves if move.start == start_pos]

    def get_moves(self):
        return self.board.get_moves(self.turn)

    def get_grid_data(self):
        return self.board.get_grid()

    def get_board(self):
        return self.board

    #search for a winner
    def check_winner(self):
        if self.board.piece_count(self.HUMAN_PLAYER) == 0:
            self.winner = self.AI_PLAYER
            return
        if self.board.piece_count(self.AI_PLAYER) == 0:
            self.winner = self.HUMAN_PLAYER
            return
        if not self.board.get_all_moves(self.turn):
            self.winner = 1 - self.turn

    def apply_move(self, move):
        if self.winner is not None:
            return 0

        legal_moves = self.get_legal_moves(move.start)
        if move not in legal_moves:
            return 0

        self.board.apply_move(move)

        is_capture = len(move.steps) > 1 or abs(move.start[0] - move.end[0]) == 2
        if is_capture:
            remaining = [
                candidate
                for candidate in self.board.get_piece_moves(self.board[move.end])
                if len(candidate.steps) > 1 or abs(candidate.start[0] - candidate.end[0]) == 2
            ]
            if remaining:
                self.must_continue_from = move.end
                self.check_winner()
                return 1

        self.must_continue_from = None
        self.turn = 1 - self.turn
        self.check_winner()
        return 1

    def move(self, start_pos, destination_pos):
        legal_moves = self.get_legal_moves(start_pos)
        for candidate in legal_moves:
            if candidate.end == destination_pos:
                return self.apply_move(candidate)
        return 0


Puzzle = CheckersGame


if __name__ == "__main__":
    game = CheckersGame()
    game.display()
    print(game.get_moves())

    while True:
        if game.winner is not None:
            print("Press q to quit.")
        token = input().strip()
        if token.capitalize() == "Q":
            exit()
        try:
            start_str, dest_str = token.split()
            start_pos = tuple(map(int, start_str.strip("(),").split(",")))
            destination_pos = tuple(map(int, dest_str.strip("(),").split(",")))
            if game.move(start_pos, destination_pos):
                game.display()
        except ValueError:
            print('Invalid format. Use "(x,y) (x,y)" or q to quit.')
