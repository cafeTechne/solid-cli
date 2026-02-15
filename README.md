# Solid CLI

A high-performance synchronization and management tool for Solid Pods (Decentralized Web).

## Features

- 🚀 Async HTTP operations with `httpx`
- 🔐 Multiple authentication strategies (OIDC DPoP, Proxy)
- 📁 Local-to-remote directory synchronization
- 🔒 ACL management with RDF/Turtle support
- 🎨 Rich CLI output and TUI dashboard
- 🪟 Tmux integration for multi-pane workflows

## Installation

```bash
uv pip install -e .
```

## Quick Start

### Sync local directory to Solid Pod

```bash
solid sync ./local-folder https://pod.example.com/ --token YOUR_DPOP_TOKEN
```

### Share a resource

```bash
solid share https://pod.example.com/resource.ttl https://agent.example.com/profile/card#me --mode Read
```

### Launch dashboard

```bash
solid monitor --token YOUR_DPOP_TOKEN
```

### Launch with Tmux

```bash
solid tmux
```

## Architecture

- **theme.py**: Styling and banner utilities
- **auth.py**: Authentication providers (OIDC, Proxy)
- **client.py**: Async HTTP client with auth injection
- **sync.py**: Directory synchronization logic
- **acl.py**: ACL management with RDF
- **tui.py**: Textual-based dashboard
- **tmux.py**: Tmux session management
- **main.py**: Typer CLI app

## Requirements

- Python 3.11+
- httpx (async HTTP)
- rdflib (RDF handling)
- typer (CLI framework)
- textual (TUI)
- libtmux (Tmux control)
- pyfiglet (ASCII art)
- pydantic (data validation)
