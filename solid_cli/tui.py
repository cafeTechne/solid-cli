"""Terminal User Interface (TUI) for Solid CLI using Textual - Professional Edition."""

import asyncio
from typing import Optional, Callable
from textual.app import ComposeResult, App
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, RichLog, ProgressBar, Static, Tree, DataTable
from textual.reactive import reactive
from textual.timer import Timer
from .sync import sync_local_to_remote
from .client import SolidClient
from .auth import ProxyAuthProvider


class SolidDashboard(App):
    """Solid Protocol Sync Manager TUI Dashboard - Professional Style."""

    CSS = """
    Screen {
        background: $surface;
        layout: vertical;
    }

    Screen > Header {
        background: #20b2aa;
        color: #ffffff;
        text-style: bold;
    }

    Screen > Footer {
        background: #2d5f5f;
        color: #20b2aa;
    }

    #main-container {
        width: 100%;
        height: 100%;
        background: #1a3a3a;
    }

    #title {
        width: 100%;
        content-align: center middle;
        background: #1a3a3a;
        color: #20b2aa;
        text-style: bold;
    }

    #pod-tree {
        width: 20%;
        background: #1a3a3a;
        color: #20b2aa;
        border: heavy #20b2aa;
    }

    #right-panel {
        width: 80%;
        height: 100%;
    }

    #active-transfers {
        height: 50%;
        background: #1a3a3a;
        color: #20b2aa;
        border: heavy #20b2aa;
    }

    #sync-log {
        background: #1a3a3a;
        color: #20b2aa;
        height: 40%;
        border: heavy #20b2aa;
    }

    #progress-container {
        height: 10%;
        background: #1a3a3a;
    }

    ProgressBar {
        width: 100%;
        height: 2;
    }

    #status-text {
        width: 100%;
        height: 1;
        content-align: left middle;
        color: #20b2aa;
    }

    DataTable {
        background: #1a3a3a;
        color: #20b2aa;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear", "Clear"),
        ("d", "demo", "Demo Mode"),
        ("s", "sync", "Start Sync"),
    ]

    progress: reactive[int] = reactive(0)

    def __init__(self, *args, **kwargs):
        """Initialize professional dashboard."""
        super().__init__(*args, **kwargs)
        self.title = "SOLID PROTOCOL SYNC MANAGER"
        self.log_widget: Optional[RichLog] = None
        self.progress_widget: Optional[ProgressBar] = None
        self.status_text: Optional[Static] = None
        self.tree_widget: Optional[Tree] = None
        self.datatable_widget: Optional[DataTable] = None
        self.sync_task: Optional[asyncio.Task] = None
        self.demo_timer: Optional[Timer] = None
        self.sync_queue: asyncio.Queue = asyncio.Queue()

    def compose(self) -> ComposeResult:
        """Compose professional dashboard layout."""
        yield Header(show_clock=False)
        
        with Container(id="main-container"):
            yield Static("[bold #20b2aa]POD SYNCHRONIZATION STATUS[/bold #20b2aa]", id="title")
            
            with Horizontal():
                # Left panel: Pod filesystem tree (20%)
                self.tree_widget = Tree("[bold #20b2aa]POD FILESYSTEM[/bold #20b2aa]", id="pod-tree")
                yield self.tree_widget
                
                # Right panel: Active transfers and logs (80%)
                with Vertical(id="right-panel"):
                    # Active transfers table
                    self.datatable_widget = DataTable(id="active-transfers")
                    yield self.datatable_widget
                    
                    # Logs and progress
                    self.log_widget = RichLog(markup=True, id="sync-log")
                    yield self.log_widget
                    
                    with Container(id="progress-container"):
                        self.status_text = Static("[bold #20b2aa]READY[/bold #20b2aa]", id="status-text")
                        yield self.status_text
                        
                        self.progress_widget = ProgressBar(total=100, id="progress")
                        yield self.progress_widget
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        # Setup DataTable with columns
        if self.datatable_widget:
            self.datatable_widget.add_columns(
                "File",
                "Size",
                "Speed",
                "Status"
            )
        
        # Initial log message
        if self.log_widget:
            self.log_widget.write("[bold #20b2aa]SYSTEM INITIALIZATION[/bold #20b2aa]")
            self.log_widget.write("[#20b2aa]Textual Terminal Interface loaded[/#20b2aa]")
            self.log_widget.write("[#20b2aa]Ready for synchronization operations[/#20b2aa]")
        
        # Schedule queue monitor to run forever (safely in app context)
        try:
            self.create_task(self.monitor_queue())
        except AttributeError:
            # Outside app context (e.g., during testing)
            pass

    def add_log(self, message: str) -> None:
        """Add message to log widget."""
        if self.log_widget:
            self.log_widget.write(f"[#20b2aa]{message}[/#20b2aa]")

    def update_progress(self, current: int, total: int, status: str = "") -> None:
        """Update progress bar."""
        if self.progress_widget and total > 0:
            self.progress_widget.update(progress=current, total=total)
        
        if self.status_text:
            percent = int((current / total * 100)) if total > 0 else 0
            self.status_text.update(f"[bold #20b2aa]{status} [{percent}%][/bold #20b2aa]")

    async def monitor_queue(self) -> None:
        """Monitor sync queue and display messages in real-time."""
        while True:
            try:
                msg = await asyncio.wait_for(self.sync_queue.get(), timeout=0.1)
                self.add_log(msg)
                
                # Extract percentage if message contains it
                if "%" in msg:
                    import re
                    match = re.search(r'(\d+)%', msg)
                    if match:
                        percent = int(match.group(1))
                        self.update_progress(percent, 100, "SYNCING")
            except asyncio.TimeoutError:
                continue
    
    async def action_sync(self) -> None:
        """Launch sync operation with real-time queue monitoring."""
        # Demo configuration (hardcoded for now)
        local_dir = "/tmp/test_sync"
        remote_url = "https://pod.example.org/sync"
        
        # Create client with proxy auth
        auth = ProxyAuthProvider("http://localhost:8089")
        client = SolidClient(auth=auth)
        
        def on_log_callback(msg: str):
            """Callback to queue log messages."""
            try:
                self.sync_queue.put_nowait(msg)
            except Exception:
                pass
        
        def on_progress_callback(bytes_sent: int, total_bytes: int, description: str):
            """Callback to queue progress updates."""
            if total_bytes > 0:
                percent = int((bytes_sent / total_bytes) * 100)
                self.sync_queue.put_nowait(f"{description}: {percent}%")
        
        # Launch sync in background
        self.sync_task = asyncio.create_task(
            sync_local_to_remote(
                client,
                local_dir,
                remote_url,
                on_progress=on_progress_callback,
                on_log=on_log_callback,
            )
        )
        
        self.add_log("Sync operation started")

    def action_clear(self) -> None:
        """Clear log widget."""
        if self.log_widget:
            self.log_widget.clear()
        if self.datatable_widget:
            self.datatable_widget.clear()

    def action_demo(self) -> None:
        """Launch professional demo mode."""
        if self.demo_timer:
            self.demo_timer.stop()
            return
        
        # Clear existing data
        if self.log_widget:
            self.log_widget.clear()
        if self.datatable_widget:
            self.datatable_widget.clear()
        if self.tree_widget:
            self.tree_widget.clear()
        
        # Populate tree with text-only labels, all nodes expanded
        if self.tree_widget:
            root = self.tree_widget.root
            
            root_dir = root.add("Root", expand=True)
            private = root.add("Private", expand=True)
            public = root.add("Public", expand=True)
            
            root_dir.add("config.ttl")
            root_dir.add("keys.pem")
            
            private.add("profile.ttl")
            private.add("data.json")
            
            photos = public.add("Photos", expand=True)
            photos.add("sunset.jpg")
            photos.add("city.png")
            public.add("Documents")
        
        # Add demo rows to DataTable with plain text columns
        if self.datatable_widget:
            files = [
                ("report.pdf", "15MB", "45MB/s", "[yellow]ENCRYPTING[/yellow]"),
                ("archive.zip", "128MB", "52MB/s", "[green]COMPLETE[/green]"),
                ("media.mp4", "256MB", "38MB/s", "[cyan]UPLOADING[/cyan]"),
                ("dataset.csv", "8MB", "61MB/s", "[magenta]VERIFYING[/magenta]"),
            ]
            for file, size, speed, status in files:
                self.datatable_widget.add_row(file, size, speed, status)
        
        # Stream log messages with standard pacing (0.5 second intervals)
        log_messages = [
            "[bold #20b2aa]AUTHENTICATION PROTOCOL INITIATED[/bold #20b2aa]",
            "[#20b2aa]Establishing secure connection to pod...[/#20b2aa]",
            "[bold #20b2aa]AUTH HANDSHAKE VALID[/bold #20b2aa]",
            "[#20b2aa]Public key exchange successful[/#20b2aa]",
            "[#20b2aa]ACL RESOLUTION ACTIVE[/#20b2aa]",
            "[bold #20b2aa]ACL RESOLVED: WRITE ACCESS GRANTED[/bold #20b2aa]",
            "[#20b2aa]INITIATING SYNC SEQUENCE[/#20b2aa]",
            "[#20b2aa]SYNCING SHARD 01[/#20b2aa]",
            "[#20b2aa]SYNCING SHARD 02[/#20b2aa]",
            "[#20b2aa]SYNCING SHARD 03[/#20b2aa]",
            "[#20b2aa]Encryption layer: AES-256[/#20b2aa]",
            "[bold #20b2aa]DATA INTEGRITY: VERIFIED[/bold #20b2aa]",
            "[#20b2aa]Synchronization complete[/#20b2aa]",
        ]
        
        if self.log_widget:
            for i, msg in enumerate(log_messages):
                # Standard pacing: 0.5 second intervals (~6.5 seconds total)
                self.set_timer(i * 0.5, lambda m=msg: self.log_widget.write(m))
        
        # Simulate progress animation (10 seconds total)
        def animate_progress():
            for progress in range(0, 101, 5):
                # 10 seconds total: progress * 0.1
                self.set_timer(progress * 0.1, lambda p=progress: 
                    self.update_progress(p, 100, "SYNC RUNNING"))
        
        animate_progress()

    async def run_sync(
        self,
        sync_func: Callable,
        *args,
        **kwargs,
    ) -> None:
        """Run sync operation in background and update UI.
        
        Args:
            sync_func: Async function to run
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        try:
            await sync_func(*args, **kwargs)
        except Exception as e:
            self.add_log(f"[bold #ff0000]ERROR: {e}[/bold #ff0000]")

