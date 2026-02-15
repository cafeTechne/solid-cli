"""Tests for SolidClient HTTP operations."""

import pytest
import respx
from httpx import Response
from solid_cli.client import SolidClient
from solid_cli.auth import OIDCAuthProvider, ProxyAuthProvider


@pytest.mark.asyncio
class TestSolidClient:
    """Test SolidClient async HTTP wrapper."""

    async def test_client_initialization(self):
        """Verify SolidClient initializes correctly."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        assert client.auth_provider == auth
        assert client.timeout == 30.0
        assert client.on_progress is None

    async def test_client_with_custom_timeout(self):
        """Verify custom timeout is stored."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth, timeout=60.0)
        
        assert client.timeout == 60.0

    async def test_client_with_progress_callback(self):
        """Verify on_progress callback is stored."""
        auth = OIDCAuthProvider("token")
        callback = lambda b, t, d: None
        client = SolidClient(auth, on_progress=callback)
        
        assert client.on_progress == callback

    async def test_client_injects_auth_headers(self, respx_mock):
        """Verify client injects auth headers into requests."""
        auth = OIDCAuthProvider("test_token")
        client = SolidClient(auth)
        
        # Mock GET request - capture the request
        route = respx_mock.get("https://pod.example.org/resource.ttl").mock(
            return_value=Response(200, text="test")
        )
        
        async with client:
            response = await client.get("https://pod.example.org/resource.ttl")
        
        # Verify the request was made
        assert route.called
        
        # Verify auth header was injected
        request = route.calls.last.request
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "DPoP test_token"

    async def test_client_head_request(self, respx_mock):
        """Verify HEAD request works with auth headers."""
        auth = OIDCAuthProvider("token123")
        client = SolidClient(auth)
        
        route = respx_mock.head("https://pod.example.org/file.txt").mock(
            return_value=Response(200)
        )
        
        async with client:
            response = await client.head("https://pod.example.org/file.txt")
        
        assert response.status_code == 200
        request = route.calls.last.request
        assert request.headers["Authorization"] == "DPoP token123"

    async def test_client_put_request_with_progress(self, respx_mock):
        """Verify PUT request calls on_progress callback."""
        auth = OIDCAuthProvider("token")
        
        progress_calls = []
        def track_progress(bytes_sent: int, total_bytes: int, description: str):
            progress_calls.append((bytes_sent, total_bytes, description))
        
        client = SolidClient(auth, on_progress=track_progress)
        
        route = respx_mock.put("https://pod.example.org/file.txt").mock(
            return_value=Response(201)
        )
        
        async with client:
            response = await client.put(
                "https://pod.example.org/file.txt",
                content=b"test content",
                description="Uploading file"
            )
        
        assert response.status_code == 201
        
        # Verify progress was called
        assert len(progress_calls) == 2
        
        # First call: start of upload
        bytes_sent, total_bytes, desc = progress_calls[0]
        assert bytes_sent == 0
        assert total_bytes == 12  # len("test content")
        assert desc == "Uploading file"
        
        # Second call: end of upload
        bytes_sent, total_bytes, desc = progress_calls[1]
        assert bytes_sent == 12
        assert total_bytes == 12

    async def test_client_delete_request(self, respx_mock):
        """Verify DELETE request works with auth headers."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        route = respx_mock.delete("https://pod.example.org/file.txt").mock(
            return_value=Response(204)
        )
        
        async with client:
            response = await client.delete("https://pod.example.org/file.txt")
        
        assert response.status_code == 204

    async def test_client_context_manager(self, respx_mock):
        """Verify client works as async context manager."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.get("https://pod.example.org/test").mock(
            return_value=Response(200)
        )
        
        # Should work fine with context manager
        async with SolidClient(auth) as client:
            response = await client.get("https://pod.example.org/test")
            assert response.status_code == 200

    async def test_client_raises_without_context_manager(self):
        """Verify client raises error if used without context manager."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        # Trying to use get without context manager should raise
        with pytest.raises(RuntimeError, match="not initialized"):
            await client.get("https://pod.example.org/test")

    async def test_client_merges_headers(self, respx_mock):
        """Verify client merges auth headers with custom headers."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        route = respx_mock.get("https://pod.example.org/test").mock(
            return_value=Response(200)
        )
        
        async with client:
            await client.get(
                "https://pod.example.org/test",
                headers={"Custom-Header": "value"}
            )
        
        request = route.calls.last.request
        assert request.headers["Authorization"] == "DPoP token"
        assert request.headers["Custom-Header"] == "value"

    async def test_client_put_without_progress_callback(self, respx_mock):
        """Verify PUT works without on_progress callback."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)  # No on_progress
        
        respx_mock.put("https://pod.example.org/file").mock(
            return_value=Response(201)
        )
        
        async with client:
            response = await client.put(
                "https://pod.example.org/file",
                content=b"data"
            )
        
        assert response.status_code == 201

    @respx.mock
    async def test_client_get_without_context_manager_error(self):
        """Verify GET raises without context manager."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        with pytest.raises(RuntimeError):
            await client.get("https://pod.example.org/test")

    @respx.mock
    async def test_client_head_without_context_manager_error(self):
        """Verify HEAD raises without context manager."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        with pytest.raises(RuntimeError):
            await client.head("https://pod.example.org/test")

    @respx.mock
    async def test_client_put_without_context_manager_error(self):
        """Verify PUT raises without context manager."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        with pytest.raises(RuntimeError):
            await client.put("https://pod.example.org/test", content=b"data")

    @respx.mock
    async def test_client_delete_without_context_manager_error(self):
        """Verify DELETE raises without context manager."""
        auth = OIDCAuthProvider("token")
        client = SolidClient(auth)
        
        with pytest.raises(RuntimeError):
            await client.delete("https://pod.example.org/test")
