import chess
import chess.engine
import math

import os

class MorphEngine:
    def __init__(self):
        # Path to stockfish executable
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.engine_path = os.path.normpath(os.path.join(base_dir, "..", "stockfish", "stockfish-windows-x86-64-avx2.exe"))
        
        if not os.path.exists(self.engine_path):
            print(f"WARNING: Stockfish engine not found at {self.engine_path}")

    def get_move(self, fen, time_taken_seconds):
        board = chess.Board(fen)
        
        # If game is over, return None
        if board.is_game_over():
            return None

        with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
            # 1. Analyze position to get current score (from User's perspective)
            # We assume the board is set to the position AFTER the user moved, so it is BOT's turn.
            # We need to evaluate the position before the bot moves.
            
            # Analyze with a small depth/time to get a baseline evaluation
            info = engine.analyse(board, chess.engine.Limit(time=0.1))
            score = info["score"].relative
            
            # Score is relative to the side to move (Bot).
            # User Score = -Bot Score
            if score.is_mate():
                # If bot has mate, user is losing badly (-inf). If bot is mated, user is winning (+inf).
                user_cp = -10000 if score.mate() > 0 else 10000
            else:
                user_cp = -score.score()

            print(f"User CP: {user_cp}, Time Taken: {time_taken_seconds}")

            # 2. Rubber Band & Time Heuristic
            
            # Case A: User Winning (> 200cp)
            if user_cp > 200:
                # If time_taken < 3: Play Aggressive/Complex (Skill 20)
                # Else: Play Best Defense (Skill 20)
                # In both cases for MVP, we play the best move (Skill 20).
                move, depth = self._play_best_move(engine, board)
                return move, {"difficulty": "Grandmaster", "depth": depth, "blunder_prob": "0%"}

            # Case B: User Losing (< -200cp)
            elif user_cp < -200:
                if time_taken_seconds < 3:
                    # Play Severe Mistake (Blunder > 300cp drop)
                    move, depth = self._play_mistake(engine, board, min_drop=300)
                    return move, {"difficulty": "Beginner", "depth": depth, "blunder_prob": "High"}
                else:
                    # Play Natural Mistake (~150cp drop)
                    move, depth = self._play_mistake(engine, board, min_drop=150, max_drop=250)
                    return move, {"difficulty": "Intermediate", "depth": depth, "blunder_prob": "Medium"}

            # Case C: Even (-200 to 200)
            else:
                # Play Complex/Best Move (Skill 20)
                move, depth = self._play_best_move(engine, board)
                return move, {"difficulty": "Grandmaster", "depth": depth, "blunder_prob": "0%"}

    def _play_best_move(self, engine, board):
        # Skill 20 is default for Stockfish
        # Use analyse to get depth info
        info = engine.analyse(board, chess.engine.Limit(time=0.5), multipv=1)
        if not info:
             return None, 0
        best_line = info[0]
        return best_line["pv"][0].uci(), best_line["depth"]

    def _play_mistake(self, engine, board, min_drop, max_drop=None):
        # Use MultiPV to find suboptimal moves
        limit = chess.engine.Limit(time=0.5)
        # Get top 20 moves to find a suitable mistake
        info = engine.analyse(board, limit, multipv=20)
        
        if not info:
            return self._play_best_move(engine, board)

        # Best move score (Bot's perspective)
        best_score = info[0]["score"].relative
        if best_score.is_mate():
            best_val = 10000 if best_score.mate() > 0 else -10000
        else:
            best_val = best_score.score()

        candidates = []

        for i, line in enumerate(info):
            if i == 0: continue # Skip best move
            
            move_score = line["score"].relative
            if move_score.is_mate():
                move_val = 10000 if move_score.mate() > 0 else -10000
            else:
                move_val = move_score.score()
            
            drop = best_val - move_val
            
            if drop >= min_drop:
                if max_drop and drop > max_drop:
                    continue
                candidates.append(line["pv"][0])

        if candidates:
            # Return the first matching candidate (usually the best of the bad moves)
            return candidates[0].uci(), info[0]["depth"]
        
        # If no suitable mistake found (e.g. forced moves), play best move or random legal?
        # Fallback to best move to avoid crashing
        return self._play_best_move(engine, board)
