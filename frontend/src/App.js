import React, { useState, useEffect, useRef } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import Cookies from "js-cookie";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";
import {
  Play,
  Settings,
  AlertTriangle,
  Trophy,
  Flag,
  Crown,
  X,
} from "lucide-react";
import MoveHistory from "./components/MoveHistory";

const API_URL = process.env.REACT_APP_API_URL || "https://chessmorph-backend.onrender.com";

function App() {
  const [game, setGame] = useState(new Chess());
  const [fen, setFen] = useState("start");
  const [orientation, setOrientation] = useState("white");
  const [isGameStarted, setIsGameStarted] = useState(false);
  const [modalOpen, setModalOpen] = useState(true);
  const [gameId, setGameId] = useState(null);
  const [gameOverData, setGameOverData] = useState(null);
  const [engineStats, setEngineStats] = useState(null);
  const [showStats, setShowStats] = useState(false);
  const [optionSquares, setOptionSquares] = useState({});
  const lastMoveTime = useRef(Date.now());

  useEffect(() => {
    let guestId = Cookies.get("guest_id");
    if (!guestId) {
      guestId = uuidv4();
      Cookies.set("guest_id", guestId);
    }
  }, []);

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
        makeBotMove(res.data.game_id, null, res.data.fen, 0, newGame.pgn());
      }
    } catch (err) {
      console.error("Error starting game", err);
    }
  };

  const makeBotMove = async (
    gId,
    userMove,
    currentFen,
    timeTaken,
    currentPgn
  ) => {
    try {
      const res = await axios.post(`${API_URL}/get-move`, {
        game_id: gId,
        user_move: userMove || "0000",
        fen: currentFen,
        time_taken: timeTaken,
      });

      console.log("Bot Move Response:", JSON.stringify(res.data, null, 2)); // DEBUG LOG

      if (res.data.bot_move) {
        const newGame = new Chess();
        newGame.loadPgn(currentPgn || "");

        const moveStr = res.data.bot_move;
        const from = moveStr.substring(0, 2);
        const to = moveStr.substring(2, 4);
        const promotion =
          moveStr.length > 4 ? moveStr.substring(4, 5) : undefined;

        newGame.move({ from, to, promotion });

        setGame(newGame);
        setFen(newGame.fen());
        lastMoveTime.current = Date.now();

        if (res.data.stats) {
          console.log(
            "Setting Engine Stats:",
            JSON.stringify(res.data.stats, null, 2)
          ); // DEBUG LOG
          setEngineStats(res.data.stats);
        } else {
          console.warn("No stats received from backend"); // DEBUG LOG
        }
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
    console.log("onDrop called:", sourceSquare, targetSquare); // DEBUG LOG
    if (!isGameStarted) {
      console.log("onDrop ignored: Game not started");
      return false;
    }
    if (gameOverData) {
      console.log("onDrop ignored: Game over");
      return false;
    }
    if (game.turn() !== orientation.charAt(0)) {
      console.log(
        "onDrop ignored: Not user turn. Turn:",
        game.turn(),
        "Orientation:",
        orientation
      );
      return false;
    }

    const move = {
      from: sourceSquare,
      to: targetSquare,
      promotion: "q",
    };

    try {
      const tempGame = new Chess();
      tempGame.loadPgn(game.pgn());
      const result = tempGame.move(move);

      if (!result) {
        console.log("onDrop ignored: Illegal move");
        return false;
      }

      console.log("Move valid. Sending to backend..."); // DEBUG LOG

      const timeTaken = (Date.now() - lastMoveTime.current) / 1000;
      const userMoveUci = result.from + result.to + (result.promotion || "");
      const fenBeforeMove = game.fen();

      setGame(tempGame);
      setFen(tempGame.fen());
      setOptionSquares({});

      makeBotMove(
        gameId,
        userMoveUci,
        fenBeforeMove,
        timeTaken,
        tempGame.pgn()
      );

      return true;
    } catch (e) {
      console.error("onDrop error:", e);
      return false;
    }
  }

  const customSquareStyles = {
    ...optionSquares,
  };

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
          "radial-gradient(circle, rgba(216, 27, 96, 0.8), transparent 80%)", // Strawberry
        borderRadius: "50%",
      };
    }
  }

  const handleResign = () => {
    if (!isGameStarted || gameOverData) return;

    const winner = orientation === "white" ? "black" : "white";
    setGameOverData({ winner, reason: "Resignation" });
  };

  const handleReset = () => {
    setModalOpen(true);
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-dessert-text bg-dessert-vanilla relative">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-orange-100 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-tr from-dessert-milkChoc to-dessert-chocolate rounded-lg flex items-center justify-center text-white shadow-md transform hover:rotate-12 transition-transform duration-300">
              <Crown className="w-5 h-5 fill-current" />
            </div>
            <h1 className="text-xl md:text-2xl font-extrabold tracking-tight text-dessert-chocolate">
              ChessMorph
            </h1>
          </div>

          <div className="flex items-center gap-2 md:gap-4">
            {isGameStarted && !gameOverData && (
              <button
                onClick={handleResign}
                className="flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 text-sm font-semibold text-dessert-strawberry bg-red-50 hover:bg-red-100 rounded-full transition-colors"
                title="Resign Game"
              >
                <Flag className="w-4 h-4 fill-current" />
                <span className="hidden sm:inline">Resign</span>
              </button>
            )}
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 text-sm font-semibold text-dessert-chocolate bg-orange-50 hover:bg-orange-100 rounded-full transition-colors"
            >
              <Play className="w-4 h-4 fill-current" />
              <span className="hidden sm:inline">New Game</span>
            </button>
            <div className="relative">
              <button
                onClick={() => setShowStats(!showStats)}
                className={`p-2 rounded-full transition-colors relative ${
                  showStats
                    ? "bg-orange-100 text-dessert-chocolate"
                    : "text-dessert-chocolate hover:bg-orange-50"
                }`}
              >
                <Settings className="w-5 h-5" />
                {engineStats && !showStats && (
                  <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white"></span>
                )}
              </button>

              {showStats && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-orange-100 p-4 z-50 animate-in fade-in zoom-in-95 duration-200">
                  <h3 className="font-bold text-dessert-chocolate mb-3 border-b border-orange-50 pb-2">
                    Engine Stats
                  </h3>
                  {engineStats ? (
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-stone-500">Bot Persona</span>
                        <span className="font-bold text-dessert-strawberry text-right">
                          {engineStats.difficulty || "Unknown"}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-stone-500">Search Depth</span>
                        <span className="font-mono bg-orange-50 px-2 py-0.5 rounded text-dessert-chocolate">
                          {engineStats.depth || 0}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-stone-500">Blunder Prob</span>
                        <span className="font-bold text-dessert-mint">
                          {engineStats.blunder_prob || "N/A"}
                        </span>
                      </div>
                      {engineStats.user_cp !== undefined && (
                        <div className="flex justify-between items-center border-t border-orange-50 pt-2 mt-2">
                          <span className="text-stone-500">Your Advantage</span>
                          <span
                            className={`font-mono font-bold ${
                              engineStats.user_cp > 0
                                ? "text-green-600"
                                : "text-red-600"
                            }`}
                          >
                            {engineStats.user_cp > 0 ? "+" : ""}
                            {engineStats.user_cp} cp
                          </span>
                        </div>
                      )}
                      {engineStats.cp_loss !== undefined && (
                        <div className="flex justify-between items-center">
                          <span className="text-stone-500">CP Loss</span>
                          <span
                            className={`font-mono ${
                              engineStats.cp_loss > 50
                                ? "text-red-500 font-bold"
                                : "text-stone-600"
                            }`}
                          >
                            {engineStats.cp_loss}
                          </span>
                        </div>
                      )}
                      {engineStats.time_taken !== undefined && (
                        <div className="flex justify-between items-center">
                          <span className="text-stone-500">Time Taken</span>
                          <span className="font-mono text-stone-600">
                            {typeof engineStats.time_taken === "number"
                              ? engineStats.time_taken.toFixed(2)
                              : engineStats.time_taken}
                            s
                          </span>
                        </div>
                      )}
                      {engineStats.is_blunder && (
                        <div className="mt-2 text-center bg-red-100 text-red-700 font-bold py-1 rounded animate-pulse text-xs uppercase tracking-wider">
                          Blunder Detected!
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center text-stone-400 py-4 italic">
                      Make a move to see stats...
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-4 md:p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8 items-start">
          {/* Left Column: Status & Board */}
          <div className="flex flex-col gap-6 w-full max-w-[600px] mx-auto lg:max-w-none">
            {/* Status Bar */}
            <div className="flex items-center justify-between bg-white px-5 py-3 rounded-xl shadow-sm border border-orange-50">
              <div className="flex items-center gap-3">
                <div
                  className={`w-3 h-3 rounded-full ${
                    game.turn() === "w"
                      ? "bg-amber-100 border-2 border-amber-900"
                      : "bg-amber-900"
                  }`}
                />
                <span className="font-bold text-lg text-dessert-chocolate">
                  {game.turn() === "w" ? "White's Turn" : "Black's Turn"}
                </span>
              </div>

              <div className="flex gap-2">
                {game.inCheck() && !game.isCheckmate() && (
                  <span className="px-3 py-1 bg-dessert-strawberry text-white text-xs font-bold uppercase tracking-wider rounded-full shadow-sm flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" /> Check
                  </span>
                )}
                {game.isCheckmate() && (
                  <span className="px-3 py-1 bg-dessert-chocolate text-white text-xs font-bold uppercase tracking-wider rounded-full shadow-sm flex items-center gap-1">
                    <Trophy className="w-3 h-3" /> Checkmate
                  </span>
                )}
              </div>
            </div>

            {/* Chessboard Area */}
            <div className="relative w-full max-w-[70vh] mx-auto aspect-square shadow-2xl rounded-xl border-[12px] border-white bg-white z-0">
              <Chessboard
                position={fen}
                onPieceDrop={onDrop}
                onPieceDragBegin={onPieceDragBegin}
                onPieceDragEnd={onPieceDragEnd}
                boardOrientation={orientation}
                customDarkSquareStyle={{ backgroundColor: "#8D6E63" }} // Milk Chocolate
                customLightSquareStyle={{ backgroundColor: "#FFF8E1" }} // Vanilla
                customSquareStyles={customSquareStyles}
                animationDuration={200}
              />
            </div>

            <div className="lg:hidden text-center text-sm text-stone-500 mt-2">
              Scroll down for move history
            </div>
          </div>

          {/* Right Column: Move History */}
          <div className="w-full lg:h-[600px] lg:sticky lg:top-24">
            <MoveHistory history={game.history({ verbose: true })} />
          </div>
        </div>
      </main>

      {/* Start Game Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-dessert-chocolate/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-dessert-vanilla rounded-2xl shadow-2xl p-8 w-full max-w-sm border-4 border-dessert-milkChoc text-center">
            <h2 className="text-2xl font-bold text-dessert-strawberry mb-2">
              Select Side
            </h2>
            <p className="text-dessert-chocolate mb-6">Choose your flavor</p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => startGame("white")}
                className="px-6 py-3 bg-white border-2 border-dessert-milkChoc rounded-xl hover:bg-orange-50 font-bold text-dessert-chocolate transition-all"
              >
                White
              </button>
              <button
                onClick={() => startGame("black")}
                className="px-6 py-3 bg-dessert-chocolate border-2 border-dessert-chocolate rounded-xl hover:bg-dessert-dark text-white font-bold transition-all"
              >
                Black
              </button>
              <button
                onClick={() => startGame("random")}
                className="px-6 py-3 bg-dessert-mint text-white rounded-xl hover:bg-teal-600 font-bold transition-all"
              >
                Random
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Game Over Modal */}
      {gameOverData && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-dessert-chocolate/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-dessert-vanilla rounded-2xl shadow-2xl p-8 w-full max-w-sm border-4 border-dessert-milkChoc text-center transform scale-100 animate-in zoom-in-95 duration-200 relative">
            <button
              onClick={() => setGameOverData(null)}
              className="absolute top-4 right-4 p-1 text-dessert-chocolate/50 hover:text-dessert-chocolate hover:bg-orange-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="text-3xl font-extrabold text-dessert-strawberry mb-2">
              {gameOverData.winner === "white"
                ? "White Won!"
                : gameOverData.winner === "black"
                ? "Black Won!"
                : "Draw!"}
            </h2>
            <p className="text-dessert-chocolate mb-8 font-medium">
              by {gameOverData.reason}
            </p>

            <div className="space-y-3 mb-8">
              <div className="flex items-center justify-between bg-white p-3 rounded-xl border border-dessert-milkChoc/30">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg border border-gray-200"></div>
                  <div className="text-left">
                    <div className="font-bold text-dessert-chocolate">
                      White
                    </div>
                    <div className="text-xs text-stone-500">1200</div>
                  </div>
                </div>
                {gameOverData.winner === "white" && (
                  <Trophy className="w-5 h-5 text-dessert-caramel" />
                )}
              </div>

              <div className="flex items-center justify-between bg-white p-3 rounded-xl border border-dessert-milkChoc/30">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-dessert-chocolate rounded-lg border border-gray-800"></div>
                  <div className="text-left">
                    <div className="font-bold text-dessert-chocolate">
                      Black
                    </div>
                    <div className="text-xs text-stone-500">1200</div>
                  </div>
                </div>
                {gameOverData.winner === "black" && (
                  <Trophy className="w-5 h-5 text-dessert-caramel" />
                )}
              </div>
            </div>

            <button
              onClick={() => {
                setGameOverData(null);
                setModalOpen(true);
              }}
              className="w-full py-3 bg-dessert-strawberry text-white font-bold rounded-xl hover:bg-pink-700 transition-colors shadow-lg shadow-pink-200"
            >
              New Game
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
