"""Access Control List (ACL) management for Solid Pods."""

from rdflib import Graph, Namespace, URIRef, Literal
from typing import Optional
from .client import SolidClient


async def update_acl(
    client: SolidClient,
    resource_url: str,
    agent_webid: str,
    mode: str = "Read",
) -> None:
    """Update ACL for a Solid Pod resource.
    
    Fetches the .acl file (Turtle format), parses it with rdflib,
    adds Agent and Mode triples, and PUTs the modified ACL back.
    
    Args:
        client: SolidClient instance
        resource_url: URL of the resource to manage ACL for
        agent_webid: WebID of the agent to grant access to
        mode: ACL mode ('Read', 'Write', 'Append', 'Control')
    """
    acl_url = resource_url.rstrip("/") + ".acl"
    
    # Fetch existing ACL
    try:
        response = await client.get(acl_url)
        if response.status_code == 200:
            acl_content = response.text
        else:
            acl_content = ""
    except Exception:
        acl_content = ""
    
    # Parse with rdflib
    graph = Graph()
    if acl_content:
        try:
            graph.parse(data=acl_content, format="turtle")
        except Exception:
            graph = Graph()
    
    # Define namespaces
    ACL = Namespace("http://www.w3.org/ns/auth/acl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    
    # Create authorization resource
    auth_uri = URIRef(acl_url + "#default")
    
    # Add triples
    graph.add((auth_uri, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), ACL.Authorization))
    graph.add((auth_uri, ACL.agent, URIRef(agent_webid)))
    graph.add((auth_uri, ACL.mode, ACL[mode]))
    graph.add((auth_uri, ACL.accessTo, URIRef(resource_url)))
    
    # Serialize back to Turtle
    acl_data = graph.serialize(format="turtle")
    
    # PUT back to server
    response = await client.put(
        acl_url,
        content=acl_data.encode("utf-8"),
        description=f"Updating ACL for {resource_url}",
    )
    
    if response.status_code not in (200, 201):
        raise RuntimeError(f"Failed to update ACL: Status {response.status_code}")
