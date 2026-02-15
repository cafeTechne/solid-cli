
import asyncio
import os
import time
import shutil
import random
import string
from pathlib import Path
import sys
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.insert(0, parent_dir)
print(f"DEBUG: sys.path[0] = {sys.path[0]}")

try:
    import solid_cli
    print(f"DEBUG: solid_cli location = {solid_cli.__file__}")
    from solid_cli.client import SolidClient
except ImportError as e:
    print(f"DEBUG: Import failed: {e}")
    sys.exit(1)

from solid_cli.auth import OIDCAuthProvider
from solid_cli.sync import sync_local_to_remote

# Configuration
TEST_DIR = Path("benchmark_data")
REMOTE_URL = "http://127.0.0.1:8004/benchmark/"
FILE_COUNTS = {
    "small": 50,  # 1KB
    "medium": 10, # 100KB
    "large": 2,   # 1MB
}

def generate_random_content(size):
    return ''.join(random.choices(string.ascii_letters, k=size)).encode()

def setup_data():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir()
    
    print(f"Generating test data in {TEST_DIR}...")
    
    # Small files (1KB)
    for i in range(FILE_COUNTS["small"]):
        with open(TEST_DIR / f"small_{i}.txt", "wb") as f:
            f.write(generate_random_content(1024))
            
    # Medium files (100KB)
    for i in range(FILE_COUNTS["medium"]):
        with open(TEST_DIR / f"medium_{i}.txt", "wb") as f:
            f.write(generate_random_content(100 * 1024))
            
    # Large files (1MB)
    for i in range(FILE_COUNTS["large"]):
        with open(TEST_DIR / f"large_{i}.txt", "wb") as f:
            f.write(generate_random_content(1024 * 1024))

    total_size = sum(f.stat().st_size for f in TEST_DIR.glob("*"))
    print(f"Generated {sum(FILE_COUNTS.values())} files, Total Size: {total_size / 1024 / 1024:.2f} MB")
    return total_size

async def run_benchmark():
    # Setup
    total_size = setup_data()
    
    # Mock Auth (since we are hitting our own unauthenticated TUI/Server endpoint which might reject PUTs... 
    # Actually checking tui.py/main.py... main.py just runs the TUI. The server running is `textual serve`. 
    # Textual serve is read-only for static files usually? 
    # WAIT. The user is running `run_tui_server.py` which runs `solid_cli.main monitor`.
    # That is just a TUI. It does NOT accept HTTP PUT requests for file storage.
    # It is NOT a Solid Pod Server. 
    # To benchmark SYNC, we need a Solid Pod.
    # Since we don't have one, we will use a MockClient to simulate network latency.
    
    print("\nStarting Benchmark (Simulated Network)...")
    
    class MockClient(SolidClient):
        def __init__(self):
            self.bytes_uploaded = 0
            
        async def head(self, url):
            # Simulate 10ms latency
            await asyncio.sleep(0.01)
            class Response:
                status_code = 404
            return Response()
            
        async def put(self, url, content, description):
            # Simulate network transfer (10MB/s)
            size = len(content)
            latency = size / (10 * 1024 * 1024) 
            await asyncio.sleep(latency + 0.05) # +50ms Overhead
            self.bytes_uploaded += size
            class Response:
                status_code = 201
            return Response()

    client = MockClient()
    
    start_time = time.time()
    
    await sync_local_to_remote(
        client,
        str(TEST_DIR),
        REMOTE_URL,
        on_log=lambda msg: None # Silence logs
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nBenchmark Complete!")
    print(f"Time: {duration:.2f} seconds")
    print(f"Throughput: {total_size / 1024 / 1024 / duration:.2f} MB/s")
    print(f"Files/Sec: {sum(FILE_COUNTS.values()) / duration:.2f} files/s")
    
    # Cleanup
    shutil.rmtree(TEST_DIR)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
