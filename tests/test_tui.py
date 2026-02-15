"""Tests for TUI dashboard."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from solid_cli.tui import SolidDashboard


class TestSolidDashboard:
    """Test SolidDashboard TUI component."""

    def test_dashboard_initialization(self):
        """Test SolidDashboard initializes with correct defaults."""
        dashboard = SolidDashboard()
        
        assert "SOLID PROTOCOL SYNC MANAGER" in dashboard.title
        assert dashboard.log_widget is None
        assert dashboard.progress_widget is None
        assert dashboard.status_text is None
        assert dashboard.sync_task is None
        assert dashboard.datatable_widget is None
        assert dashboard.tree_widget is None

    @pytest.mark.skip(reason="Requires Textual app context with active event loop")
    def test_dashboard_compose(self):
        """Test dashboard compose returns correct widgets."""
        dashboard = SolidDashboard()
        
        # Compose should return an iterable of widgets
        widgets = list(dashboard.compose())
        
        # Should have Header, containers, and Footer
        assert len(widgets) > 0

    def test_add_log_with_widget(self):
        """Test add_log writes to log widget when available."""
        dashboard = SolidDashboard()
        dashboard.log_widget = MagicMock()
        
        dashboard.add_log("Test message")
        
        # Verify it called write on the widget
        dashboard.log_widget.write.assert_called_once()
        call_args = dashboard.log_widget.write.call_args[0][0]
        assert "Test message" in call_args

    def test_add_log_without_widget(self):
        """Test add_log gracefully handles missing widget."""
        dashboard = SolidDashboard()
        dashboard.log_widget = None
        
        # Should not raise
        dashboard.add_log("Test message")

    def test_update_progress_with_widget(self):
        """Test update_progress updates widgets when available."""
        dashboard = SolidDashboard()
        dashboard.progress_widget = MagicMock()
        dashboard.status_text = MagicMock()
        
        dashboard.update_progress(50, 100, "Syncing")
        
        # Verify progress widget was updated
        dashboard.progress_widget.update.assert_called_once()
        
        # Verify status text was updated
        dashboard.status_text.update.assert_called_once()
        call_args = dashboard.status_text.update.call_args[0][0]
        assert "Syncing" in call_args
        assert "50%" in call_args

    def test_update_progress_zero_total(self):
        """Test update_progress with zero total."""
        dashboard = SolidDashboard()
        dashboard.progress_widget = MagicMock()
        dashboard.status_text = MagicMock()
        
        dashboard.update_progress(0, 0, "Status")
        
        # Should not crash and should show 0%
        dashboard.status_text.update.assert_called_once()
        call_args = dashboard.status_text.update.call_args[0][0]
        assert "0%" in call_args

    def test_update_progress_without_widgets(self):
        """Test update_progress gracefully handles missing widgets."""
        dashboard = SolidDashboard()
        dashboard.progress_widget = None
        dashboard.status_text = None
        
        # Should not raise
        dashboard.update_progress(50, 100)

    def test_action_clear(self):
        """Test clear action clears log widget."""
        dashboard = SolidDashboard()
        dashboard.log_widget = MagicMock()
        
        dashboard.action_clear()
        
        # Verify clear was called
        dashboard.log_widget.clear.assert_called_once()

    def test_action_clear_without_widget(self):
        """Test clear action gracefully handles missing widget."""
        dashboard = SolidDashboard()
        dashboard.log_widget = None
        
        # Should not raise
        dashboard.action_clear()

    @pytest.mark.asyncio
    async def test_run_sync_success(self):
        """Test run_sync executes sync function successfully."""
        dashboard = SolidDashboard()
        dashboard.log_widget = MagicMock()
        
        # Create a mock async function
        mock_sync = AsyncMock()
        
        await dashboard.run_sync(mock_sync, "arg1", kwarg1="value1")
        
        # Verify sync function was called with correct args
        mock_sync.assert_called_once_with("arg1", kwarg1="value1")

    @pytest.mark.asyncio
    async def test_run_sync_with_exception(self):
        """Test run_sync handles exceptions gracefully."""
        dashboard = SolidDashboard()
        dashboard.log_widget = MagicMock()
        
        # Create a mock async function that raises
        mock_sync = AsyncMock(side_effect=RuntimeError("Test error"))
        
        # Should not raise
        await dashboard.run_sync(mock_sync, "arg1")
        
        # Verify error was logged
        dashboard.log_widget.write.assert_called()
        call_args = [call[0][0] for call in dashboard.log_widget.write.call_args_list]
        assert any("ERROR" in arg or "error" in arg for arg in call_args)

    def test_on_mount(self):
        """Test on_mount initializes log with startup messages."""
        dashboard = SolidDashboard()
        dashboard.log_widget = MagicMock()
        dashboard.datatable_widget = MagicMock()
        
        # Call on_mount
        dashboard.on_mount()
        
        # Verify log was written (3 times with new cyberpunk messages)
        assert dashboard.log_widget.write.call_count >= 1
        call_args = [call[0][0] for call in dashboard.log_widget.write.call_args_list]
        assert any("INITIALIZATION" in arg or "loaded" in arg for arg in call_args)

    def test_dashboard_bindings(self):
        """Test dashboard has correct key bindings."""
        dashboard = SolidDashboard()
        
        # Should have quit, clear, and demo bindings
        binding_names = [binding[1] for binding in dashboard.BINDINGS]
        assert "quit" in binding_names
        assert "clear" in binding_names
        assert "demo" in binding_names

    def test_action_demo(self):
        """Test demo action populates dashboard with fake data."""
        dashboard = SolidDashboard()
        dashboard.log_widget = MagicMock()
        dashboard.datatable_widget = MagicMock()
        dashboard.tree_widget = MagicMock()
        dashboard.status_text = MagicMock()
        
        # Mock set_timer to avoid event loop issues in test
        dashboard.set_timer = MagicMock()
        
        # Call demo action
        dashboard.action_demo()
        
        # Verify log was cleared and datatable was cleared
        dashboard.log_widget.clear.assert_called_once()
        dashboard.datatable_widget.clear.assert_called_once()
        dashboard.tree_widget.clear.assert_called_once()

    def test_dashboard_css(self):
        """Test dashboard CSS is defined."""
        dashboard = SolidDashboard()
        
        # CSS should not be empty
        assert dashboard.CSS
        assert len(dashboard.CSS) > 0
        assert "Screen" in dashboard.CSS
