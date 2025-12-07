import React, { useEffect, useRef } from "react";

const MoveHistory = ({ history }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const moves = [];
  for (let i = 0; i < history.length; i += 2) {
    const whiteMove = history[i];
    const blackMove = history[i + 1];

    moves.push({
      number: Math.floor(i / 2) + 1,
      white: typeof whiteMove === "object" ? whiteMove.san : whiteMove,
      black: blackMove
        ? typeof blackMove === "object"
          ? blackMove.san
          : blackMove
        : "",
    });
  }

  return (
    <div className="bg-dessert-vanilla rounded-xl shadow-sm border border-orange-100 h-full flex flex-col overflow-hidden">
      <div className="p-4 bg-white/50 border-b border-orange-50 flex items-center justify-between">
        <h3 className="font-bold text-dessert-chocolate flex items-center gap-2">
          Move History
        </h3>
        <span className="text-xs font-medium px-2 py-1 bg-orange-100 text-dessert-chocolate rounded-md">
          {history.length} moves
        </span>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-2 space-y-0.5 scroll-smooth"
      >
        {moves.map((move, index) => (
          <div
            key={index}
            className={`grid grid-cols-[3rem_1fr_1fr] items-center px-3 py-2 rounded-lg text-sm transition-colors ${
              index % 2 === 0 ? "bg-white/60" : "bg-transparent"
            } hover:bg-orange-50`}
          >
            <span className="text-dessert-milkChoc font-mono text-xs opacity-70">
              {move.number}.
            </span>
            <span className="font-semibold text-dessert-chocolate">
              {move.white}
            </span>
            <span className="font-semibold text-dessert-chocolate">
              {move.black}
            </span>
          </div>
        ))}

        {moves.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-dessert-milkChoc/50 p-8 text-center">
            <p className="text-sm">Game hasn't started yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MoveHistory;
