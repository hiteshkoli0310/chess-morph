import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client.chessmorph

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
    result = db.games.insert_one(game)
    return str(result.inserted_id)

def update_game_move(game_id, fen, move_uci, is_bot=False):
    from bson.objectid import ObjectId
    db.games.update_one(
        {"_id": ObjectId(game_id)},
        {
            "$set": {"current_fen": fen},
            "$push": {
                "moves": {
                    "uci": move_uci,
                    "by": "bot" if is_bot else "user",
                    "timestamp": datetime.utcnow()
                }
            }
        }
    )

def get_player(guest_id):
    return db.players.find_one({"guest_id": guest_id})

def update_player_rating(guest_id, new_rating):
    db.players.update_one(
        {"guest_id": guest_id},
        {"$set": {"rating": new_rating}},
        upsert=True
    )
