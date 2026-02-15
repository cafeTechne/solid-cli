"""Solid Pod HTTP client with authentication support."""

import httpx
from typing import Callable, Optional, Dict, Any
from .auth import AuthProvider


class SolidClient:
    """Async HTTP client for Solid Pod operations with auth injection."""

    def __init__(
        self,
        auth_provider: AuthProvider,
        timeout: float = 30.0,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
    ):
        """Initialize Solid client.
        
        Args:
            auth_provider: Authentication provider for headers
            timeout: Request timeout in seconds
            on_progress: Callback for progress updates (bytes_sent, total_bytes, description)
        """
        self.auth_provider = auth_provider
        self.timeout = timeout
        self.on_progress = on_progress
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers from auth provider."""
        return self.auth_provider.get_headers()

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Perform GET request with auth headers."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async with context manager.")
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        return await self._client.get(url, headers=headers, **kwargs)

    async def head(self, url: str, **kwargs) -> httpx.Response:
        """Perform HEAD request with auth headers."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async with context manager.")
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        return await self._client.head(url, headers=headers, **kwargs)

    async def put(
        self, url: str, content: bytes, description: str = "Uploading", **kwargs
    ) -> httpx.Response:
        """Perform PUT request with auth headers and progress tracking.
        
        Args:
            url: Target URL
            content: File content to upload
            description: Progress description
            **kwargs: Additional request kwargs
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async with context manager.")
        
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        
        if self.on_progress:
            self.on_progress(0, len(content), description)
        
        response = await self._client.put(url, content=content, headers=headers, **kwargs)
        
        if self.on_progress:
            self.on_progress(len(content), len(content), description)
        
        return response

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Perform DELETE request with auth headers."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async with context manager.")
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}
        return await self._client.delete(url, headers=headers, **kwargs)
