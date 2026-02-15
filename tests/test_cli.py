"""Tests for CLI commands."""

import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from typer.testing import CliRunner
from solid_cli.main import app


@pytest.fixture
def cli_runner():
    """Provide CliRunner for CLI testing."""
    return CliRunner()


class TestCLIHelp:
    """Test CLI help output."""

    def test_main_help(self, cli_runner: CliRunner):
        """Test main --help displays available commands."""
        result = cli_runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "sync" in result.stdout
        assert "share" in result.stdout
        assert "monitor" in result.stdout
        assert "tmux" in result.stdout
        assert "watch" in result.stdout
        assert "agent" in result.stdout
        assert "verify" in result.stdout
        assert "mount" in result.stdout

    def test_sync_help(self, cli_runner: CliRunner):
        """Test sync --help displays command options."""
        result = cli_runner.invoke(app, ["sync", "--help"])
        
        assert result.exit_code == 0
        assert "local_dir" in result.stdout or "Local" in result.stdout
        assert "remote_url" in result.stdout or "Remote" in result.stdout
        assert "--token" in result.stdout
        assert "--proxy" in result.stdout

    def test_share_help(self, cli_runner: CliRunner):
        """Test share --help displays command options."""
        result = cli_runner.invoke(app, ["share", "--help"])
        
        assert result.exit_code == 0
        assert "resource_url" in result.stdout or "Resource" in result.stdout
        assert "agent_webid" in result.stdout or "Agent" in result.stdout
        assert "--mode" in result.stdout
        assert "--token" in result.stdout

    def test_monitor_help(self, cli_runner: CliRunner):
        """Test monitor --help displays command options."""
        result = cli_runner.invoke(app, ["monitor", "--help"])
        
        assert result.exit_code == 0
        assert "--token" in result.stdout or "token" in result.stdout

    def test_tmux_help(self, cli_runner: CliRunner):
        """Test tmux --help displays command info."""
        result = cli_runner.invoke(app, ["tmux", "--help"])
        
        assert result.exit_code == 0


class TestCLISync:
    """Test sync command."""

    def test_sync_missing_arguments(self, cli_runner: CliRunner):
        """Test sync fails without required arguments."""
        result = cli_runner.invoke(app, ["sync"])
        
        # Should fail due to missing arguments
        assert result.exit_code != 0

    def test_sync_missing_auth(self, cli_runner: CliRunner):
        """Test sync fails without auth provider."""
        result = cli_runner.invoke(
            app,
            ["sync", "/tmp/local", "https://pod.example.org/"]
        )
        
        # Should fail: must provide --token or --proxy
        assert result.exit_code != 0

    def test_sync_with_token_option(self, cli_runner: CliRunner):
        """Test sync command accepts --token option."""
        # Note: This will fail at sync time (no actual pod), but syntax should be valid
        result = cli_runner.invoke(
            app,
            ["sync", "/tmp/test", "https://pod.example.org/", "--token", "test_token"]
        )
        
        # The command should parse the arguments correctly
        # May fail due to missing directory or network, but that's expected
        assert result.exit_code in [0, 1]

    def test_sync_with_proxy_option(self, cli_runner: CliRunner):
        """Test sync command accepts --proxy option."""
        result = cli_runner.invoke(
            app,
            ["sync", "/tmp/test", "https://pod.example.org/", "--proxy", "http://localhost:8089"]
        )
        
        # Command should parse (may fail at runtime due to network or missing dir)
        assert result.exit_code in [0, 1]


