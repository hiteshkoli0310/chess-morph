<div align="center">
  <br>
  <!-- Replace with your actual logo path/URL if available, otherwise just text -->
  <h1>ChessMorph</h1>
  <br>
  <strong>A Dynamic Chess Bot That Adapts to Your Skill Level</strong>
</div>
<br>
<p align="center">
  <a href="https://chess-morph.vercel.app/">
    <img src="https://img.shields.io/badge/Live-Demo-dessert?style=for-the-badge&logo=vercel&color=D81B60" alt="Live Demo">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" alt="License">
  </a>
  <img src="https://img.shields.io/github/stars/hiteshkoli0310/chess-morph?style=for-the-badge&color=yellow" alt="Stars">
  <img src="https://img.shields.io/github/issues/hiteshkoli0310/chess-morph?style=for-the-badge&color=red" alt="Issues">
  <img src="https://img.shields.io/github/last-commit/hiteshkoli0310/chess-morph?style=for-the-badge&color=green" alt="Last Commit">
</p>

Welcome to **ChessMorph**, a unique chess engine that doesn't just crush youit plays *with* you. Unlike standard engines that play at a fixed Elo, ChessMorph dynamically adjusts its strength in real-time based on your current position, giving you a chance to recover from mistakes or challenging you when you're ahead.

## What is ChessMorph?

ChessMorph is a Full-Stack Chess Application that wraps the powerful **Stockfish** engine with a custom Python heuristic layer ("Morph Engine"). It analyzes the game state after every move to determine if it should play optimally, make a human-like mistake, or blunder intentionally to keep the game engaging.

It features a beautiful, dessert-themed UI built with React and a robust FastAPI backend.

## Table of Contents

- [What is ChessMorph?](#what-is-chessmorph)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Adaptive Logic](#adaptive-logic)
- [Getting Started](#getting-started)
- [Live Demo](#live-demo)
- [Contributing](#contributing)
- [License](#license)

## Features

 **Adaptive AI**: The bot weakens slightly when you are losing heavily, and plays sharper when you are winning.  
 **Dessert Theme UI**: A distinctive "Strawberry & Chocolate" visual style for a relaxing gameplay experience.  
 **Live Engine Stats**: See real-time analysis, including CP loss, blunder probability, and search depth.  
 **FastAPI Backend**: High-performance Python backend serving Stockfish analysis via UCI protocol.  
 **Dockerized**: Fully containerized backend for easy deployment on Render/Cloud.  
 **Fault Tolerant**: Includes database fallbacks (In-Memory) so the game is always playable.

## Tech Stack

We use a modern stack to combine high-performance computing with a reactive frontend:

- **Frontend**: [React](https://reactjs.org/), [Tailwind CSS](https://tailwindcss.com/), [Chess.js](https://github.com/jhlywa/chess.js), [React-Chessboard](https://github.com/Clariity/react-chessboard)
- **Backend**: [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Python-Chess](https://python-chess.readthedocs.io/)
- **Engine**: [Stockfish 16](https://stockfishchess.org/) (via UCI) / Morph Heuristics
- **Database**: [MongoDB](https://www.mongodb.com/) (Optional, with In-Memory fallback)
- **Deployment**: [Docker](https://www.docker.com/), [Render](https://render.com/)

## Adaptive Logic

The `MorphEngine` isn't just a wrapper; it implements a "Human-Like" engagement algorithm:

1.  **Winning Margin**: If the user is winning by >250cp, the bot enters "Defensive Mode" (plays best moves).
2.  **Losing Margin**: If the user is losing, the bot increases its "Blunder Probability", intentionally picking sub-optimal moves to give the user a fighting chance.
3.  **Natural Mistakes**: When deciding to error, it filters for "Natural" mistakes (200-400cp loss) that look like plausible human errors, rather than obvious suicides.

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.9+)
- Stockfish executable (or modify path in `backend/morph_engine.py`)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/hiteshkoli0310/chess-morph.git
    cd chess-morph
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    pip install -r requirements.txt
    
    # Download Stockfish and place it in stockfish/ folder OR update morph_engine.py path
    
    uvicorn main:app --reload
    ```

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    npm start
    ```

## Live Demo

Play against the bot right now: **[ChessMorph Live](https://chessmorph.vercel.app)**

## Contributing

Contributions are welcome! Whether it's adding new "Personalities" to the engine, improving the React UI, or optimizing the Docker build.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes
4.  Push to the Branch
5.  Open a Pull Request

## License

This project is licensed under the MIT License.

<br>

<p align="center">
  <img src="https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif" width="200" alt="Chess Gif">
  <br>
  <strong>Checkmate.</strong> 
</p>

[ Back to Top](#table-of-contents)
