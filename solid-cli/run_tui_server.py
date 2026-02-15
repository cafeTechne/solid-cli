from textual_serve.server import Server
import asyncio
import sys
import os

if __name__ == "__main__":
    # Construct command using current Python executable
    cmd = f"{sys.executable} -m solid_cli.main monitor"

    # Set PYTHONPATH to include the parent directory (where solid_cli lives)
    # The source code is in ../solid_cli, not src/solid_cli
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] = f"{src_path}{os.pathsep}{os.environ['PYTHONPATH']}"
    else:
        os.environ["PYTHONPATH"] = src_path

    # Initialize Server on port 8003 to avoid conflicts
    server = Server(cmd, port=8003, host="127.0.0.1")
    server.serve()
