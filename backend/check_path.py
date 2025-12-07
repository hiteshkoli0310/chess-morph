import os
base_dir = os.path.dirname(os.path.abspath(__file__))
engine_path = os.path.join(base_dir, "..", "stockfish", "stockfish-windows-x86-64-avx2.exe")
print(f"Base dir: {base_dir}")
print(f"Engine path: {engine_path}")
print(f"Exists: {os.path.exists(engine_path)}")
print(f"Abs path: {os.path.abspath(engine_path)}")
