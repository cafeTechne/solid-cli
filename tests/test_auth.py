"""Tests for authentication providers."""

import pytest
from solid_cli.auth import AuthProvider, ProxyAuthProvider, OIDCAuthProvider


class TestAuthProvider:
    """Test AuthProvider abstract base class."""

    def test_auth_provider_is_abstract(self):
        """Verify AuthProvider cannot be instantiated."""
        with pytest.raises(TypeError):
            AuthProvider()


class TestProxyAuthProvider:
    """Test ProxyAuthProvider implementation."""

    def test_get_headers_returns_dict(self):
        """Verify get_headers returns a dictionary."""
        provider = ProxyAuthProvider("http://localhost:8089")
        headers = provider.get_headers()
        
        assert isinstance(headers, dict)
        assert "X-Proxy-Authorization" in headers
        assert headers["X-Proxy-Authorization"] == "http://localhost:8089"

    def test_proxy_auth_with_different_urls(self):
        """Verify ProxyAuthProvider works with different URLs."""
        urls = [
            "http://localhost:8089",
            "http://127.0.0.1:3000",
            "https://proxy.example.com",
        ]
        
        for url in urls:
            provider = ProxyAuthProvider(url)
            headers = provider.get_headers()
            assert headers["X-Proxy-Authorization"] == url

    def test_proxy_auth_initialization(self):
        """Verify ProxyAuthProvider stores URL correctly."""
        url = "http://localhost:8089"
        provider = ProxyAuthProvider(url)
        
        assert provider.url == url


class TestOIDCAuthProvider:
    """Test OIDCAuthProvider implementation."""

    def test_get_headers_returns_dpop_header(self):
        """Verify get_headers returns DPoP authorization header."""
        token = "test_token_123"
        provider = OIDCAuthProvider(token)
        headers = provider.get_headers()
        
        assert isinstance(headers, dict)
        assert "Authorization" in headers
        assert headers["Authorization"] == "DPoP test_token_123"

    def test_oidc_auth_with_different_tokens(self):
        """Verify OIDCAuthProvider works with different tokens."""
        tokens = [
            "abc123",
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",
            "very_long_token_" + "x" * 100,
        ]
        
        for token in tokens:
            provider = OIDCAuthProvider(token)
            headers = provider.get_headers()
            assert headers["Authorization"] == f"DPoP {token}"

    def test_oidc_auth_initialization(self):
        """Verify OIDCAuthProvider stores token correctly."""
        token = "secret_token"
        provider = OIDCAuthProvider(token)
        
        assert provider.token == token

    def test_oidc_header_format(self):
        """Verify DPoP header format is correct."""
        token = "my_token"
        provider = OIDCAuthProvider(token)
        headers = provider.get_headers()
        
        # Should follow pattern: "DPoP <token>"
        auth_header = headers["Authorization"]
        assert auth_header.startswith("DPoP ")
        assert auth_header.endswith(token)


class TestAuthProviderIntegration:
    """Test auth providers work as expected in context."""

    def test_both_providers_implement_get_headers(self):
        """Verify both providers implement get_headers method."""
        proxy = ProxyAuthProvider("http://localhost:8089")
        oidc = OIDCAuthProvider("token")
        
        # Both should have get_headers method
        assert hasattr(proxy, "get_headers")
        assert hasattr(oidc, "get_headers")
        
        # Both should be callable
        assert callable(proxy.get_headers)
        assert callable(oidc.get_headers)

    def test_providers_return_dict(self):
        """Verify both providers return dict from get_headers."""
        proxy = ProxyAuthProvider("http://localhost:8089")
        oidc = OIDCAuthProvider("token")
        
        assert isinstance(proxy.get_headers(), dict)
        assert isinstance(oidc.get_headers(), dict)
