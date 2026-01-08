import os
import sys
import time
import subprocess
import shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, 'backend')
LOG_PATH = os.path.join(ROOT, 'game_log.csv')

def ensure_backend_env():
    req = os.path.join(BACKEND, 'requirements.txt')
    if os.path.exists(req):
        print('Note: Ensure packages in requirements.txt are installed')

def rotate_log(tag: str):
    if os.path.exists(LOG_PATH):
        dest = os.path.join(ROOT, f"game_log_{tag}.csv")
        shutil.copyfile(LOG_PATH, dest)
        print(f"Rotated current log to {dest}")
        # Clear log to start fresh for batch
        os.remove(LOG_PATH)

def run_one_game(i: int):
    print(f"\n=== Running game {i+1} ===")
    result = subprocess.run([sys.executable, os.path.join(BACKEND, 'simulate_tuning.py')], cwd=BACKEND)
    if result.returncode != 0:
        print(f"Game {i+1} failed with code {result.returncode}")

def analyze():
    print("\n=== Analysis after batch ===")
    subprocess.run([sys.executable, os.path.join(BACKEND, 'analyze_log.py')], cwd=BACKEND)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Run batch MorphEngine simulations')
    parser.add_argument('-n', '--num-games', type=int, default=1000, help='Number of full games to simulate')
    parser.add_argument('--rotate-tag', type=str, default=datetime.now().strftime('%Y%m%d_%H%M%S'), help='Tag to rotate previous log file')
    args = parser.parse_args()

    ensure_backend_env()
    rotate_log(args.rotate_tag)

    start = time.time()
    for i in range(args.num_games):
        run_one_game(i)
    dur = time.time() - start
    print(f"\nBatch completed: {args.num_games} games in {dur/60:.1f} min")

    analyze()

if __name__ == '__main__':
    main()
