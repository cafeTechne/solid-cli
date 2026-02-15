"""Tests for natural language command parser."""

import pytest
from solid_cli.agent import parse_natural_language


class TestParseNaturalLanguage:
    """Test natural language parsing functionality."""
    
    def test_upload_command_basic(self):
        """Test parsing 'Upload file to remote' command."""
        result = parse_natural_language("Upload myfile.txt to https://pod.example.org/sync")
        assert result == ("sync", "myfile.txt", "https://pod.example.org/sync")
    
    def test_upload_command_lowercase(self):
        """Test parsing 'upload' command in lowercase."""
        result = parse_natural_language("upload document.pdf to https://solid.example.com")
        assert result == ("sync", "document.pdf", "https://solid.example.com")
    
    def test_upload_command_mixed_case(self):
        """Test parsing 'Upload' command with mixed case."""
        result = parse_natural_language("UPLOAD file.dat TO https://pod.test")
        assert result == ("sync", "file.dat", "https://pod.test")
    
    def test_sync_command_alias(self):
        """Test parsing 'Sync' as alias for upload."""
        result = parse_natural_language("sync config.ttl to https://pod.example.org")
        assert result == ("sync", "config.ttl", "https://pod.example.org")
    
    def test_share_command_basic(self):
        """Test parsing 'Share file with user' command."""
        result = parse_natural_language("share myfile.txt with https://alice.example.org/profile#me")
        assert result == ("share", "myfile.txt", "https://alice.example.org/profile#me")
    
    def test_share_command_lowercase(self):
        """Test parsing 'share' command in lowercase."""
        result = parse_natural_language("share document.pdf with bob@example.org")
        assert result == ("share", "document.pdf", "bob@example.org")
    
    def test_share_command_mixed_case(self):
        """Test parsing 'SHARE' command in uppercase."""
        result = parse_natural_language("SHARE data.json WITH user123")
        assert result == ("share", "data.json", "user123")
    
    def test_list_files_command_basic(self):
        """Test parsing 'List files in remote' command."""
        result = parse_natural_language("List files in https://pod.example.org")
        assert result == ("ls", "https://pod.example.org", "")
    
    def test_list_files_command_short_form(self):
        """Test parsing 'ls' command short form."""
        result = parse_natural_language("ls in https://pod.example.org")
        assert result == ("ls", "https://pod.example.org", "")
    
    def test_list_files_command_without_files_keyword(self):
        """Test parsing 'list in remote' without 'files' keyword."""
        result = parse_natural_language("list in https://pod.example.org/folder")
        assert result == ("ls", "https://pod.example.org/folder", "")
    
    def test_list_files_command_mixed_case(self):
        """Test parsing 'LIST' command in uppercase."""
        result = parse_natural_language("LIST FILES IN https://example.com/data")
        assert result == ("ls", "https://example.com/data", "")
    
    def test_invalid_command(self):
        """Test parsing invalid command returns error message."""
        result = parse_natural_language("delete all files")
        assert result == "I'm sorry, I didn't understand that command."
    
    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_natural_language("")
        assert result == "I'm sorry, I didn't understand that command."
    
    def test_whitespace_only(self):
        """Test parsing whitespace-only string."""
        result = parse_natural_language("   ")
        assert result == "I'm sorry, I didn't understand that command."
    
    def test_random_text(self):
        """Test parsing random unmatched text."""
        result = parse_natural_language("Hello world, this is a test")
        assert result == "I'm sorry, I didn't understand that command."
    
    def test_upload_with_path(self):
        """Test parsing upload with full file path."""
        result = parse_natural_language("upload /home/user/documents/file.pdf to https://pod.example.org")
        # Should capture the entire path up to the next space
        assert result[0] == "sync"
        assert result[2] == "https://pod.example.org"
    
    def test_share_with_webid(self):
        """Test parsing share with WebID URI."""
        result = parse_natural_language("share resources/data.ttl with https://alice.example.org/profile#me")
        assert result == ("share", "resources/data.ttl", "https://alice.example.org/profile#me")
    
    def test_upload_with_spaces_in_prompt(self):
        """Test upload command with extra spaces - regex handles them."""
        result = parse_natural_language("upload file.txt to https://pod.org")
        # Regex \s+ handles multiple spaces, so this should match
        assert result == ("sync", "file.txt", "https://pod.org")
    
    def test_malformed_upload_missing_to(self):
        """Test malformed upload command without 'to' keyword."""
        result = parse_natural_language("upload file.txt https://pod.example.org")
        assert result == "I'm sorry, I didn't understand that command."
    
    def test_malformed_share_missing_with(self):
        """Test malformed share command without 'with' keyword."""
        result = parse_natural_language("share file.txt alice")
        assert result == "I'm sorry, I didn't understand that command."
    
    def test_partial_command(self):
        """Test incomplete command."""
        result = parse_natural_language("upload file.txt to")
        assert result == "I'm sorry, I didn't understand that command."
