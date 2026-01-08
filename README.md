<div align="center">
  <br>
  <h1> ChessMorph</h1>
  <strong>The Chess Engine That Adapts To You</strong>
</div>
<br>
<p align="center">
  <a href="https://chessmorph.vercel.app">
    <img src="https://img.shields.io/badge/Live-Demo-success?style=for-the-badge&logo=vercel" alt="Live Demo">
  </a>
  <a href="https://github.com/hiteshkoli0310/chess-morph/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/hiteshkoli0310/chess-morph?style=for-the-badge" alt="License">
  </a>
  <img src="https://img.shields.io/github/stars/hiteshkoli0310/chess-morph?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/issues/hiteshkoli0310/chess-morph?style=for-the-badge" alt="Issues">
  <img src="https://img.shields.io/github/last-commit/hiteshkoli0310/chess-morph?style=for-the-badge" alt="Last Commit">
</p>

Welcome to **ChessMorph**, an intelligent chess application that goes beyond standard engines. Powered by **Stockfish** and a custom **Python FastAPI backend**, ChessMorph analyzes your gameplay in real-time and provides detailed statistics, centipawn loss tracking, and blunder detection.

Whether you're a grandmaster or a beginner, our sleek, dessert-themed interface ensures a delightful gaming experience.

## Table of Contents

- [What is ChessMorph?](#what-is-chessmorph)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Live Demo](#live-demo)
- [Contributing](#contributing)
- [License](#license)

## Features

 **Adaptive Engine**: Built on top of Stockfish to provide challenging yet human-like gameplay.  
 **Real-time Analytics**: View Centipawn (CP) loss, blunder probability, and search depth after every move.  
 **Dessert UI Theme**: A unique, relaxing visual style featuring "Dessert Chocolate", "Strawberry", and "Vanilla" palettes.  
 **Instant Feedback**: Fast move validation and execution using a highly optimized Python backend.  
 **Robust Backend**: Containerized with Docker and capable of handling complex chess logic with fallback mechanisms.  
 **Responsive Design**: Play seamlessly on desktop or mobile devices.

## Tech Stack

We use a powerful combination of modern web technologies and systems programming:

- **Frontend**: [React](https://reactjs.org/), [Tailwind CSS](https://tailwindcss.com/), [Chess.js](https://github.com/jhlywa/chess.js), [React-Chessboard](https://github.com/Clariity/react-chessboard)
- **Backend**: [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Engine**: [Stockfish](https://stockfishchess.org/) (integrated via python-chess)
- **Database**: [MongoDB](https://www.mongodb.com/) (with In-Memory fallback)
- **DevOps**: [Docker](https://www.docker.com/), [Render](https://render.com/)

## Getting Started

Follow these steps to set up ChessMorph locally on your machine.

### Prerequisites

- Node.js (v14+)
- Python (v3.9+)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/hiteshkoli0310/chess-morph.git
   cd chess-morph
   ```

2. **Backend Setup**

   ```bash
   cd backend
   
   # Create virtual environment (optional but recommended)
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the server
   uvicorn main:app --reload
   ```
   *The backend will start at `http://localhost:8000`*

3. **Frontend Setup**

   Open a new terminal window:
   
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Run the client
   npm start
   ```
   *The frontend will start at `http://localhost:3000`*

## Live Demo

Experience the application live: **[ChessMorph on Vercel](https://chessmorph.vercel.app)**

## Contributing

Contributions are welcome! If you have ideas for new features, better engine tuning, or UI improvements:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br>

<p align="center">
  <img src="https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif" width="300" alt="Chess Gif">
  <br>
  <strong>Checkmate.</strong> 
</p>

[ Back to Top](#table-of-contents)
