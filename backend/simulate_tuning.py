import chess
import chess.engine
import os
import sys
import random
from morph_engine import MorphEngine

# Add current directory to path so we can import MorphEngine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_game():
    print("--- Starting Tuning Simulation ---")
    print("Simulating a game between 'Weak User' and 'MorphEngine'...")

    # Initialize MorphEngine
    morph = MorphEngine()
    
    # Initialize a separate engine to act as the "User" (Weak Stockfish)
    # We'll use the same stockfish binary but limit its strength
    stockfish_path = morph.engine_path
    if not os.path.exists(stockfish_path):
        print(f"Error: Stockfish not found at {stockfish_path}")
        return

    user_engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    # Limit user engine to be weak (e.g., 100ms per move, low skill)
    # Note: Stockfish doesn't always respect Skill Level perfectly without UCI options, 
    # but low time is usually enough to make it blunder occasionally.
    user_limit = chess.engine.Limit(time=0.05) 

    board = chess.Board()
    
    # Play until game over or max moves reached
    move_count = 0
    MAX_MOVES = 200

    while not board.is_game_over() and move_count < MAX_MOVES:
        move_count += 1
        print(f"\nMove {move_count}:")
        
        # --- USER MOVE (White) ---
        # We want the user to make some mistakes to trigger "Mercy Mode"
        # Let's sometimes play a random legal move to simulate a blunder
        if random.random() < 0.2:
            print("User is making a random blunder...")
            user_move = random.choice(list(board.legal_moves))
        else:
            result = user_engine.play(board, user_limit)
            user_move = result.move
            
        board.push(user_move)
        print(f"User played: {user_move.uci()}")
        
        if board.is_game_over():
            break

        # --- MORPH ENGINE MOVE (Black) ---
        # We need to pass: fen, time_taken, prev_fen, user_move_uci
        # Reconstruct state for MorphEngine
        # The board is now at the state AFTER user moved.
        current_fen = board.fen()
        
        # We need the FEN *before* the user moved for CP loss calc.
        # Since we just pushed the move, we can pop it to get prev, then push back.
        board.pop()
        prev_fen = board.fen()
        board.push(user_move)
        
        # Simulate user taking some time (e.g., 2-5 seconds)
        time_taken = random.uniform(1.0, 6.0)
        
        print(f"MorphEngine analyzing...")
        bot_move_uci, stats = morph.get_move(
            fen=current_fen, 
            time_taken_seconds=time_taken, 
            prev_fen=prev_fen, 
            user_move_uci=user_move.uci()
        )
        
        if bot_move_uci:
            print(f"MorphEngine Stats: {stats}")
            print(f"MorphEngine played: {bot_move_uci}")
            board.push(chess.Move.from_uci(bot_move_uci))
        else:
            print("MorphEngine resigned or failed.")
            break

    print("\n--- Simulation Complete ---")
    print(f"Result: {board.result()}")
    print(f"Termination: {board.outcome().termination if board.outcome() else 'Max moves reached'}")
    print(f"Final FEN: {board.fen()}")
    print(f"Game Log should be updated at: {morph.log_file}")
    
    user_engine.quit()

if __name__ == "__main__":
    simulate_game()
