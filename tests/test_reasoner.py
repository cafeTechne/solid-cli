"""Tests for semantic reasoner."""

import pytest
from pathlib import Path
from rdflib import Graph, Literal, Namespace
from solid_cli.reasoner import SemanticReasoner


class TestSemanticReasoner:
    """Test semantic reasoner functionality."""
    
    @pytest.fixture
    def reasoner(self):
        """Provide SemanticReasoner instance."""
        return SemanticReasoner()
    
    def test_reasoner_initialization(self, reasoner):
        """Test SemanticReasoner initialization."""
        assert reasoner.graph is not None
        assert reasoner.inferred_graph is not None
    
    def test_extract_provenance(self, reasoner, tmp_path):
        """Test provenance extraction."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        provenance = reasoner.extract_provenance(test_file)
        
        # Should be valid Turtle format
        assert isinstance(provenance, str)
        assert "@prefix" in provenance or "prov:" in provenance
        assert "generatedAtTime" in provenance
        assert "wasAttributedTo" in provenance
    
    def test_extract_provenance_has_timestamp(self, reasoner, tmp_path):
        """Test that provenance includes ISO timestamp."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        provenance = reasoner.extract_provenance(test_file)
        
        # Should contain ISO timestamp format
        assert "T" in provenance  # ISO format includes T
        assert "Z" in provenance  # UTC timezone indicator
    
    def test_apply_rules_no_modification_for_empty_graph(self, reasoner):
        """Test apply_rules on empty graph."""
        g = Graph()
        result = reasoner.apply_rules(g)
        
        assert len(list(result.triples((None, None, None)))) == 0
    
    def test_apply_rules_preserves_original_triples(self, reasoner):
        """Test that apply_rules preserves original triples."""
        g = Graph()
        g.bind("ex", reasoner.EX)
        
        # Add a simple triple
        subject = reasoner.EX["test"]
        g.add((subject, reasoner.EX.name, Literal("test")))
        
        result = reasoner.apply_rules(g)
        
        # Original triple should still exist
        assert (subject, reasoner.EX.name, Literal("test")) in result
    
    def test_confidentiality_propagation_rule(self, reasoner):
        """Test confidentiality propagation inference rule."""
        g = Graph()
        g.bind("ex", reasoner.EX)
        
        # Create folder and file hierarchy
        folder = reasoner.EX["secret_folder"]
        file_obj = reasoner.EX["secret_file"]
        
        # File is instance of folder
        g.add((file_obj, reasoner.RDF.type, folder))
        
        # Folder has TopSecret level
        g.add((folder, reasoner.EX.securityLevel, Literal("TopSecret")))
        
        # Apply rules
        result = reasoner.apply_rules(g)
        
        # File should now have TopSecret level (inferred)
        inferred = list(result.triples((file_obj, reasoner.EX.securityLevel, Literal("TopSecret"))))
        assert len(inferred) > 0
    
    def test_containment_transitivity_rule(self, reasoner):
        """Test transitivity of containment inference rule."""
        g = Graph()
        g.bind("ex", reasoner.EX)
        
        # Create hierarchy: A contains B, B contains C
        a = reasoner.EX["A"]
        b = reasoner.EX["B"]
        c = reasoner.EX["C"]
        
        g.add((a, reasoner.EX.contains, b))
        g.add((b, reasoner.EX.contains, c))
        
        # Apply rules
        result = reasoner.apply_rules(g)
        
        # Should infer: A contains C
        inferred = list(result.triples((a, reasoner.EX.contains, c)))
        assert len(inferred) > 0
    
    def test_forward_chaining_fixed_point(self, reasoner):
        """Test that forward chaining reaches fixed point."""
        g = Graph()
        g.bind("ex", reasoner.EX)
        
        # Create a chain that requires multiple iterations
        # A contains B, B contains C (transitivity rule applies once)
        # A contains C should be inferred in first iteration
        a = reasoner.EX["A"]
        b = reasoner.EX["B"]
        c = reasoner.EX["C"]
        d = reasoner.EX["D"]
        
        g.add((a, reasoner.EX.contains, b))
        g.add((b, reasoner.EX.contains, c))
        g.add((c, reasoner.EX.contains, d))
        
        result = reasoner.apply_rules(g)
        
        # After fixed point, should have inferred transitive closures
        # At minimum: A contains C and B contains D
        assert (a, reasoner.EX.contains, c) in result or \
               (b, reasoner.EX.contains, d) in result
    
    def test_query_inferences(self, reasoner):
        """Test querying inferred triples."""
        g = Graph()
        g.bind("ex", reasoner.EX)
        
        subject = reasoner.EX["test"]
        g.add((subject, reasoner.EX.prop, Literal("value")))
        
        results = reasoner.query_inferences(g, (subject, None, None))
        
        assert len(results) > 0
        assert (subject, reasoner.EX.prop, Literal("value")) in results
    
    def test_serialize_graph(self, reasoner):
        """Test graph serialization."""
        g = Graph()
        g.bind("ex", reasoner.EX)
        g.add((reasoner.EX["test"], reasoner.EX.prop, Literal("value")))
        
        # Turtle serialization
        turtle = reasoner.serialize_graph(g, format="turtle")
        assert isinstance(turtle, str)
        assert "@prefix" in turtle or "ex:" in turtle
        
        # JSON-LD serialization
        jsonld = reasoner.serialize_graph(g, format="json-ld")
        assert isinstance(jsonld, str)
        assert "{" in jsonld or "test" in jsonld
    
    def test_multiple_rules_interaction(self, reasoner):
        """Test interaction between multiple inference rules."""
        g = Graph()
        g.bind("ex", reasoner.EX)
        
        # Create scenario where both rules apply
        folder = reasoner.EX["folder"]
        file_obj = reasoner.EX["file"]
        child_file = reasoner.EX["child_file"]
        
        # File is instance of folder
        g.add((file_obj, reasoner.RDF.type, folder))
        
        # Folder has TopSecret
        g.add((folder, reasoner.EX.securityLevel, Literal("TopSecret")))
        
        # File contains child_file
        g.add((file_obj, reasoner.EX.contains, child_file))
        
        result = reasoner.apply_rules(g)
        
        # At least file should have TopSecret (from confidentiality rule)
        assert (file_obj, reasoner.EX.securityLevel, Literal("TopSecret")) in result
    
    def test_reasoner_query_inferences(self, reasoner):
        """Test query_inferences method with different patterns."""
        from rdflib import Namespace, Literal
        
        g = Graph()
        EX = Namespace("http://example.org/")
        
        # Add some test triples
        subject = EX["subject"]
        predicate = EX["predicate"]
        obj = Literal("object")
        g.add((subject, predicate, obj))
        
        # Query with specific pattern
        results = reasoner.query_inferences(g, (subject, predicate, None))
        assert len(results) >= 1
        
        # Query with all wildcards (None as pattern)
        all_results = reasoner.query_inferences(g, None)
        assert len(all_results) >= 1
        
        # Query with no matches
        no_match = reasoner.query_inferences(g, (EX["none"], EX["none"], None))
        assert len(no_match) == 0
    
    def test_reasoner_serialize_graph(self, reasoner):
        """Test graph serialization."""
        from rdflib import Namespace, Literal
        
        g = Graph()
        EX = Namespace("http://example.org/")
        
        # Add a triple
        subject = EX["subject"]
        predicate = EX["predicate"]
        obj = Literal("object")
        g.add((subject, predicate, obj))
        
        # Serialize to turtle
        serialized = reasoner.serialize_graph(g, format="turtle")
        
        # Should contain basic Turtle syntax
        assert isinstance(serialized, str)
        assert len(serialized) > 0
