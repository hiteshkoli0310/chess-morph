import React, { useState, useEffect, useRef } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import Cookies from "js-cookie";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [game, setGame] = useState(new Chess());
  const [fen, setFen] = useState("start");
  const [orientation, setOrientation] = useState("white");
  const [isGameStarted, setIsGameStarted] = useState(false);
  const [modalOpen, setModalOpen] = useState(true);
  const [gameId, setGameId] = useState(null);
  const [gameOverData, setGameOverData] = useState(null); // { winner: 'white'|'black'|'draw', reason: 'checkmate'|... }
  const [moveSquares, setMoveSquares] = useState({});
  const [optionSquares, setOptionSquares] = useState({});
  const lastMoveTime = useRef(Date.now());

  useEffect(() => {
    let guestId = Cookies.get("guest_id");
    if (!guestId) {
      guestId = uuidv4();
      Cookies.set("guest_id", guestId);
    }
  }, []);

  // Check for game over conditions
  useEffect(() => {
    if (game.isGameOver()) {
      let winner = "draw";
      let reason = "draw";

      if (game.isCheckmate()) {
        winner = game.turn() === "w" ? "black" : "white";
        reason = "Checkmate";
      } else if (game.isDraw()) {
        reason = "Draw";
      } else if (game.isStalemate()) {
        reason = "Stalemate";
      } else if (game.isThreefoldRepetition()) {
        reason = "Repetition";
      } else if (game.isInsufficientMaterial()) {
        reason = "Insufficient Material";
      }

      setGameOverData({ winner, reason });
    }
  }, [game]);

  const startGame = async (side) => {
    const guestId = Cookies.get("guest_id");
    try {
      const res = await axios.post(`${API_URL}/start-game`, {
        guest_id: guestId,
        side: side,
      });

      setGameId(res.data.game_id);
      setOrientation(res.data.orientation);
      const newGame = new Chess(res.data.fen);
      setGame(newGame);
      setFen(newGame.fen());
      setIsGameStarted(true);
      setModalOpen(false);
      setGameOverData(null);
      lastMoveTime.current = Date.now();

      if (res.data.orientation === "black") {
        // Trigger bot move for white
        makeBotMove(res.data.game_id, null, res.data.fen, 0);
      }
    } catch (err) {
      console.error("Error starting game", err);
    }
  };

  const makeBotMove = async (gId, userMove, currentFen, timeTaken) => {
    try {
      const res = await axios.post(`${API_URL}/get-move`, {
        game_id: gId,
        user_move: userMove || "0000",
        fen: currentFen,
        time_taken: timeTaken,
      });

      if (res.data.bot_move) {
        const newGame = new Chess(res.data.fen);
        setGame(newGame);
        setFen(res.data.fen);
        lastMoveTime.current = Date.now();
      }
    } catch (err) {
      console.error("Error getting bot move", err);
    }
  };

  function onPieceDragBegin(piece, sourceSquare) {
    if (!isGameStarted || gameOverData) return;
    if (game.turn() !== orientation.charAt(0)) return;

    const moves = game.moves({ square: sourceSquare, verbose: true });
    const newSquares = {};

    moves.forEach((move) => {
      newSquares[move.to] = {
        background:
          "radial-gradient(circle, rgba(0,0,0,.2) 25%, transparent 25%)",
        borderRadius: "50%",
      };
    });

    newSquares[sourceSquare] = { background: "rgba(255, 255, 0, 0.4)" };
    setOptionSquares(newSquares);
  }

  function onPieceDragEnd() {
    setOptionSquares({});
  }

  function onDrop(sourceSquare, targetSquare) {
    if (!isGameStarted || gameOverData) return false;
    if (game.turn() !== orientation.charAt(0)) return false;

    const move = {
      from: sourceSquare,
      to: targetSquare,
      promotion: "q",
    };

    try {
      const tempGame = new Chess(game.fen());
      const result = tempGame.move(move);

      if (!result) return false;

      const timeTaken = (Date.now() - lastMoveTime.current) / 1000;
      const userMoveUci = result.from + result.to + (result.promotion || "");
      const fenBeforeMove = game.fen();

      setGame(tempGame);
      setFen(tempGame.fen());
      setOptionSquares({}); // Clear hints

      makeBotMove(gameId, userMoveUci, fenBeforeMove, timeTaken);

      return true;
    } catch (e) {
      return false;
    }
  }

  // Calculate custom square styles (Check highlight + Move hints)
  const customSquareStyles = {
    ...optionSquares,
  };

  // Add King Check Highlight
  if (game.inCheck()) {
    const kingSquare = game.board().reduce((acc, row, rowIndex) => {
      const colIndex = row.findIndex(
        (p) => p && p.type === "k" && p.color === game.turn()
      );
      if (colIndex !== -1) {
        const file = String.fromCharCode(97 + colIndex);
        const rank = 8 - rowIndex;
        return `${file}${rank}`;
      }
      return acc;
    }, null);

    if (kingSquare) {
      customSquareStyles[kingSquare] = {
        backgroundColor:
          "radial-gradient(circle, rgba(255,0,0,.8), transparent 80%)",
        borderRadius: "50%",
      };
    }
  }

  return (
    <div
      className="App"
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        flexDirection: "column",
      }}
    >
      <h1>ChessMorph</h1>
      <div style={{ width: "400px", height: "400px" }}>
        <Chessboard
          position={fen}
          onPieceDrop={onDrop}
          onPieceDragBegin={onPieceDragBegin}
          onPieceDragEnd={onPieceDragEnd}
          boardOrientation={orientation}
          customDarkSquareStyle={{ backgroundColor: "#8D6E63" }} // Milk Chocolate
          customLightSquareStyle={{ backgroundColor: "#F0E68C" }} // White Chocolate
          customSquareStyles={customSquareStyles}
        />
      </div>

      {/* Start Game Modal */}
      {modalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">Select Side</div>
            <div className="modal-subtext">Choose your flavor</div>
            <div
              style={{ display: "flex", justifyContent: "center", gap: "10px" }}
            >
              <button onClick={() => startGame("white")}>White</button>
              <button onClick={() => startGame("black")}>Black</button>
              <button className="secondary" onClick={() => startGame("random")}>
                Random
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Game Over Modal */}
      {gameOverData && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              {gameOverData.winner === "white"
                ? "White Won!"
                : gameOverData.winner === "black"
                ? "Black Won!"
                : "Draw!"}
            </div>
            <div className="modal-subtext">by {gameOverData.reason}</div>

            <div className="player-card">
              <div className="player-info">
                <div
                  className="avatar"
                  style={{ backgroundColor: "white", border: "1px solid #ccc" }}
                ></div>
                <div>
                  <div style={{ fontWeight: "bold" }}>White</div>
                  <div style={{ fontSize: "12px", color: "#666" }}>1200</div>
                </div>
              </div>
              {gameOverData.winner === "white" && (
                <div className="winner-icon">👑</div>
              )}
            </div>

            <div className="player-card">
              <div className="player-info">
                <div
                  className="avatar"
                  style={{ backgroundColor: "black", border: "1px solid #ccc" }}
                ></div>
                <div>
                  <div style={{ fontWeight: "bold" }}>Black</div>
                  <div style={{ fontSize: "12px", color: "#666" }}>1200</div>
                </div>
              </div>
              {gameOverData.winner === "black" && (
                <div className="winner-icon">👑</div>
              )}
            </div>

            <div
              style={{
                marginTop: "20px",
                display: "flex",
                justifyContent: "center",
                gap: "10px",
              }}
            >
              <button
                onClick={() => {
                  setGameOverData(null);
                  setModalOpen(true);
                }}
              >
                New Game
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
