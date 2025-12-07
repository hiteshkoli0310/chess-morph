import pymongo
import chess
import chess.pgn
from datetime import datetime
import os

# 1. Connect to MongoDB
# Using localhost as we are running this script locally
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = pymongo.MongoClient(MONGO_URL)
db = client["chessmorph"]
games_collection = db["games"]

def select_and_export_game():
    # 2. Get all games sorted by most recent
    games_cursor = games_collection.find().sort("_id", -1)
    games = list(games_cursor)
    
    if not games:
        print("No games found in database.")
        return

    print(f"\n--- Found {len(games)} Games ---")
    for i, g in enumerate(games):
        moves_count = len(g.get("moves", []))
        created_at = g.get("created_at", "Unknown Date")
        player_side = g.get("side", "unknown")
        print(f"{i+1}. ID: {g['_id']} | Date: {created_at} | Player: {player_side} | Moves: {moves_count}")
    
    print("-" * 30)
    
    try:
        choice = input(f"Select a game number (1-{len(games)}): ")
        index = int(choice) - 1
        if index < 0 or index >= len(games):
            print("Invalid selection.")
            return
        game_doc = games[index]
    except ValueError:
        print("Invalid input.")
        return

    print(f"\nSelected Game ID: {game_doc['_id']}")
    
    # 3. Setup PGN Headers
    game = chess.pgn.Game()
    game.headers["Event"] = "ChessMorph Game"
    game.headers["Site"] = "Localhost"
    
    # Format date if it's a datetime object
    date_val = game_doc.get("created_at")
    if isinstance(date_val, datetime):
        game.headers["Date"] = date_val.strftime("%Y.%m.%d")
    else:
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    
    # Determine sides
    # In create_game, 'side' is the player's side.
    player_side = game_doc.get("side", "white")
    if player_side == "white":
        game.headers["White"] = "Player"
        game.headers["Black"] = "ChessMorph Bot"
    else:
        game.headers["White"] = "ChessMorph Bot"
        game.headers["Black"] = "Player"

    # 4. Replay Moves
    node = game
    board = chess.Board()
    
    moves = game_doc.get("moves", [])
    
    for move_data in moves:
        # Schema uses 'uci' key
        uci = move_data.get("uci")
        
        if uci:
            try:
                move = chess.Move.from_uci(uci)
                if move in board.legal_moves:
                    node = node.add_variation(move)
                    board.push(move)
                    
                    # Add metadata as comments
                    by_who = move_data.get("by", "unknown")
                    
                    comment_parts = []
                    if by_who:
                        comment_parts.append(f"By: {by_who}")
                    
                    if comment_parts:
                        node.comment = ", ".join(comment_parts)
                        
            except ValueError:
                print(f"Skipping invalid move: {uci}")
                continue

    # 5. Output
    print("\n" + "="*30)
    print("   COPY THE PGN BELOW   ")
    print("="*30 + "\n")
    print(game)
    print("\n" + "="*30)

if __name__ == "__main__":
    select_and_export_game()
