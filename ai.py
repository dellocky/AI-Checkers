"""
Created by Kyle Dellock
5/31/2026

Minimax AI with alpha-beta pruning for checkers.
Search depth is controlled by difficulty level from config.json.
"""

from board import CheckersGame, NUMBER_TO_COLOR_CONVERT
from settings import settings

#Infinity for pruning
INF = 10**9


class CheckersAI:
    def __init__(self, difficulty=None):
        self.difficulty = difficulty or "medium" #backup incase import issues
        self.depth = settings.DIFFICULTY_DEPTHS.get(self.difficulty, 4)
        self.player = CheckersGame.AI_PLAYER

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.depth = settings.DIFFICULTY_DEPTHS.get(difficulty, 4)

    def get_best_move(self, game):
        _, move = self.alphabeta(game, self.depth, -INF, INF, True)
        return move

    #Evaluation function to find the value of a board state 
    def evaluate(self, game):
        #set winning positions to inifinty
        if game.winner == self.player:
            return INF - 1 
        if game.winner == CheckersGame.HUMAN_PLAYER:
            return -INF + 1

        score = 0
        board = game.board
        for player in (CheckersGame.HUMAN_PLAYER, self.player):
            sign = -1 if player == CheckersGame.HUMAN_PLAYER else 1 #invert calulations for the player for minimax algo
            for piece in board.piece_map[player]:
                piece_value = 3 if piece.is_king() else 1 #value of king is 3 regular checkers is 1
                score += sign * piece_value #multiply the value 
                if not piece.is_king():
                    advancement = (7 - piece.pos[1]) if player == self.player else piece.pos[1]
                    score += sign * advancement * 0.05 #evaluate further advanced pieces as being worth more than further back one for nonkings
        return score
    
    #move through simulated moves
    def simulate_move(self, game, move):
        snapshot = {
            "turn": game.turn,
            "winner": game.winner,
            "must_continue_from": game.must_continue_from,
            "board": game.board.copy(),
        }
        game.apply_move(move)
        return snapshot

    def restore(self, game, snapshot):
        game.turn = snapshot["turn"]
        game.winner = snapshot["winner"]
        game.must_continue_from = snapshot["must_continue_from"]
        game.board = snapshot["board"]

    #alpha beta pruning, and the core logic of the minimax algorithim using the above evaluation function
    def alphabeta(self, game, depth, alpha, beta, maximizing):
        if depth == 0 or game.winner is not None:
            return self.evaluate(game), None

        moves = game.get_legal_moves()
        if not moves:
            if game.winner is None:
                return (-INF + 1, None) if maximizing else (INF - 1, None)
            return self.evaluate(game), None

        best_move = moves[0]
        if maximizing:
            best_score = -INF
            for move in moves:
                snapshot = self.simulate_move(game, move)
                score, _ = self.alphabeta(game, depth - 1, alpha, beta, False)
                self.restore(game, snapshot)
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score, best_move

        best_score = INF
        for move in moves:
            snapshot = self.simulate_move(game, move)
            score, _ = self.alphabeta(game, depth - 1, alpha, beta, True)
            self.restore(game, snapshot)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move


if __name__ == "__main__":
    from config import load_config

    config = load_config()
    ai = CheckersAI(config["difficulty"])
    game = CheckersGame()
    game.turn = CheckersGame.AI_PLAYER

    move = ai.get_best_move(game)
    if move:
        game.apply_move(move)
        print(f"Difficulty: {config['difficulty']} (depth {ai.depth})")
        print(f"AI chose: {move}")
        game.display()
    else:
        print("No legal AI moves available.")
