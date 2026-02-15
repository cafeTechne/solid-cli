# Solid-CLI: The Privacy-Preserving Agent

> **"The Web of data with meaning... allowing a computer program to learn enough about what the data means to process it."** — Tim Berners-Lee

**Solid-CLI** is a command-line interface for **Decentralized Personal Data Stores** (Solid Pods). It implements **Client-Side Reasoning** (N3Logic) and **Privacy-Preserving Computation**, bridging the gap between your local OS and the Semantic Web.

---

## Performance: Real Benchmark Results

![Real Benchmark](real_benchmark.svg)

**Actual test:** 62 files (3.03 MB) synced using parallel async I/O with bounded semaphores.

---

## Live Demonstration

![Actual Sync](demo_actual_sync.svg)

Real file synchronization showing the tool scanning directories, uploading files, and generating provenance metadata.

---

## State of the Art Features

*   **N3Logic Reasoning Engine:** Implements forward-chaining inference based on Berners-Lee et al. (`0711.1533`)
*   **Universal FUSE Mount:** Cross-platform filesystem driver (Windows/macOS/Linux)
*   **Parallel Async I/O:** Bounded semaphore architecture for optimal throughput
*   **Verifiable Audit:** PROV-O provenance tracking and cryptographic integrity reports

---

## Quick Start

### Docker (Zero Dependency)
```bash
docker run --rm -it cafeTechne/solid-cli sync ./data https://my.pod/data
```

### Installation (Python 3.11+)
```bash
pip install solid-cli
solid login
solid mount S: https://my.pod/
```

---

## Documentation
*   **[Submission Paper](SUBMISSION.md)**: Scientific methodology and academic citations
*   **[Works Cited](WORKS_CITED.md)**: Research papers backing this implementation
*   **[Technical Debt](TECHNICAL_DEBT.md)**: Production roadmap and architectural audit

---

## Technical Details

### Test Coverage (86% overall)
*   **Core Logic (100% tested):**
    - `reasoner.py`: N3Logic inference engine
    - `auth.py`: OIDC authentication
    - `client.py`: HTTP client with retry logic
*   **Well-tested (85-95%):**
    - `sync.py`: Parallel async upload/download
    - `verify.py`: Integrity checking and audit reports
    - `mount.py`: FUSE filesystem driver (89%)
*   **Partially tested (70-85%):**
    - `tui.py`: Textual dashboard (platform-specific UI interactions)
    - `main.py`: CLI entry points (some error paths untested)

**Untested areas:** OS-specific error handling (e.g., WinFsp not installed), edge cases in interactive TUI prompts.

### Test Suite
*   **Tests:** 166 passed, 1 skipped
*   **License:** MIT
*   **Repository:** [cafeTechne/solid-cli](https://github.com/cafeTechne/solid-cli)

Built with GitHub Copilot CLI as a pair programmer.
