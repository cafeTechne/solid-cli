
import os
import sys
from textual_serve.server import Server

# Add the project root to sys.path so solid_cli can be imported
sys.path.insert(0, "..")

# Set environment variable to help textual find the app
os.environ['PYTHONPATH'] = ".."

if __name__ == "__main__":
    server = Server(
        "python -m solid_cli.main monitor",
        host="127.0.0.1",
        port=8004,
        public_url="http://127.0.0.1:8004",
    )
    server.serve()
