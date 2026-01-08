import os
import uuid
from datetime import datetime

# Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Global State
db = None
USE_MONGO = True
games_memory = {}

# Try Connection
try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client.chessmorph
    print(f"Connected to MongoDB: {MONGO_URL}")
except Exception as e:
    print(f"MongoDB connection failed: {e}. Using In-Memory Fallback.")
    USE_MONGO = False
    db = None

def get_database():
    return db

def create_game(guest_id, side, fen, orientation):
    game = {
        "guest_id": guest_id,
        "side": side,
        "start_fen": fen,
        "current_fen": fen,
        "orientation": orientation,
        "moves": [],
        "created_at": datetime.utcnow(),
        "status": "active"
    }
    
    if USE_MONGO and db is not None:
        try:
            result = db.games.insert_one(game)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting to Mongo: {e}. Falling back to memory.")
            
    # Fallback / Memory
    game_id = str(uuid.uuid4())
    game["_id"] = game_id
    games_memory[game_id] = game
    return game_id

def update_game_move(game_id, fen, move_uci, is_bot=False):
    update_data = {
        "current_fen": fen,
        "last_updated": datetime.utcnow()
    }
    
    if USE_MONGO and db is not None:
        try:
            from bson.objectid import ObjectId
            db.games.update_one(
                {"_id": ObjectId(game_id)},
                {"$set": update_data, "$push": {"moves": move_uci}}
            )
            return
        except Exception as e:
            print(f"Error updating Mongo: {e}")
            
    # Memory Fallback
    if game_id in games_memory:
        games_memory[game_id]["current_fen"] = fen
        games_memory[game_id]["moves"].append(move_uci)
