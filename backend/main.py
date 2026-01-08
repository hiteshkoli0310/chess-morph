from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess
import random
import uuid

from database import create_game, update_game_move
from morph_engine import MorphEngine

app = FastAPI()

API_VERSION = "1.0.1 (Debug Fix)"

@app.get("/health")
def health_check():
    return {"status": "ok", "version": API_VERSION}

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

class ConfigRequest(BaseModel):
    USER_WINNING_MARGIN: int = None
    USER_LOSING_MARGIN: int = None
    FAST_PLAY_LIMIT: float = None
    MISTAKE_SEVERE_MIN: int = None
    MISTAKE_NATURAL_MIN: int = None
    MISTAKE_NATURAL_MAX: int = None

@app.post("/update-config")
def update_config(req: ConfigRequest):
    config = req.dict(exclude_none=True)
    engine.update_config(config)
    return {"status": "updated", "config": config}

@app.post("/start-game")
def start_game(req: StartGameRequest):
    try:
        side = req.side
        if side == "random":
            side = random.choice(["white", "black"])
        
        board = chess.Board()
        
        # HANDICAP: Remove Bot's Queen to give user a strong start
        if side == "white": # User is White, Bot is Black
            board.remove_piece_at(chess.D8)
        else: # User is Black, Bot is White
            board.remove_piece_at(chess.D1)

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
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Start Game Error: {str(e)}")

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

    prev_fen = req.fen if req.user_move != "0000" else None
    user_move = req.user_move if req.user_move != "0000" else None

    bot_move_uci, stats = engine.get_move(new_fen, req.time_taken, prev_fen=prev_fen, user_move_uci=user_move)
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
