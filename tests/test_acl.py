"""Tests for ACL management."""

import pytest
import respx
from httpx import Response
from rdflib import Graph, Namespace, URIRef
from solid_cli.client import SolidClient
from solid_cli.acl import update_acl
from solid_cli.auth import OIDCAuthProvider


@pytest.mark.asyncio
class TestUpdateACL:
    """Test ACL update functionality."""

    async def test_update_acl_creates_new_acl(
        self, respx_mock, sample_acl_turtle: str
    ):
        """Verify update_acl creates ACL when none exists."""
        auth = OIDCAuthProvider("token")
        
        # Mock GET returning 404 (no ACL exists)
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(404)
        )
        
        # Mock PUT for creating ACL
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                mode="Read"
            )
        
        # Verify PUT was called
        assert put_route.called
        
        # Verify the request contains Turtle data
        request = put_route.calls.last.request
        content = request.content.decode("utf-8")
        
        # Should contain ACL triples
        assert "Authorization" in content or "@prefix" in content

    async def test_update_acl_modifies_existing(
        self, respx_mock, sample_acl_turtle: str
    ):
        """Verify update_acl modifies existing ACL file."""
        auth = OIDCAuthProvider("token")
        
        # Mock GET returning existing ACL
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(200, text=sample_acl_turtle)
        )
        
        # Mock PUT for updating
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(200)
        )
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                "https://new_agent.example.org/profile#me",
                mode="Write"
            )
        
        # Verify PUT was called
        assert put_route.called
        
        # Get the updated content
        request = put_route.calls.last.request
        content = request.content.decode("utf-8")
        
        # Should contain new agent
        assert "new_agent.example.org" in content

    async def test_update_acl_different_modes(
        self, respx_mock
    ):
        """Verify update_acl supports different ACL modes."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.get().mock(return_value=Response(404))
        
        modes = ["Read", "Write", "Append", "Control"]
        
        for mode in modes:
            # Reset mock
            respx_mock.reset()
            respx_mock.get().mock(return_value=Response(404))
            
            put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
                return_value=Response(201)
            )
            
            async with SolidClient(auth) as client:
                await update_acl(
                    client,
                    "https://pod.example.org/resource.ttl",
                    "https://agent.example.org/profile#me",
                    mode=mode
                )
            
            # Verify PUT was called
            assert put_route.called
            
            # Verify mode is in content
            request = put_route.calls.last.request
            content = request.content.decode("utf-8")
            assert mode in content

    async def test_update_acl_contains_agent_triple(
        self, respx_mock
    ):
        """Verify updated ACL contains agent triple."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(404)
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        agent_webid = "https://alice.example.org/profile#me"
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                agent_webid,
                mode="Read"
            )
        
        # Get the content
        request = put_route.calls.last.request
        content = request.content.decode("utf-8")
        
        # Parse as RDF to verify triples
        graph = Graph()
        graph.parse(data=content, format="turtle")
        
        # Should contain the agent
        ACL = Namespace("http://www.w3.org/ns/auth/acl#")
        agent_found = False
        for s, p, o in graph:
            if p == ACL.agent and str(o) == agent_webid:
                agent_found = True
                break
        
        assert agent_found, "Agent triple not found in ACL"

    async def test_update_acl_contains_mode_triple(
        self, respx_mock
    ):
        """Verify updated ACL contains mode triple."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(404)
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                mode="Write"
            )
        
        # Get the content
        request = put_route.calls.last.request
        content = request.content.decode("utf-8")
        
        # Parse as RDF
        graph = Graph()
        graph.parse(data=content, format="turtle")
        
        # Should contain Write mode
        ACL = Namespace("http://www.w3.org/ns/auth/acl#")
        mode_found = False
        for s, p, o in graph:
            if p == ACL.mode and "Write" in str(o):
                mode_found = True
                break
        
        assert mode_found, "Mode triple not found in ACL"

    async def test_update_acl_contains_accessto_triple(
        self, respx_mock
    ):
        """Verify updated ACL contains accessTo triple."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(404)
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        resource_url = "https://pod.example.org/resource.ttl"
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                resource_url,
                "https://agent.example.org/profile#me",
                mode="Read"
            )
        
        # Get the content
        request = put_route.calls.last.request
        content = request.content.decode("utf-8")
        
        # Parse as RDF
        graph = Graph()
        graph.parse(data=content, format="turtle")
        
        # Should contain accessTo pointing to resource
        ACL = Namespace("http://www.w3.org/ns/auth/acl#")
        accessto_found = False
        for s, p, o in graph:
            if p == ACL.accessTo and str(o) == resource_url:
                accessto_found = True
                break
        
        assert accessto_found, "accessTo triple not found in ACL"

    async def test_update_acl_handles_malformed_response(
        self, respx_mock
    ):
        """Verify update_acl handles malformed ACL gracefully."""
        auth = OIDCAuthProvider("token")
        
        # Return malformed Turtle
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(200, text="not valid turtle @@@ !@#$")
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(200)
        )
        
        async with SolidClient(auth) as client:
            # Should not raise, but create new graph
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                mode="Read"
            )
        
        # Should still try to PUT
        assert put_route.called

    async def test_update_acl_put_failure_raises_error(
        self, respx_mock
    ):
        """Verify update_acl raises error if PUT fails."""
        auth = OIDCAuthProvider("token")
        
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(404)
        )
        
        # PUT returns error
        respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(403)  # Forbidden
        )
        
        async with SolidClient(auth) as client:
            with pytest.raises(RuntimeError, match="Failed to update ACL"):
                await update_acl(
                    client,
                    "https://pod.example.org/resource.ttl",
                    "https://agent.example.org/profile#me",
                    mode="Read"
                )

    async def test_update_acl_with_trailing_slash(
        self, respx_mock
    ):
        """Verify update_acl handles URLs with trailing slash."""
        auth = OIDCAuthProvider("token")
        
        # Should normalize to resource.ttl.acl
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(404)
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl/",  # Trailing slash
                "https://agent.example.org/profile#me",
                mode="Read"
            )
        
        # Should still work
        assert put_route.called

    async def test_update_acl_get_error_not_found(
        self, respx_mock
    ):
        """Verify update_acl handles GET 404 by creating new ACL."""
        auth = OIDCAuthProvider("token")
        
        # GET returns 404 (not 200)
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(404)
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                mode="Read"
            )
        
        # Should create new ACL
        assert put_route.called

    async def test_update_acl_get_exception(
        self, respx_mock
    ):
        """Verify update_acl handles GET exceptions by creating new ACL."""
        auth = OIDCAuthProvider("token")
        
        # GET raises exception
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            side_effect=Exception("Connection error")
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                mode="Read"
            )
        
        # Should still create ACL
        assert put_route.called

    async def test_update_acl_empty_response(
        self, respx_mock
    ):
        """Verify update_acl handles empty GET response."""
        auth = OIDCAuthProvider("token")
        
        # GET returns 200 but with empty content
        respx_mock.get("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(200, text="")
        )
        
        put_route = respx_mock.put("https://pod.example.org/resource.ttl.acl").mock(
            return_value=Response(201)
        )
        
        async with SolidClient(auth) as client:
            await update_acl(
                client,
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                mode="Read"
            )
        
        # Should create new graph
        assert put_route.called
        
        # Verify content was created
        request = put_route.calls.last.request
        content = request.content.decode("utf-8")
        assert "Authorization" in content or "@prefix" in content
