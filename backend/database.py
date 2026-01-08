import os
import uuid
from datetime import datetime

# Check config
MONGO_URL = os.getenv("MONGO_URL")
USE_MONGO = MONGO_URL is not None

db = None
if USE_MONGO:
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000) # 2 sec timeout
        # Force connection check
        client.admin.command('ping')
        db = client.chessmorph
        print(f"Connected to MongoDB: {MONGO_URL}")
    except Exception as e:
        print(f"Failed to connect to Mongo, falling back to memory: {e}")
        USE_MONGO = False
        db = None

# In-Memory Fallback Storage
games_memory = {}
players_memory = {}

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

    if USE_MONGO:
        result = db.games.insert_one(game)
        return str(result.inserted_id)
    else:
        # Generate a fake ID
        game_id = str(uuid.uuid4())
        game["_id"] = game_id # simulate mongo _id
        games_memory[game_id] = game
        return game_id

def update_game_move(game_id, fen, move_uci, is_bot=False):
    move_entry = {
        "uci": move_uci,
        "by": "bot" if is_bot else "user",
        "timestamp": datetime.utcnow()
    }

    if USE_MONGO:
        from bson.objectid import ObjectId
        db.games.update_one(
            {"_id": ObjectId(game_id)},
            {
                "$set": {"current_fen": fen},
                "$push": {"moves": move_entry}
            }
        )
    else:
        if game_id in games_memory:
            games_memory[game_id]["current_fen"] = fen
            games_memory[game_id]["moves"].append(move_entry)

def get_player(guest_id):
    if USE_MONGO:
        return db.players.find_one({"guest_id": guest_id})
    else:
        return players_memory.get(guest_id)

def update_player_rating(guest_id, new_rating):
    if USE_MONGO:
        db.players.update_one(
            {"guest_id": guest_id},
            {"$set": {"rating": new_rating}},
            upsert=True
        )
    else:
        if guest_id not in players_memory:
            players_memory[guest_id] = {"guest_id": guest_id}
        players_memory[guest_id]["rating"] = new_rating