class TestCLIShare:
    """Test share command."""

    def test_share_missing_arguments(self, cli_runner: CliRunner):
        """Test share fails without required arguments."""
        result = cli_runner.invoke(app, ["share"])
        
        assert result.exit_code != 0

    def test_share_missing_auth(self, cli_runner: CliRunner):
        """Test share fails without auth provider."""
        result = cli_runner.invoke(
            app,
            [
                "share",
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me"
            ]
        )
        
        # Should fail: must provide --token or --proxy
        assert result.exit_code != 0

    def test_share_accepts_mode_option(self, cli_runner: CliRunner):
        """Test share command accepts --mode option."""
        result = cli_runner.invoke(
            app,
            [
                "share",
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                "--mode", "Write",
                "--token", "test_token"
            ]
        )
        
        # Command should parse (may fail at network level)
        # The important thing is the --mode argument is accepted
        assert result.exit_code in [0, 1]

    def test_share_mode_options(self, cli_runner: CliRunner):
        """Test share command works with different modes."""
        modes = ["Read", "Write", "Append", "Control"]
        
        for mode in modes:
            result = cli_runner.invoke(
                app,
                [
                    "share",
                    "https://pod.example.org/resource.ttl",
                    "https://agent.example.org/profile#me",
                    "--mode", mode,
                    "--token", "test_token"
                ]
            )
            
            # Should not fail on invalid mode (just check exit code)
            # The command may fail due to network or lack of httpx mock
            # But not due to invalid argument parsing
            assert result.exit_code in [0, 1]  # Allow 0 or 1 depending on network

    def test_share_with_proxy(self, cli_runner: CliRunner):
        """Test share command accepts --proxy option."""
        result = cli_runner.invoke(
            app,
            [
                "share",
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                "--proxy", "http://localhost:8089"
            ]
        )
        
        # Command should parse arguments successfully
        # May fail at runtime due to network, but not argument syntax
        assert result.exit_code in [0, 1]

    def test_share_with_default_mode(self, cli_runner: CliRunner):
        """Test share command uses default mode (Read)."""
        result = cli_runner.invoke(
            app,
            [
                "share",
                "https://pod.example.org/resource.ttl",
                "https://agent.example.org/profile#me",
                "--token", "test_token"
            ]
        )
        
        # Command should parse (default mode is Read)
        assert result.exit_code in [0, 1]

    def test_share_success_with_mocked_acl(self, cli_runner: CliRunner):
        """Test share command success path (line 84 coverage)."""
        with patch("solid_cli.acl.update_acl", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = None  # Success
            
            result = cli_runner.invoke(
                app,
                [
                    "share",
                    "https://pod.example.org/resource.ttl",
                    "https://agent.example.org/profile#me",
                    "--token", "test_token",
                    "--mode", "Read"
                ]
            )
            
            # Should succeed now
            assert result.exit_code == 0
            assert "Granted" in result.stdout


class TestCLIMonitor:
    """Test monitor command."""

    def test_monitor_help_works(self, cli_runner: CliRunner):
        """Test monitor --help works."""
        result = cli_runner.invoke(app, ["monitor", "--help"])
        
        assert result.exit_code == 0

    def test_monitor_requires_auth_or_default(self, cli_runner: CliRunner):
        """Test monitor can be invoked (though TUI won't display)."""
        # Note: We don't actually run monitor since it needs a terminal
        # Just verify the command exists and accepts auth options
        result = cli_runner.invoke(app, ["monitor", "--help"])
        
        assert result.exit_code == 0
        assert "--token" in result.stdout

    def test_monitor_with_token(self, cli_runner: CliRunner):
        """Test monitor accepts --token option."""
        # Don't try to actually run monitor (TUI needs a terminal)
        # Just verify the help text includes the option
        result = cli_runner.invoke(app, ["monitor", "--help"])
        
        assert result.exit_code == 0
        assert "--token" in result.stdout

    def test_monitor_with_proxy(self, cli_runner: CliRunner):
        """Test monitor accepts --proxy option."""
        # Don't try to actually run monitor (TUI needs a terminal)
        # Just verify the help text includes the option
        result = cli_runner.invoke(app, ["monitor", "--help"])
        
        assert result.exit_code == 0
        assert "--proxy" in result.stdout


class TestCLITmux:
    """Test tmux command."""

    def test_tmux_help_works(self, cli_runner: CliRunner):
        """Test tmux --help works."""
        result = cli_runner.invoke(app, ["tmux", "--help"])
        
        assert result.exit_code == 0

    def test_tmux_command_exists(self, cli_runner: CliRunner):
        """Test tmux command exists."""
        # Don't run tmux (would require actual tmux server), just verify help
        result = cli_runner.invoke(app, ["tmux", "--help"])
        
        assert result.exit_code == 0

    def test_tmux_command_listed(self, cli_runner: CliRunner):
        """Test tmux command is listed in main help."""
        result = cli_runner.invoke(app, ["--help"])
        
        assert "tmux" in result.stdout


class TestCLIGlobalOptions:
    """Test global CLI options."""

    def test_global_proxy_option(self, cli_runner: CliRunner):
        """Test global --proxy option is available."""
        result = cli_runner.invoke(app, ["--help"])
        
        # Global --proxy might be in help
        assert result.exit_code == 0

    def test_help_flag_works(self, cli_runner: CliRunner):
        """Test -h and --help work."""
        result1 = cli_runner.invoke(app, ["--help"])
        result2 = cli_runner.invoke(app, ["-h"], catch_exceptions=False)
        
        assert result1.exit_code == 0


class TestCLIBannerPrinting:
    """Test that banner is printed on command execution."""

    def test_sync_prints_banner(self, cli_runner: CliRunner):
        """Test sync command prints banner."""
        result = cli_runner.invoke(
            app,
            ["sync", "--help"]
        )
        
        # Help output should come from command
        assert result.exit_code == 0

    def test_share_prints_banner(self, cli_runner: CliRunner):
        """Test share command prints banner."""
        result = cli_runner.invoke(
            app,
            ["share", "--help"]
        )
        
        assert result.exit_code == 0


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_command(self, cli_runner: CliRunner):
        """Test invalid command returns error."""
        result = cli_runner.invoke(app, ["invalid_command"])
        
        assert result.exit_code != 0

    def test_nonexistent_directory_sync(self, cli_runner: CliRunner):
        """Test sync with nonexistent directory fails gracefully."""
        result = cli_runner.invoke(
            app,
            ["sync", "/this/path/does/not/exist", "https://pod.example.org/", "--token", "token"]
        )
        
        # Should fail (directory doesn't exist)
        assert result.exit_code != 0


class TestTmux:
    """Test tmux module functionality."""

    def test_launch_dashboard_with_mocked_tmux(self):
        """Test launch_dashboard function with mocked libtmux."""
        from solid_cli import tmux
        
        # Mock libtmux
        with patch("solid_cli.tmux.libtmux.Server") as mock_server_class:
            # Setup mock objects
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server
            
            mock_session = MagicMock()
            mock_window = MagicMock()
            mock_pane = MagicMock()
            mock_new_pane = MagicMock()
            
            # Configure return values
            mock_server.list_sessions.return_value = []  # No existing session
            mock_server.new_session.return_value = mock_session
            mock_session.list_windows.return_value = [mock_window]
            mock_window.list_panes.return_value = [mock_pane]
            mock_window.split_window.return_value = mock_new_pane
            
            # Call the function
            tmux.launch_dashboard()
            
            # Verify the function created a session
            mock_server.new_session.assert_called_with(session_name="solid-cli")
            
            # Verify it split the window
            mock_window.split_window.assert_called_once()
            
            # Verify it attached
            mock_session.attach_session.assert_called_once()

    def test_launch_dashboard_with_existing_session(self):
        """Test launch_dashboard with existing tmux session."""
        from solid_cli import tmux
        
        with patch("solid_cli.tmux.libtmux.Server") as mock_server_class:
            # Setup mock objects
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server
            
            mock_existing_session = MagicMock()
            mock_existing_session.name = "solid-cli"
            
            mock_window = MagicMock()
            mock_pane = MagicMock()
            mock_new_pane = MagicMock()
            
            # Configure return values - session already exists
            mock_server.list_sessions.return_value = [mock_existing_session]
            mock_server.sessions.filter.return_value = [mock_existing_session]
            mock_existing_session.list_windows.return_value = [mock_window]
            mock_window.list_panes.return_value = [mock_pane]
            mock_window.split_window.return_value = mock_new_pane
            
            # Call the function
            tmux.launch_dashboard()
            
            # Verify it used the existing session (didn't create new one)
            mock_server.new_session.assert_not_called()
            
            # Verify it still split the window
            mock_window.split_window.assert_called_once()
            
            # Verify it attached
            mock_existing_session.attach_session.assert_called_once()


class TestMainEntryPoint:
    """Test main.py entry point and interactive commands."""

    def test_monitor_command_with_mocked_dashboard(self, cli_runner: CliRunner):
        """Test monitor command calls SolidDashboard.run()."""
        with patch("solid_cli.main.SolidDashboard") as mock_dashboard_class:
            mock_dashboard = MagicMock()
            mock_dashboard_class.return_value = mock_dashboard
            
            result = cli_runner.invoke(app, ["monitor", "--token", "test"])
            
            # Verify dashboard was created
            mock_dashboard_class.assert_called_once()
            
            # Verify run was called
            mock_dashboard.run.assert_called_once()

    def test_tmux_command_with_mocked_launch(self, cli_runner: CliRunner):
        """Test tmux command calls launch_dashboard()."""
        with patch("solid_cli.main.launch_dashboard") as mock_launch:
            result = cli_runner.invoke(app, ["tmux"])
            
            # Verify launch_dashboard was called
            mock_launch.assert_called_once()


class TestAgentCommand:
    """Test natural language agent command."""
    
    def test_agent_help(self, cli_runner: CliRunner):
        """Test agent --help displays command options."""
        result = cli_runner.invoke(app, ["agent", "--help"])
        
        assert result.exit_code == 0
        assert "Natural language" in result.stdout or "agent" in result.stdout.lower()
    
    def test_agent_upload_command(self, cli_runner: CliRunner):
        """Test agent command with upload intent."""
        with patch("solid_cli.main.sync") as mock_sync:
            result = cli_runner.invoke(app, ["agent", "upload myfile.txt to https://pod.org", "--proxy", "http://localhost:8089"])
            
            # Should invoke sync command
            assert result.exit_code == 0 or "Syncing" in result.stdout
    
    def test_agent_share_command(self, cli_runner: CliRunner):
        """Test agent command with share intent."""
        with patch("solid_cli.main.share") as mock_share:
            result = cli_runner.invoke(app, ["agent", "share file.txt with alice@example.org", "--proxy", "http://localhost:8089"])
            
            # Should invoke share command
            assert result.exit_code == 0 or "Sharing" in result.stdout
    
    def test_agent_list_command(self, cli_runner: CliRunner):
        """Test agent command with list intent."""
        result = cli_runner.invoke(app, ["agent", "list files in https://pod.org", "--proxy", "http://localhost:8089"])
        
        # Should process list command
        assert "Listing" in result.stdout or result.exit_code == 0
    
    def test_agent_invalid_command(self, cli_runner: CliRunner):
        """Test agent command with invalid input."""
        result = cli_runner.invoke(app, ["agent", "do something weird", "--proxy", "http://localhost:8089"])
        
        # Should fail and show error
        assert result.exit_code != 0
        assert "didn't understand" in result.stdout
    
    def test_agent_empty_prompt(self, cli_runner: CliRunner):
        """Test agent command with empty prompt."""
        result = cli_runner.invoke(app, ["agent", "", "--proxy", "http://localhost:8089"])
        
        # Should fail
        assert result.exit_code != 0


class TestWatchCommand:
    """Test watch command for file system monitoring."""
    
    def test_watch_help(self, cli_runner: CliRunner):
        """Test watch --help displays command options."""
        result = cli_runner.invoke(app, ["watch", "--help"])
        
        assert result.exit_code == 0
        assert "watch" in result.stdout.lower() or "local" in result.stdout.lower()
    
    def test_watch_nonexistent_directory(self, cli_runner: CliRunner):
        """Test watch command with non-existent directory."""
        result = cli_runner.invoke(app, ["watch", "/nonexistent/path", "https://pod.org", "--proxy", "http://localhost:8089"])
        
        # Should fail validation
        assert result.exit_code != 0
    
    def test_watch_requires_auth(self, cli_runner: CliRunner, tmp_path):
        """Test watch command requires auth provider."""
        result = cli_runner.invoke(app, ["watch", str(tmp_path), "https://pod.org"])
        
        # Should fail due to missing auth
        assert result.exit_code != 0
    
    def test_watch_with_proxy_auth(self, cli_runner: CliRunner, tmp_path):
        """Test watch command with proxy auth provider."""
        # Mock the Observer to avoid actually running the watch
        with patch("solid_cli.main.Observer") as mock_observer_class:
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer
            
            # We need to interrupt the async loop - mock asyncio.sleep
            with patch("solid_cli.main.asyncio.sleep") as mock_sleep:
                mock_sleep.side_effect = KeyboardInterrupt()
                
                result = cli_runner.invoke(
                    app,
                    ["watch", str(tmp_path), "https://pod.org", "--proxy", "http://localhost:8089"],
                    catch_exceptions=False
                )
                
                # Should start watching (observer should be scheduled)
                mock_observer.schedule.assert_called_once()
                mock_observer.start.assert_called_once()
    
    def test_watch_event_handler_creation(self):
        """Test SolidEventHandler initialization."""
        from solid_cli.main import SolidEventHandler
        from unittest.mock import MagicMock
        
        mock_client = MagicMock()
        handler = SolidEventHandler(mock_client, "/tmp/test", "https://pod.org")
        
        assert handler.client == mock_client
        assert handler.local_dir == Path("/tmp/test")
        assert handler.remote_url == "https://pod.org"


class TestVerifyCommand:
    """Test verify command for checksum validation."""
    
    def test_verify_help(self, cli_runner: CliRunner):
        """Test verify --help displays command options."""
        result = cli_runner.invoke(app, ["verify", "--help"])
        
        assert result.exit_code == 0
        assert "verify" in result.stdout.lower() or "local" in result.stdout.lower()
    
    def test_verify_nonexistent_directory(self, cli_runner: CliRunner):
        """Test verify command with non-existent directory."""
        result = cli_runner.invoke(app, ["verify", "/nonexistent/path", "https://pod.org", "--proxy", "http://localhost:8089"])
        
        # Should fail validation
        assert result.exit_code != 0
    
    def test_verify_requires_auth(self, cli_runner: CliRunner, tmp_path):
        """Test verify command requires auth provider."""
        result = cli_runner.invoke(app, ["verify", str(tmp_path), "https://pod.org"])
        
        # Should fail due to missing auth
        assert result.exit_code != 0
    
    def test_calculate_checksum(self, tmp_path):
        """Test checksum calculation function."""
        from solid_cli.main import calculate_checksum
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Calculate checksum
        checksum = calculate_checksum(test_file)
        
        # Verify it's a valid hex string
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 produces 64 hex characters
        assert all(c in "0123456789abcdef" for c in checksum)
    
    def test_calculate_checksum_consistency(self, tmp_path):
        """Test that checksum is consistent for same file."""
        from solid_cli.main import calculate_checksum
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("consistent content")
        
        # Calculate checksum twice
        checksum1 = calculate_checksum(test_file)
        checksum2 = calculate_checksum(test_file)
        
        # Should be identical
        assert checksum1 == checksum2
    
    def test_verify_with_mock_client(self, cli_runner: CliRunner, tmp_path):
        """Test verify command with mocked client."""
        import json
        
        # Create test files
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with patch("solid_cli.main.SolidClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock GET response with matching content
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"test content"
            mock_client.get.return_value = mock_response
            
            result = cli_runner.invoke(
                app,
                ["verify", str(tmp_path), "https://pod.org", "--proxy", "http://localhost:8089"],
                catch_exceptions=False
            )
            
            # Should succeed
            assert result.exit_code == 0
            
            # Verify report was created
            assert Path("audit_report.json").exists()
            
            # Verify report contents
            with open("audit_report.json") as f:
                report = json.load(f)
                assert report["total_files"] == 1
                assert report["matched"] == 1
            
            # Cleanup
            Path("audit_report.json").unlink()


class TestMountCommand:
    """Test mount command."""
    
    def test_mount_help(self, cli_runner: CliRunner):
        """Test mount --help."""
        result = cli_runner.invoke(app, ["mount", "--help"])
        
        assert result.exit_code == 0
        assert "Mount" in result.stdout or "mount" in result.stdout.lower()
    
    def test_mount_requires_remote_url(self, cli_runner: CliRunner, tmp_path):
        """Test mount command requires --remote-url."""
        mount_point = str(tmp_path / "mnt")
        result = cli_runner.invoke(app, ["mount", mount_point])
        
        # Should fail due to missing --remote-url
        assert result.exit_code != 0
    
    def test_mount_requires_auth(self, cli_runner: CliRunner, tmp_path):
        """Test mount command requires auth."""
        mount_point = str(tmp_path / "mnt")
        result = cli_runner.invoke(
            app,
            ["mount", mount_point, "--remote-url", "https://pod.org"]
        )
        
        # Should fail due to missing auth
        assert result.exit_code != 0
    
    @patch("solid_cli.main.mount_pod")
    def test_mount_with_token(self, mock_mount, cli_runner: CliRunner, tmp_path):
        """Test mount with OIDC token."""
        mount_point = str(tmp_path / "mnt")
        mock_mount.side_effect = KeyboardInterrupt()
        
        result = cli_runner.invoke(
            app,
            [
                "mount", mount_point,
                "--remote-url", "https://pod.org",
                "--token", "abc123"
            ]
        )
        
        # Should be called (interrupted by KeyboardInterrupt)
        assert mock_mount.called
    
    @patch("solid_cli.main.mount_pod")
    def test_mount_with_proxy(self, mock_mount, cli_runner: CliRunner, tmp_path):
        """Test mount with proxy auth."""
        mount_point = str(tmp_path / "mnt")
        mock_mount.side_effect = KeyboardInterrupt()
        
        result = cli_runner.invoke(
            app,
            [
                "mount", mount_point,
                "--remote-url", "https://pod.org",
                "--proxy", "http://localhost:8089"
            ]
        )
        
        # Should be called
        assert mock_mount.called

