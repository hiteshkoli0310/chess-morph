import chess
import chess.engine
import math

import os

import csv
from datetime import datetime

class MorphEngine:
    def __init__(self):
        # Define base_dir globally for the class scope
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to stockfish executable
        if os.name == 'nt': # Windows
            self.engine_path = os.path.normpath(os.path.join(base_dir, "..", "stockfish", "stockfish-windows-x86-64-avx2.exe"))
        else: # Linux (Docker/Cloud)
            # We will install stockfish via apt-get in the Dockerfile
            self.engine_path = "/usr/games/stockfish"
            if not os.path.exists(self.engine_path):
                 self.engine_path = "/usr/bin/stockfish" # Alternative path

        if not os.path.exists(self.engine_path) and os.name == 'nt':
            print(f"WARNING: Stockfish engine not found at {self.engine_path}")

        # --- LOGGING SETUP ---
        self.log_file = os.path.join(base_dir, "..", "game_log.csv")
        self._init_log()

        # --- ENGAGEMENT TUNING PARAMETERS ---
        # 1. Game State Thresholds (Centipawns)
        # If User CP > WINNING_MARGIN, Bot plays max strength to defend.
        # If User CP < LOSING_MARGIN, Bot plays mistakes to let user recover.
        self.USER_WINNING_MARGIN = 250
        self.USER_LOSING_MARGIN = 0 # Start helping as soon as user is losing

        # 2. Time Heuristics
        # If user plays faster than this (seconds), we might treat it as "casual/blitz" play.
        self.FAST_PLAY_LIMIT = 2.5

        # 3. Bot Mistake Magnitudes (How bad should the mistake be?)
        # Severe mistake: Drops evaluation by ~400cp (e.g. hanging a piece)
        self.MISTAKE_SEVERE_MIN = 400
        # Natural mistake: Drops evaluation by ~200-400cp (e.g. positional error)
        self.MISTAKE_NATURAL_MIN = 200
        self.MISTAKE_NATURAL_MAX = 400

    def update_config(self, config: dict):
        """
        Update tuning parameters dynamically.
        Expected keys: USER_WINNING_MARGIN, USER_LOSING_MARGIN, FAST_PLAY_LIMIT, etc.
        """
        print(f"Updating MorphEngine config: {config}")
        if "USER_WINNING_MARGIN" in config: self.USER_WINNING_MARGIN = config["USER_WINNING_MARGIN"]
        if "USER_LOSING_MARGIN" in config: self.USER_LOSING_MARGIN = config["USER_LOSING_MARGIN"]
        if "FAST_PLAY_LIMIT" in config: self.FAST_PLAY_LIMIT = config["FAST_PLAY_LIMIT"]
        if "MISTAKE_SEVERE_MIN" in config: self.MISTAKE_SEVERE_MIN = config["MISTAKE_SEVERE_MIN"]
        if "MISTAKE_NATURAL_MIN" in config: self.MISTAKE_NATURAL_MIN = config["MISTAKE_NATURAL_MIN"]
        if "MISTAKE_NATURAL_MAX" in config: self.MISTAKE_NATURAL_MAX = config["MISTAKE_NATURAL_MAX"]

    def _init_log(self):
        # Initialize CSV with headers if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "move_number", "user_move_uci", "time_taken", 
                    "user_eval", "best_eval", "cp_loss", "is_blunder", 
                    "bot_persona", "bot_move", "bot_depth"
                ])

    def get_move(self, fen, time_taken_seconds, prev_fen=None, user_move_uci=None):
        board = chess.Board(fen)
        
        # If game is over, return None
        if board.is_game_over():
            return None, {}

        with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
            # 1. Analyze position to get current score (from User's perspective)
            # We assume the board is set to the position AFTER the user moved, so it is BOT's turn.
            
            # Analyze with a small depth/time to get a baseline evaluation
            info = engine.analyse(board, chess.engine.Limit(time=0.1))
            score = info["score"].relative
            
            # Score is relative to the side to move (Bot).
            # User Score = -Bot Score
            if score.is_mate():
                user_cp = -10000 if score.mate() > 0 else 10000
            else:
                user_cp = -score.score()

            # --- PERFORMANCE TRACKING ---
            cp_loss = 0
            best_val = user_cp # Default if we can't calc
            is_blunder = False
            
            if prev_fen and user_move_uci:
                try:
                    # Analyze the position BEFORE user moved to find what the best score WAS
                    prev_board = chess.Board(prev_fen)
                    # We want score relative to the side that was about to move (User)
                    prev_info = engine.analyse(prev_board, chess.engine.Limit(time=0.1))
                    prev_score = prev_info["score"].relative
                    
                    if prev_score.is_mate():
                        best_val = 10000 if prev_score.mate() > 0 else -10000
                    else:
                        best_val = prev_score.score()
                    
                    # CP Loss = (Score of Best Move) - (Score of Actual Move)
                    # Note: user_cp is the score of the actual move
                    cp_loss = best_val - user_cp
                    
                    # Simple blunder classification
                    if cp_loss > 200:
                        is_blunder = True
                        
                except Exception as e:
                    print(f"Error calculating CP loss: {e}")

            # 2. Rubber Band & Time Heuristic Logic
            bot_move = None
            stats = {}
            
            common_stats = {
                "user_cp": user_cp,
                "time_taken": time_taken_seconds,
                "cp_loss": cp_loss,
                "is_blunder": is_blunder
            }
            
            # Case A: User is Winning (Score > Threshold)
            if user_cp > self.USER_WINNING_MARGIN:
                move, depth = self._play_best_move(engine, board, depth=6)
                bot_move = move
                stats = {
                    "difficulty": "Defensive Master", 
                    "depth": depth, 
                    "blunder_prob": "0% (Trying to hold)",
                    **common_stats
                }

            # Case B: User is Losing (Score < Threshold)
            elif user_cp < self.USER_LOSING_MARGIN:
                # If losing badly (<-300), force severe mistake regardless of time
                if user_cp < -300:
                    move, depth = self._play_mistake(engine, board, min_drop=self.MISTAKE_SEVERE_MIN)
                    stats = {
                        "difficulty": "Mercy Mode (Rescue)", 
                        "depth": depth, 
                        "blunder_prob": "Critical (Rescue)",
                        **common_stats
                    }
                    bot_move = move
                elif time_taken_seconds < self.FAST_PLAY_LIMIT:
                    move, depth = self._play_mistake(engine, board, min_drop=self.MISTAKE_SEVERE_MIN)
                    bot_move = move
                    stats = {
                        "difficulty": "Mercy Mode (Speed)", 
                        "depth": depth, 
                        "blunder_prob": "High (Giving chance)",
                        **common_stats
                    }
                else:
                    move, depth = self._play_mistake(engine, board, min_drop=self.MISTAKE_NATURAL_MIN, max_drop=self.MISTAKE_NATURAL_MAX)
                    bot_move = move
                    stats = {
                        "difficulty": "Assist Mode", 
                        "depth": depth, 
                        "blunder_prob": "Medium (Positional error)",
                        **common_stats
                    }

            # Case C: Game is Even
            else:
                # Weaken the balanced mode significantly (depth 8 is approx 1200-1400 Elo)
                move, depth = self._play_best_move(engine, board, depth=1)
                bot_move = move
                stats = {
                    "difficulty": "Balanced Challenger", 
                    "depth": depth, 
                    "blunder_prob": "Low",
                    **common_stats
                }
            
            # --- REALTIME STATS ---
            print(f"[{stats.get('difficulty')}] User CP: {user_cp} | Loss: {cp_loss} | Time: {time_taken_seconds}s | Bot Move: {bot_move}")

            # --- LOG TO CSV ---
            try:
                with open(self.log_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.now().isoformat(),
                        board.fullmove_number,
                        user_move_uci or "start",
                        time_taken_seconds,
                        user_cp,
                        best_val,
                        cp_loss,
                        is_blunder,
                        stats.get("difficulty", "Unknown"),
                        bot_move,
                        stats.get("depth", 0)
                    ])
            except Exception as e:
                print(f"Logging error: {e}")

            return bot_move, stats

    def _play_best_move(self, engine, board, depth=None):
        # Skill 20 is default for Stockfish
        # Use analyse to get depth info
        limit = chess.engine.Limit(depth=depth) if depth else chess.engine.Limit(time=0.5)
        info = engine.analyse(board, limit, multipv=1)
        if not info:
             return None, 0
        best_line = info[0]
        return best_line["pv"][0].uci(), best_line["depth"]

    def _play_mistake(self, engine, board, min_drop, max_drop=None):
        # Use MultiPV to find suboptimal moves
        limit = chess.engine.Limit(depth=4)
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
