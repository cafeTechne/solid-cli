# Solid-CLI: The Privacy-Preserving Agent

> **"The Web of data with meaning... allowing a computer program to learn enough about what the data means to process it."** — Tim Berners-Lee

**Solid-CLI** is a command-line interface for **Decentralized Personal Data Stores** (Solid Pods). It implements **Client-Side Reasoning** (N3Logic) and **Privacy-Preserving Computation**, bridging the gap between your local OS and the Semantic Web.

---

## Performance: Real Benchmark Results

![Real Benchmark](real_benchmark.svg)

**Actual test:** 62 files (3.03 MB) synced using parallel async I/O with bounded semaphores.

---

## Command Reference

![CLI Help](real_cli_help.svg)

Full command documentation showing sync, verify, mount, and monitor capabilities.

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

---

## Technical Details
*   **Tests:** 166 passed, 1 skipped
*   **Coverage:** 86%
*   **License:** MIT
*   **Repository:** [cafeTechne/solid-cli](https://github.com/cafeTechne/solid-cli)

Built with GitHub Copilot CLI as a pair programmer.
