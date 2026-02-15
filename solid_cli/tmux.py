"""Tmux window management for Solid CLI."""

import libtmux


def launch_dashboard() -> None:
    """Launch dashboard using tmux with split layout.
    
    Creates a tmux session with:
    - Top pane (70%): solid-cli monitor (TUI)
    - Bottom pane (30%): Shell for commands
    """
    server = libtmux.Server()
    
    # Create or get session
    session_name = "solid-cli"
    if any(s.name == session_name for s in server.list_sessions()):
        session = server.sessions.filter(session_name=session_name)[0]
    else:
        session = server.new_session(session_name=session_name)
    
    # Get the main window
    window = session.list_windows()[0]
    pane = window.list_panes()[0]
    
    # Split window vertically (top/bottom) - 70/30 split
    # First, let's create a 70% pane for the monitor
    pane.send_keys("solid monitor", enter=True)
    
    # Split the window horizontally
    new_pane = window.split_window(vertical=False)
    new_pane.resize_pane(height="-30%")
    
    # Send shell to new pane
    new_pane.send_keys("cd .", enter=False)
    
    # Attach to session
    session.attach_session()
