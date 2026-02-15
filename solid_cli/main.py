"""Main CLI entry point for Solid CLI."""

import asyncio
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import typer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from rich.table import Table
from rich.console import Console
from . import theme
from .agent import parse_natural_language
from .auth import ProxyAuthProvider, OIDCAuthProvider
from .client import SolidClient
from .sync import sync_local_to_remote
from .tui import SolidDashboard
from .tmux import launch_dashboard
from .mount import mount_pod

app = typer.Typer(help="Solid CLI - Sync and manage Solid Pods")


@app.callback()
def main(
    proxy: Optional[str] = typer.Option(
        None, "--proxy", help="Proxy server URL for authentication"
    ),
):
    """Solid CLI main entry point."""
    pass


@app.command()
def sync(
    local_dir: str = typer.Argument(..., help="Local directory to sync"),
    remote_url: str = typer.Argument(..., help="Remote Solid Pod URL"),
    token: Optional[str] = typer.Option(None, "--token", help="OIDC DPoP token"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL"),
):
    """Synchronize local directory to remote Solid Pod."""
    theme.print_banner()
    
    # Choose auth provider
    if proxy:
        auth = ProxyAuthProvider(proxy)
    elif token:
        auth = OIDCAuthProvider(token)
    else:
        typer.echo("Error: Must provide --token or --proxy", err=True)
        raise typer.Exit(1)
    
    async def run_sync():
        async with SolidClient(auth) as client:
            def log_callback(msg: str):
                typer.echo(msg)
            
            await sync_local_to_remote(
                client,
                local_dir,
                remote_url,
                on_log=log_callback,
            )
    
    asyncio.run(run_sync())


@app.command()
def share(
    resource_url: str = typer.Argument(..., help="Resource URL to share"),
    agent_webid: str = typer.Argument(..., help="Agent WebID to grant access"),
    mode: str = typer.Option("Read", "--mode", help="ACL mode (Read/Write/Append/Control)"),
    token: Optional[str] = typer.Option(None, "--token", help="OIDC DPoP token"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL"),
):
    """Update ACL to share a resource with an agent."""
    theme.print_banner()
    
    # Choose auth provider
    if proxy:
        auth = ProxyAuthProvider(proxy)
    elif token:
        auth = OIDCAuthProvider(token)
    else:
        typer.echo("Error: Must provide --token or --proxy", err=True)
        raise typer.Exit(1)
    
    async def run_share():
        from .acl import update_acl
        async with SolidClient(auth) as client:
            await update_acl(client, resource_url, agent_webid, mode)
            typer.echo(f"✓ Granted {mode} access to {agent_webid}")
    
    asyncio.run(run_share())


@app.command()
def monitor(
    token: Optional[str] = typer.Option(None, "--token", help="OIDC DPoP token"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL"),
):
    """Launch TUI dashboard for monitoring."""
    theme.print_banner()
    
    # Launch dashboard
    dashboard = SolidDashboard()
    dashboard.run()


@app.command()
def tmux():
    """Launch dashboard in tmux with split layout."""
    theme.print_banner()
    launch_dashboard()


@app.command()
def agent(
    prompt: str = typer.Argument(..., help="Natural language command"),
    token: Optional[str] = typer.Option(None, "--token", help="OIDC DPoP token"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL"),
):
    """Execute a natural language command."""
    theme.print_banner()
    
    # Parse natural language
    result = parse_natural_language(prompt)
    
    # Check if parsing succeeded
    if isinstance(result, str):
        typer.echo(result)
        raise typer.Exit(1)
    
    intent, arg1, arg2 = result
    
    # Route to appropriate command
    if intent == "sync":
        typer.echo(f"Syncing {arg1} to {arg2}...")
        # Invoke sync command with parsed arguments
        ctx = typer.get_current().obj if hasattr(typer.get_current(), 'obj') else None
        sync(local_dir=arg1, remote_url=arg2, token=token, proxy=proxy)
    
    elif intent == "share":
        typer.echo(f"Sharing {arg1} with {arg2}...")
        # Invoke share command with parsed arguments
        share(resource_url=arg1, agent_webid=arg2, token=token, proxy=proxy)
    
    elif intent == "ls":
        typer.echo(f"Listing files in {arg1}...")
        typer.echo("(Feature not yet implemented)")
    
    else:
        typer.echo(f"Unknown intent: {intent}")
        raise typer.Exit(1)


class SolidEventHandler(FileSystemEventHandler):
    """File system event handler for syncing changes to Solid Pod."""
    
    def __init__(self, client: SolidClient, local_dir: str, remote_url: str):
        """Initialize event handler.
        
        Args:
            client: SolidClient instance for remote operations
            local_dir: Local directory being watched
            remote_url: Remote Solid Pod base URL
        """
        super().__init__()
        self.client = client
        self.local_dir = Path(local_dir)
        self.remote_url = remote_url
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        local_path = Path(event.src_path)
        try:
            rel_path = local_path.relative_to(self.local_dir)
            remote_path = self.remote_url.rstrip("/") + "/" + str(rel_path).replace("\\", "/")
            
            # Upload file asynchronously
            asyncio.run(self._upload_file(local_path, remote_path))
        except Exception as e:
            typer.echo(f"Error handling created file {event.src_path}: {e}", err=True)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        local_path = Path(event.src_path)
        try:
            rel_path = local_path.relative_to(self.local_dir)
            remote_path = self.remote_url.rstrip("/") + "/" + str(rel_path).replace("\\", "/")
            
            # Upload file asynchronously
            asyncio.run(self._upload_file(local_path, remote_path))
        except Exception as e:
            typer.echo(f"Error handling modified file {event.src_path}: {e}", err=True)
    
    async def _upload_file(self, local_path: Path, remote_path: str):
        """Upload a single file to the remote pod.
        
        Args:
            local_path: Path to local file
            remote_path: Remote URL for the file
        """
        try:
            with open(local_path, "rb") as f:
                content = f.read()
            
            response = await self.client.put(remote_path, content=content)
            
            if response.status_code in (200, 201):
                typer.echo(f"✓ Synced: {local_path.name}")
            else:
                typer.echo(
                    f"✗ Sync failed: {local_path.name} (Status: {response.status_code})",
                    err=True
                )
        except Exception as e:
            typer.echo(f"✗ Error uploading {local_path.name}: {e}", err=True)


@app.command()
def watch(
    local_dir: str = typer.Argument(..., help="Local directory to watch"),
    remote_url: str = typer.Argument(..., help="Remote Solid Pod URL"),
    token: Optional[str] = typer.Option(None, "--token", help="OIDC DPoP token"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL"),
):
    """Watch local directory and sync changes to remote Solid Pod."""
    theme.print_banner()
    
    # Validate local directory
    local_path = Path(local_dir)
    if not local_path.exists():
        typer.echo(f"Error: Directory not found: {local_dir}", err=True)
        raise typer.Exit(1)
    
    # Choose auth provider
    if proxy:
        auth = ProxyAuthProvider(proxy)
    elif token:
        auth = OIDCAuthProvider(token)
    else:
        typer.echo("Error: Must provide --token or --proxy", err=True)
        raise typer.Exit(1)
    
    async def run_watch():
        async with SolidClient(auth) as client:
            # Create event handler
            event_handler = SolidEventHandler(client, local_dir, remote_url)
            
            # Setup observer
            observer = Observer()
            observer.schedule(event_handler, local_dir, recursive=True)
            observer.start()
            
            typer.echo(f"Watching {local_dir} for changes...")
            typer.echo("Press Ctrl+C to stop")
            
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                observer.join()
                typer.echo("Watch stopped")
    
    asyncio.run(run_watch())


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Hex digest of SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


@app.command()
def verify(
    local_dir: str = typer.Argument(..., help="Local directory to verify"),
    remote_url: str = typer.Argument(..., help="Remote Solid Pod URL"),
    token: Optional[str] = typer.Option(None, "--token", help="OIDC DPoP token"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL"),
):
    """Verify local files against remote Solid Pod and generate audit report."""
    theme.print_banner()
    
    # Validate local directory
    local_path = Path(local_dir)
    if not local_path.exists():
        typer.echo(f"Error: Directory not found: {local_dir}", err=True)
        raise typer.Exit(1)
    
    # Choose auth provider
    if proxy:
        auth = ProxyAuthProvider(proxy)
    elif token:
        auth = OIDCAuthProvider(token)
    else:
        typer.echo("Error: Must provide --token or --proxy", err=True)
        raise typer.Exit(1)
    
    async def run_verify():
        async with SolidClient(auth) as client:
            # Collect verification results
            results = []
            table = Table(title="File Verification Report")
            table.add_column("File", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Checksum", style="green")
            
            # Walk local directory
            for root, dirs, files in Path(local_dir).walk():
                for file in files:
                    local_file = Path(root) / file
                    rel_path = local_file.relative_to(local_path)
                    remote_path = remote_url.rstrip("/") + "/" + str(rel_path).replace("\\", "/")
                    
                    try:
                        # Calculate local checksum
                        local_hash = calculate_checksum(local_file)
                        
                        # Download remote file
                        remote_response = await client.get(remote_path)
                        
                        if remote_response.status_code == 200:
                            # Calculate remote checksum
                            remote_hash = hashlib.sha256(remote_response.content).hexdigest()
                            
                            # Compare
                            if local_hash == remote_hash:
                                status = "[green]✓ MATCH[/green]"
                                status_text = "MATCH"
                            else:
                                status = "[red]✗ MISMATCH[/red]"
                                status_text = "MISMATCH"
                            
                            result = {
                                "file": str(rel_path),
                                "status": status_text,
                                "local_hash": local_hash,
                                "remote_hash": remote_hash,
                            }
                        else:
                            status = "[yellow]? NOT FOUND[/yellow]"
                            result = {
                                "file": str(rel_path),
                                "status": "NOT_FOUND",
                                "local_hash": local_hash,
                                "remote_hash": None,
                            }
                        
                        results.append(result)
                        table.add_row(str(rel_path), status, local_hash[:16] + "...")
                        
                    except Exception as e:
                        typer.echo(f"Error verifying {rel_path}: {e}", err=True)
                        result = {
                            "file": str(rel_path),
                            "status": "ERROR",
                            "error": str(e),
                        }
                        results.append(result)
                        table.add_row(str(rel_path), "[red]✗ ERROR[/red]", "N/A")
            
            # Display table
            console = Console()
            console.print(table)
            
            # Save report to JSON
            report = {
                "local_dir": local_dir,
                "remote_url": remote_url,
                "total_files": len(results),
                "matched": sum(1 for r in results if r.get("status") == "MATCH"),
                "mismatched": sum(1 for r in results if r.get("status") == "MISMATCH"),
                "not_found": sum(1 for r in results if r.get("status") == "NOT_FOUND"),
                "errors": sum(1 for r in results if r.get("status") == "ERROR"),
                "files": results,
            }
            
            # Write report
            with open("audit_report.json", "w") as f:
                json.dump(report, f, indent=2)
            
            typer.echo(f"\n✓ Report saved to audit_report.json")
            typer.echo(f"Matched: {report['matched']}, Mismatched: {report['mismatched']}, " +
                      f"Not Found: {report['not_found']}, Errors: {report['errors']}")
    
    asyncio.run(run_verify())


@app.command()
def mount(
    mount_point: str = typer.Argument(..., help="Local filesystem mount point"),
    remote_url: Optional[str] = typer.Option(None, "--remote-url", help="Remote Solid Pod URL"),
    token: Optional[str] = typer.Option(None, "--token", help="OIDC DPoP token"),
    proxy: Optional[str] = typer.Option(None, "--proxy", help="Proxy URL"),
):
    """Mount a Solid Pod as a virtual filesystem."""
    theme.print_banner()
    
    # Remote URL is required
    if not remote_url:
        typer.echo("Error: --remote-url is required", err=True)
        raise typer.Exit(1)
    
    # Choose auth provider
    if proxy:
        auth = ProxyAuthProvider(proxy)
    elif token:
        auth = OIDCAuthProvider(token)
    else:
        typer.echo("Error: Must provide --token or --proxy", err=True)
        raise typer.Exit(1)
    
    async def run_mount():
        async with SolidClient(auth) as client:
            typer.echo(f"Mounting {remote_url} at {mount_point}...")
            mount_pod(mount_point, client, remote_url)
    
    try:
        asyncio.run(run_mount())
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except KeyboardInterrupt:
        typer.echo("\nMount stopped")


if __name__ == "__main__":
    app()
