"""Synchronization logic for local-to-remote Solid Pod sync."""

import asyncio
import os
from pathlib import Path
from typing import Callable, Optional
from .client import SolidClient


async def sync_local_to_remote(
    client: SolidClient,
    local_dir: str,
    remote_url: str,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    on_log: Optional[Callable[[str], None]] = None,
) -> None:
    """Synchronize local directory to remote Solid Pod.
    
    Crawls local directory, checks if files exist remotely via HEAD requests,
    and uploads new/modified files via PUT requests using parallel workers.
    
    Args:
        client: SolidClient instance
        local_dir: Local directory path to sync
        remote_url: Remote Solid Pod base URL
        on_progress: Progress callback (bytes_sent, total_bytes, description)
        on_log: Logging callback for messages
    """
    local_path = Path(local_dir)
    
    if not local_path.exists():
        msg = f"Local directory not found: {local_dir}"
        if on_log:
            on_log(msg)
        raise ValueError(msg)
    
    files_to_upload = []
    total_size = 0
    
    # Crawl local directory
    for root, dirs, files in os.walk(local_path):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(local_path)
            remote_path = remote_url.rstrip("/") + "/" + str(rel_path).replace("\\", "/")
            size = file_path.stat().st_size
            
            files_to_upload.append((file_path, remote_path, size))
            total_size += size
            
            if on_log:
                on_log(f"Found: {rel_path}")
    
    if on_log:
        on_log(f"Total files: {len(files_to_upload)}, Size: {total_size} bytes")
    
    # Create semaphore for parallel uploads (max 10 concurrent)
    sem = asyncio.Semaphore(10)
    bytes_sent = 0
    bytes_lock = asyncio.Lock()
    
    async def upload_worker(file_info):
        """Worker coroutine to upload a single file with semaphore control."""
        nonlocal bytes_sent
        local_file, remote_path, file_size = file_info
        
        async with sem:
            try:
                # HEAD check - see if file exists
                head_response = await client.head(remote_path)
                
                if head_response.status_code == 200:
                    if on_log:
                        on_log(f"File exists (skipping): {local_file.name}")
                    async with bytes_lock:
                        bytes_sent += file_size
                    if on_progress:
                        on_progress(bytes_sent, total_size, f"Syncing {local_file.name}")
                    return
            except Exception as e:
                if on_log:
                    on_log(f"HEAD check failed for {local_file.name}: {e}")
            
            # Upload file
            try:
                with open(local_file, "rb") as f:
                    content = f.read()
                
                response = await client.put(
                    remote_path,
                    content=content,
                    description=f"Uploading {local_file.name}",
                )
                
                if response.status_code in (200, 201):
                    if on_log:
                        on_log(f"✓ Uploaded: {local_file.name}")
                else:
                    if on_log:
                        on_log(f"✗ Upload failed: {local_file.name} (Status: {response.status_code})")
                
                async with bytes_lock:
                    bytes_sent += file_size
                if on_progress:
                    on_progress(bytes_sent, total_size, f"Syncing {local_file.name}")
                    
            except Exception as e:
                if on_log:
                    on_log(f"✗ Upload error: {local_file.name} - {e}")
    
    # Create and execute all upload tasks in parallel
    tasks = [upload_worker(f) for f in files_to_upload]
    await asyncio.gather(*tasks)
    
    if on_log:
        on_log("Sync complete!")
