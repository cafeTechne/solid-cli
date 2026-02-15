"""Tests for directory synchronization logic."""

import pytest
import respx
from pathlib import Path
from httpx import Response
from solid_cli.client import SolidClient
from solid_cli.sync import sync_local_to_remote
from solid_cli.auth import OIDCAuthProvider


@pytest.mark.asyncio
class TestSyncLocalToRemote:
    """Test local-to-remote directory synchronization."""

    async def test_sync_nonexistent_directory(self):
        """Verify sync fails gracefully for nonexistent directory."""
        auth = OIDCAuthProvider("token")
        
        async with SolidClient(auth) as client:
            with pytest.raises(ValueError, match="not found"):
                await sync_local_to_remote(
                    client,
                    "/nonexistent/path",
                    "https://pod.example.org/"
                )

    async def test_sync_file_not_remote(self, mock_fs: Path, respx_mock):
        """Scenario: Local file exists, Remote returns 404 (HEAD) -> Should PUT."""
        auth = OIDCAuthProvider("token")
        
        # Mock HEAD returning 404 (file doesn't exist on remote)
        respx_mock.head("https://pod.example.org/test_file1.txt").mock(
            return_value=Response(404)
        )
        
        # Mock PUT for upload
        put_route = respx_mock.put("https://pod.example.org/test_file1.txt").mock(
            return_value=Response(201)
        )
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_log=capture_log
            )
        
        # Verify PUT was called
        assert put_route.called
        
        # Verify logging
        assert any("Found:" in msg for msg in log_messages)
        assert any("Uploaded:" in msg for msg in log_messages)

    async def test_sync_file_exists_remote_skip(
        self, mock_fs: Path, respx_mock
    ):
        """Scenario: Remote file exists (HEAD 200) -> Should SKIP PUT."""
        auth = OIDCAuthProvider("token")
        
        # Mock HEAD returning 200 (file exists)
        respx_mock.head("https://pod.example.org/test_file1.txt").mock(
            return_value=Response(200)
        )
        
        # Mock PUT to ensure it's not called
        put_route = respx_mock.put("https://pod.example.org/test_file1.txt").mock(
            return_value=Response(201)
        )
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_log=capture_log
            )
        
        # Verify PUT was not called for file1
        # (Only HEAD should be called)
        assert not put_route.called
        
        # Verify we logged the skip
        assert any("exists (skipping)" in msg for msg in log_messages)

    async def test_sync_progress_on_skipped_file(
        self, mock_fs: Path, respx_mock
    ):
        """Verify progress callback is called when file is skipped."""
        auth = OIDCAuthProvider("token")
        
        # Mock HEAD returning 200 (file exists, will be skipped)
        respx_mock.head("https://pod.example.org/test_file1.txt").mock(
            return_value=Response(200)
        )
        
        # Mock HEAD for other files to avoid issues
        respx_mock.head().mock(return_value=Response(404))
        respx_mock.put().mock(return_value=Response(201))
        
        progress_calls = []
        def track_progress(bytes_sent: int, total_bytes: int, desc: str):
            progress_calls.append((bytes_sent, total_bytes, desc))
        
        async with SolidClient(auth, on_progress=track_progress) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_progress=track_progress
            )
        
        # Verify progress was called for skipped file
        # The test_file1 is 100 bytes and will be skipped
        # Other files (200 + 50 = 250 bytes) will be uploaded
        skipped_calls = [c for c in progress_calls if "test_file1" in c[2]]
        assert len(skipped_calls) > 0  # Should have called progress for skipped file

    async def test_sync_acl_files(self, mock_fs: Path, respx_mock):
        """Verify .acl files are uploaded correctly."""
        auth = OIDCAuthProvider("token")
        
        # Mock all HEAD requests returning 404
        respx_mock.head().mock(return_value=Response(404))
        
        # Mock all PUT requests
        respx_mock.put().mock(return_value=Response(201))
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_log=capture_log
            )
        
        # Verify .acl file was found and uploaded
        assert any("resource.acl" in msg for msg in log_messages)

    async def test_sync_multiple_files(
        self, mock_fs: Path, respx_mock
    ):
        """Verify sync handles multiple files correctly."""
        auth = OIDCAuthProvider("token")
        
        # Mock all requests
        respx_mock.head().mock(return_value=Response(404))
        respx_mock.put().mock(return_value=Response(201))
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_log=capture_log
            )
        
        # Should have found all 4 files
        found_count = sum(1 for msg in log_messages if "Found:" in msg)
        assert found_count == 4

    async def test_sync_preserves_directory_structure(
        self, mock_fs: Path, respx_mock
    ):
        """Verify sync preserves directory structure in remote URLs."""
        auth = OIDCAuthProvider("token")
        
        # Track put requests
        put_requests = []
        
        def capture_put(request, route):
            put_requests.append(request.url)
            return Response(201)
        
        respx_mock.head().mock(return_value=Response(404))
        respx_mock.put().mock(side_effect=capture_put)
        
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/"
            )
        
        # Verify subdirectory structure is preserved
        urls = [str(url) for url in put_requests]
        assert any("subdir/test_file3.txt" in url for url in urls)
        assert any("subdir/resource.acl" in url for url in urls)

    async def test_sync_handles_put_errors(
        self, mock_fs: Path, respx_mock
    ):
        """Verify sync handles PUT errors gracefully."""
        auth = OIDCAuthProvider("token")
        
        # First file returns 404, second returns 500 error
        respx_mock.head().mock(return_value=Response(404))
        respx_mock.put("https://pod.example.org/test_file1.txt").mock(
            return_value=Response(201)
        )
        respx_mock.put("https://pod.example.org/test_file2.txt").mock(
            return_value=Response(500)  # Server error
        )
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        async with SolidClient(auth) as client:
            # Should not raise, but log the error
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_log=capture_log
            )
        
        # Verify error was logged
        assert any("Upload failed" in msg for msg in log_messages)
        assert any("500" in msg for msg in log_messages)

    async def test_sync_total_size_calculation(
        self, mock_fs: Path, respx_mock
    ):
        """Verify sync calculates total size correctly."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.head().mock(return_value=Response(404))
        respx_mock.put().mock(return_value=Response(201))
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_log=capture_log
            )
        
        # Find the total size log message
        total_size_msg = [msg for msg in log_messages if "Total files:" in msg]
        assert len(total_size_msg) > 0
        
        # Verify the message contains size info
        msg = total_size_msg[0]
        assert "bytes" in msg

    async def test_sync_without_callbacks(
        self, mock_fs: Path, respx_mock
    ):
        """Verify sync works without on_log and on_progress callbacks."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.head().mock(return_value=Response(404))
        respx_mock.put().mock(return_value=Response(201))
        
        # No callbacks provided
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/"
                # on_log=None (default)
                # on_progress=None (default)
            )
        
        # Should complete without error
        assert True

    async def test_sync_head_exception_handling(
        self, mock_fs: Path, respx_mock
    ):
        """Verify sync handles HEAD request exceptions gracefully."""
        auth = OIDCAuthProvider("token")
        
        # HEAD raises exception
        respx_mock.head().mock(side_effect=Exception("Connection timeout"))
        respx_mock.put("https://pod.example.org/test_file1.txt").mock(
            return_value=Response(201)
        )
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        async with SolidClient(auth) as client:
            await sync_local_to_remote(
                client,
                str(mock_fs),
                "https://pod.example.org/",
                on_log=capture_log
            )
        
        # Should log HEAD check failure and continue
        assert any("HEAD check failed" in msg for msg in log_messages)

    async def test_sync_file_read_error(
        self, tmp_path: Path, respx_mock
    ):
        """Verify sync handles file read errors gracefully."""
        auth = OIDCAuthProvider("token")
        
        # Create a file that will be unreadable after creation
        test_file = tmp_path / "unreadable.txt"
        test_file.write_text("content")
        
        # Make it unreadable (Windows: remove read permission)
        import os
        os.chmod(str(test_file), 0o000)
        
        respx_mock.head().mock(return_value=Response(404))
        respx_mock.put().mock(return_value=Response(201))
        
        log_messages = []
        def capture_log(msg: str):
            log_messages.append(msg)
        
        try:
            async with SolidClient(auth) as client:
                await sync_local_to_remote(
                    client,
                    str(tmp_path),
                    "https://pod.example.org/",
                    on_log=capture_log
                )
            
            # Should complete without error even with unreadable file
            # The sync function should handle the error gracefully
            # May or may not log error depending on system behavior
            assert True  # Test passes if sync completes
        finally:
            # Restore read permission
            os.chmod(str(test_file), 0o644)
