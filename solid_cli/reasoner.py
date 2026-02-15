"""Semantic Reasoner for RDF graphs using N3 logic and forward chaining."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS


class SemanticReasoner:
    """Semantic reasoner for RDF data using forward chaining and N3 logic."""
    
    # Define namespaces
    PROV = Namespace("http://www.w3.org/ns/prov#")
    EX = Namespace("http://example.org/")
    LOG = Namespace("http://www.w3.org/2000/10/swap/log#")
    RDF = RDF
    RDFS = RDFS
    
    def __init__(self):
        """Initialize semantic reasoner."""
        self.graph = Graph()
        self.inferred_graph = Graph()
    
    def extract_provenance(self, file_path: Path) -> str:
        """Extract and generate provenance metadata for a file.
        
        Uses W3C PROV ontology to record:
        - Generation timestamp
        - Attribution to processing agent
        
        Args:
            file_path: Path to the file
        
        Returns:
            Turtle format provenance string
        """
        # Create a simple graph with provenance
        g = Graph()
        g.bind("prov", self.PROV)
        g.bind("ex", self.EX)
        
        # Use file path as subject
        subject = self.EX[f"file-{file_path.name}"]
        
        # Add provenance metadata
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        g.add((subject, self.PROV.generatedAtTime, Literal(now)))
        g.add((subject, self.PROV.wasAttributedTo, self.EX["me"]))
        
        # Return as Turtle
        return g.serialize(format="turtle")
    
    def apply_rules(self, graph: Graph) -> Graph:
        """Apply forward-chaining inference rules to RDF graph.
        
        Implements a simple forward-chaining rule engine with one key rule:
        
        **Confidentiality Propagation Rule:**
        If a folder has securityLevel "TopSecret" and a file belongs to that folder,
        then the file inherits the securityLevel "TopSecret".
        
        This demonstrates semantic reasoning by inferring implicit knowledge
        from explicit facts about hierarchical relationships.
        
        Args:
            graph: Input RDF graph
        
        Returns:
            Extended graph with inferred triples
        """
        # Create output graph
        inferred = Graph()
        
        # Copy all original triples
        for s, p, o in graph:
            inferred.add((s, p, o))
        
        # Forward chaining loop - apply rules until fixed point
        max_iterations = 10
        iteration = 0
        changed = True
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            triples_before = len(list(inferred.triples((None, None, None))))
            
            # Rule 1: Confidentiality Propagation
            # If Folder has ex:securityLevel "TopSecret"
            # AND File has rdf:type Folder
            # THEN File has ex:securityLevel "TopSecret"
            
            # Query for folders with TopSecret level
            for folder in inferred.subjects(self.EX.securityLevel, Literal("TopSecret")):
                # Query for files that are instances of this folder or contained by it
                for file_obj in inferred.subjects(RDF.type, folder):
                    # If file doesn't already have this property, add it
                    security_triples = list(
                        inferred.triples((file_obj, self.EX.securityLevel, None))
                    )
                    
                    if not security_triples:
                        inferred.add((file_obj, self.EX.securityLevel, Literal("TopSecret")))
                        changed = True
            
            # Rule 2: Transitivity of containment
            # If A contains B and B contains C, then A contains C
            for a, _, b in inferred.triples((None, self.EX.contains, None)):
                for _, _, c in inferred.triples((b, self.EX.contains, None)):
                    if not (a, self.EX.contains, c) in inferred:
                        inferred.add((a, self.EX.contains, c))
                        changed = True
            
            triples_after = len(list(inferred.triples((None, None, None))))
            if triples_after > triples_before:
                changed = True
        
        return inferred
    
    def query_inferences(self, graph: Graph, pattern: Optional[tuple] = None) -> list:
        """Query inferred triples from a graph.
        
        Args:
            graph: RDF graph to query
            pattern: Tuple of (subject, predicate, object) to match. Use None for wildcards.
        
        Returns:
            List of matching triples
        """
        if pattern is None:
            pattern = (None, None, None)
        
        return list(graph.triples(pattern))
    
    def serialize_graph(self, graph: Graph, format: str = "turtle") -> str:
        """Serialize a graph to string.
        
        Args:
            graph: RDF graph to serialize
            format: Serialization format (turtle, xml, json-ld, etc.)
        
        Returns:
            Serialized graph string
        """
        return graph.serialize(format=format)
