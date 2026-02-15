"""Test configuration and fixtures for solid-cli tests."""

import pytest
import respx
from pathlib import Path
from typing import Generator


@pytest.fixture
def mock_pod() -> Generator[respx.MockRouter, None, None]:
    """Mock Solid Pod using respx.
    
    Sets up a mocked HTTP backend for https://pod.example.org.
    Returns respx.MockRouter for easy route configuration.
    """
    with respx.mock:
        yield respx


@pytest.fixture
def mock_fs(tmp_path: Path) -> Path:
    """Create a dummy local directory structure for testing sync.
    
    Creates:
    - test_file1.txt (100 bytes)
    - test_file2.txt (200 bytes)
    - subdir/test_file3.txt (50 bytes)
    - subdir/resource.acl (simple ACL)
    
    Returns the tmp_path for use in tests.
    """
    # Create test files
    file1 = tmp_path / "test_file1.txt"
    file1.write_text("a" * 100)
    
    file2 = tmp_path / "test_file2.txt"
    file2.write_text("b" * 200)
    
    # Create subdirectory with files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    
    file3 = subdir / "test_file3.txt"
    file3.write_text("c" * 50)
    
    # Create ACL file
    acl_file = subdir / "resource.acl"
    acl_content = """@prefix acl: <http://www.w3.org/ns/auth/acl#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<#owner>
    a acl:Authorization ;
    acl:agent <http://example.com/profile#me> ;
    acl:mode acl:Control ;
    acl:accessTo <./resource.ttl> .
"""
    acl_file.write_text(acl_content)
    
    return tmp_path


@pytest.fixture
def sample_acl_turtle() -> str:
    """Return a sample ACL in Turtle format."""
    return """@prefix acl: <http://www.w3.org/ns/auth/acl#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<#default>
    a acl:Authorization ;
    acl:agent <http://example.com/profile#me> ;
    acl:mode acl:Read ;
    acl:accessTo <./resource.ttl> .
"""


@pytest.fixture
def sample_resource_turtle() -> str:
    """Return a sample RDF resource in Turtle format."""
    return """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<#this> a <http://example.com/Thing> ;
    rdfs:label "Sample Resource" .
"""
