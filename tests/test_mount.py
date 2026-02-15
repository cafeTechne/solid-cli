"""Tests for FUSE mount functionality."""

import pytest
import platform
import errno
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from solid_cli.mount import SolidOperations, mount_pod
from fuse import FuseOSError


class TestSolidOperations:
    """Test FUSE filesystem operations."""
    
    @pytest.fixture
    def mock_client(self):
        """Provide mocked SolidClient."""
        client = AsyncMock()
        client._client = MagicMock()
        return client
    
    @pytest.fixture
    def operations(self, mock_client):
        """Provide SolidOperations instance."""
        return SolidOperations(mock_client, "https://pod.example.org")
    
    def test_operations_initialization(self, operations):
        """Test SolidOperations initialization."""
        assert operations.client is not None
        assert operations.remote_url == "https://pod.example.org"
        assert operations._cache == {}
    
    def test_readdir_root(self, operations):
        """Test listing root directory."""
        entries = list(operations.readdir("/", None))
        
        # Should have at least "." and ".."
        assert "." in entries
        assert ".." in entries
    
    def test_readdir_subdirectory(self, operations):
        """Test listing subdirectory."""
        entries = list(operations.readdir("/folder", None))
        
        # Should still have "." and ".."
        assert "." in entries
        assert ".." in entries
    
    def test_readdir_error_handling(self, operations, mock_client):
        """Test readdir error handling."""
        # Mock head to raise exception
        mock_client._client.head.side_effect = Exception("Connection error")
        
        entries = list(operations.readdir("/folder", None))
        
        # Should still return standard entries
        assert "." in entries
        assert ".." in entries
    
    def test_getattr_root(self, operations):
        """Test getting attributes of root directory."""
        attrs = operations.getattr("/")
        
        # Root should be a directory
        assert attrs["st_mode"] == 0o40755  # Directory
        assert attrs["st_nlink"] == 2
        assert attrs["st_size"] == 0
    
    def test_getattr_file_exists(self, operations, mock_client):
        """Test getting attributes of existing file."""
        # Mock successful HEAD request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "1024"}
        mock_client._client.head.return_value = mock_response
        
        attrs = operations.getattr("/file.txt")
        
        # Should be a regular file
        assert attrs["st_mode"] == 0o100644  # File
        assert attrs["st_nlink"] == 1
        assert attrs["st_size"] == 1024
    
    def test_getattr_file_not_found(self, operations, mock_client):
        """Test getting attributes of non-existent file."""
        # Mock 404 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client._client.head.return_value = mock_response
        
        # Should raise ENOENT error
        with pytest.raises(FuseOSError) as exc_info:
            operations.getattr("/nonexistent.txt")
        
        assert exc_info.value.errno == errno.ENOENT
    
    def test_read_file(self, operations, mock_client):
        """Test reading file contents."""
        # Mock successful GET request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"file content"
        mock_client._client.get.return_value = mock_response
        
        content = operations.read("/file.txt", 100, 0, None)
        
        assert content == b"file content"
    
    def test_read_file_with_range(self, operations, mock_client):
        """Test reading file with byte range."""
        # Mock successful 206 (Partial Content) response
        mock_response = MagicMock()
        mock_response.status_code = 206
        mock_response.content = b"partial"
        mock_client._client.get.return_value = mock_response
        
        content = operations.read("/file.txt", 10, 5, None)
        
        assert content == b"partial"
        
        # Verify Range header was sent
        call_args = mock_client._client.get.call_args
        assert "Range" in call_args[1]["headers"]
    
    def test_read_file_error(self, operations, mock_client):
        """Test read error handling."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client._client.get.return_value = mock_response
        
        # Should raise EIO error
        with pytest.raises(FuseOSError) as exc_info:
            operations.read("/file.txt", 100, 0, None)
        
        assert exc_info.value.errno == errno.EIO


class TestMountPod:
    """Test mount_pod function."""
    
    def test_mount_pod_validates_mount_point(self, tmp_path):
        """Test that mount_pod creates mount point if it doesn't exist."""
        mount_point = tmp_path / "mnt" / "pod"
        mock_client = MagicMock()
        
        # Should create the directory structure
        assert not mount_point.exists()
        
        with patch("solid_cli.mount.FUSE") as mock_fuse:
            mock_fuse.side_effect = KeyboardInterrupt()
            with patch("solid_cli.mount.platform.system", return_value="Linux"):
                with patch("solid_cli.mount.ctypes.CDLL"):
                    try:
                        mount_pod(str(mount_point), mock_client, "https://pod.org")
                    except KeyboardInterrupt:
                        pass
        
        # Mount point should have been created
        assert mount_point.exists()
    
    def test_mount_pod_linux_requires_libfuse(self, tmp_path):
        """Test that Linux detects missing libfuse."""
        mock_client = MagicMock()
        mount_point = str(tmp_path / "mnt")
        
        with patch("solid_cli.mount.platform.system", return_value="Linux"):
            with patch("solid_cli.mount.ctypes.CDLL", side_effect=OSError("libfuse not found")):
                with pytest.raises(RuntimeError) as exc_info:
                    mount_pod(mount_point, mock_client, "https://pod.org")
                
                assert "libfuse" in str(exc_info.value)
    
    def test_mount_pod_macos_requires_osxfuse(self, tmp_path):
        """Test that macOS detects missing osxfuse."""
        mock_client = MagicMock()
        mount_point = str(tmp_path / "mnt")
        
        with patch("solid_cli.mount.platform.system", return_value="Darwin"):
            with patch("solid_cli.mount.ctypes.CDLL", side_effect=OSError("osxfuse not found")):
                with pytest.raises(RuntimeError) as exc_info:
                    mount_pod(mount_point, mock_client, "https://pod.org")
                
                assert "osxfuse" in str(exc_info.value)
    
    def test_mount_pod_calls_fuse(self, tmp_path):
        """Test that mount_pod calls FUSE with correct arguments."""
        mock_client = MagicMock()
        mount_point = str(tmp_path / "mnt")
        remote_url = "https://pod.example.org"
        
        with patch("solid_cli.mount.FUSE") as mock_fuse:
            mock_fuse.side_effect = KeyboardInterrupt()
            with patch("solid_cli.mount.platform.system", return_value="Linux"):
                with patch("solid_cli.mount.ctypes.CDLL") as mock_cdll:
                    try:
                        mount_pod(mount_point, mock_client, remote_url)
                    except KeyboardInterrupt:
                        pass
                    
                    # Verify FUSE was called
                    mock_fuse.assert_called_once()
                    
                    # Check arguments
                    call_args = mock_fuse.call_args
                    assert call_args[1]["foreground"] == True
                    assert call_args[1]["nothreads"] == True
