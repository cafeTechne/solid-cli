"""FUSE filesystem for mounting Solid Pods."""

import platform
import sys
import ctypes
from pathlib import Path
from typing import Optional
import fuse
from fuse import FUSE, FuseOSError, Operations
import errno
import os
from .client import SolidClient


class SolidOperations(Operations):
    """FUSE filesystem operations for Solid Pod."""
    
    def __init__(self, client: SolidClient, remote_url: str):
        """Initialize Solid filesystem operations.
        
        Args:
            client: SolidClient for remote operations
            remote_url: Base URL of remote Solid Pod
        """
        self.client = client
        self.remote_url = remote_url.rstrip("/")
        self._cache = {}  # Simple cache for directory listings
    
    def readdir(self, path: str, fh):
        """List directory contents.
        
        Args:
            path: Virtual filesystem path
            fh: File handle (unused)
        
        Yields:
            Directory entries: ".", "..", and file/folder names
        """
        try:
            # Standard entries
            yield "."
            yield ".."
            
            # Construct remote URL
            remote_path = self.remote_url + path.rstrip("/")
            
            # For now, return empty listing (would require WebDAV/PROPFIND)
            # In production, implement actual directory listing
            
        except Exception as e:
            raise FuseOSError(errno.EIO)
    
    def getattr(self, path: str, fh=None):
        """Get file/directory attributes.
        
        Args:
            path: Virtual filesystem path
            fh: File handle (unused)
        
        Returns:
            Dictionary of file attributes (st_mode, st_size, st_mtime, etc.)
        """
        # Get uid/gid portably
        uid = os.getuid() if hasattr(os, 'getuid') else 0
        gid = os.getgid() if hasattr(os, 'getgid') else 0
        
        # Root directory
        if path == "/":
            return {
                "st_mode": 0o40755,  # Directory
                "st_nlink": 2,
                "st_size": 0,
                "st_uid": uid,
                "st_gid": gid,
                "st_mtime": 0,
            }
        
        try:
            # Construct remote URL
            remote_path = self.remote_url + path
            
            # Try HEAD request to check if file exists
            response = self.client._client.head(remote_path, timeout=5)
            
            if response.status_code == 200:
                size = int(response.headers.get("content-length", 0))
                return {
                    "st_mode": 0o100644,  # Regular file
                    "st_nlink": 1,
                    "st_size": size,
                    "st_uid": uid,
                    "st_gid": gid,
                    "st_mtime": 0,
                }
            else:
                raise FuseOSError(errno.ENOENT)
                
        except FuseOSError:
            raise
        except Exception as e:
            raise FuseOSError(errno.EIO)
    
    def read(self, path: str, size: int, offset: int, fh) -> bytes:
        """Read file contents.
        
        Args:
            path: Virtual filesystem path
            size: Number of bytes to read
            offset: Byte offset to start from
            fh: File handle (unused)
        
        Returns:
            File content bytes
        """
        try:
            # Construct remote URL
            remote_path = self.remote_url + path
            
            # Fetch file from remote
            headers = {"Range": f"bytes={offset}-{offset + size - 1}"}
            response = self.client._client.get(
                remote_path,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in (200, 206):
                return response.content
            else:
                raise FuseOSError(errno.EIO)
                
        except Exception as e:
            raise FuseOSError(errno.EIO)


def mount_pod(mount_point: str, client: SolidClient, remote_url: str) -> None:
    """Mount a Solid Pod as a filesystem.
    
    Detects the operating system and checks for required dependencies:
    - Windows: Requires WinFsp (https://winfsp.dev)
    - Linux/macOS: Requires libfuse
    
    Args:
        mount_point: Local filesystem path to mount at
        client: SolidClient instance for remote operations
        remote_url: Base URL of Solid Pod
    
    Raises:
        RuntimeError: If FUSE dependencies are not installed
    """
    system = platform.system()
    
    # Validate mount point
    mount_path = Path(mount_point)
    if not mount_path.exists():
        mount_path.mkdir(parents=True, exist_ok=True)
    
    # Check OS-specific dependencies
    if system == "Windows":
        # Windows requires WinFsp
        try:
            import winfsp
        except ImportError:
            raise RuntimeError(
                "WinFsp is required for FUSE on Windows.\n"
                "Please install from: https://winfsp.dev\n"
                "Then reinstall fusepy: pip install fusepy"
            )
    
    elif system in ("Linux", "Darwin"):  # Darwin is macOS
        # Check for libfuse
        if system == "Linux":
            try:
                import ctypes
                ctypes.CDLL("libfuse.so.2") or ctypes.CDLL("libfuse.so.3")
            except (OSError, AttributeError):
                raise RuntimeError(
                    "libfuse is required for FUSE on Linux.\n"
                    "Install with: sudo apt-get install libfuse-dev (Ubuntu/Debian)\n"
                    "Or: sudo yum install fuse-devel (CentOS/RHEL)"
                )
        
        # macOS requires osxfuse
        if system == "Darwin":
            try:
                import ctypes
                ctypes.CDLL("/usr/local/lib/libfuse.dylib") or \
                ctypes.CDLL("/opt/homebrew/lib/libfuse.dylib")
            except (OSError, AttributeError):
                raise RuntimeError(
                    "osxfuse is required for FUSE on macOS.\n"
                    "Install with: brew install osxfuse"
                )
    
    # Mount the filesystem
    operations = SolidOperations(client, remote_url)
    FUSE(
        operations,
        mount_point,
        foreground=True,
        allow_other=False,
        nothreads=True
    )
