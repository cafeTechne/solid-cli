"""Authentication providers for Solid Pod access."""

from abc import ABC, abstractmethod
from typing import Dict


class AuthProvider(ABC):
    """Abstract base class for authentication providers."""

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Return authorization headers for Solid Pod requests."""
        pass


class ProxyAuthProvider(AuthProvider):
    """Authentication provider for localhost proxy."""

    def __init__(self, url: str):
        """Initialize proxy auth provider.
        
        Args:
            url: Proxy server URL (typically localhost)
        """
        self.url = url

    def get_headers(self) -> Dict[str, str]:
        """Return headers for localhost proxy."""
        return {"X-Proxy-Authorization": self.url}


class OIDCAuthProvider(AuthProvider):
    """Authentication provider for OIDC (DPoP) tokens."""

    def __init__(self, token: str):
        """Initialize OIDC auth provider.
        
        Args:
            token: DPoP authentication token
        """
        self.token = token

    def get_headers(self) -> Dict[str, str]:
        """Return DPoP authorization header."""
        return {"Authorization": f"DPoP {self.token}"}
