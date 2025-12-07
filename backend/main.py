from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess
import random
import uuid

from database import create_game, update_game_move
from morph_engine import MorphEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MorphEngine()

class StartGameRequest(BaseModel):
    guest_id: str
    side: str # "white", "black", "random"

class MoveRequest(BaseModel):
    game_id: str
    user_move: str # UCI
    fen: str # FEN before user move (or we can reconstruct, but passing current FEN is easier)
    time_taken: float

@app.post("/start-game")
def start_game(req: StartGameRequest):
    side = req.side
    if side == "random":
        side = random.choice(["white", "black"])
    
    board = chess.Board()
    fen = board.fen()
    
    game_id = create_game(req.guest_id, side, fen, side)
    
    # If user is black, bot needs to make first move? 
    # For MVP simplicity, let's assume user triggers bot move if they are black via frontend logic 
    # or we handle it here. Let's stick to standard flow: return game setup.
    
    return {
        "game_id": game_id,
        "fen": fen,
        "orientation": side
    }

@app.post("/get-move")
def get_move(req: MoveRequest):
    # 1. Update DB with user move
    # We need to apply user move to FEN to get new FEN
    board = chess.Board(req.fen)
    try:
        if req.user_move == "0000":
             # Dummy move for bot start
             pass
        else:
            move = chess.Move.from_uci(req.user_move)
            if move in board.legal_moves:
                board.push(move)
            else:
                raise HTTPException(status_code=400, detail="Illegal move")
    except ValueError:
        if req.user_move == "0000":
             pass
        else:
             raise HTTPException(status_code=400, detail="Invalid UCI")

    new_fen = board.fen()
    if req.user_move != "0000":
        update_game_move(req.game_id, new_fen, req.user_move, is_bot=False)
    
    # 2. Call Engine
    if board.is_game_over():
        return {"bot_move": None, "fen": new_fen, "game_over": True}

    bot_move_uci, stats = engine.get_move(new_fen, req.time_taken)
    
    if bot_move_uci:
        board.push(chess.Move.from_uci(bot_move_uci))
        final_fen = board.fen()
        update_game_move(req.game_id, final_fen, bot_move_uci, is_bot=True)
        return {
            "bot_move": bot_move_uci,
            "fen": final_fen,
            "game_over": board.is_game_over(),
            "stats": stats
        }
    else:
        return {"bot_move": None, "fen": new_fen, "game_over": True}
