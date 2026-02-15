# Solid-CLI: A Privacy-Preserving Agent for the Decentralized Web

![Solid-CLI: The Reasoning Agent](https://raw.githubusercontent.com/cafeTechne/solid-cli/master/hero_agent.png)

> **"The Web of data with meaning... allowing a computer program to learn enough about what the data means to process it."** — Tim Berners-Lee

**Solid-CLI** is a command-line interface for **Decentralized Personal Data Stores** ([Solid Pods](https://docs.inrupt.com/ess/2.4/pod-resources)). It implements **[N3Logic](https://www.w3.org/DesignIssues/N3Logic) Client-Side Reasoning** based on the foundational work of **Berners-Lee et al. ([0711.1533](https://arxiv.org/abs/0711.1533))** and **Privacy-Preserving Computation** principles established by **Zhao/Oxford ([2309.16365](https://arxiv.org/abs/2309.16365))**.


---

## Performance: Real Benchmark Results

![Real Benchmark](https://raw.githubusercontent.com/cafeTechne/solid-cli/master/real_benchmark.svg)

**Actual test:** 62 files (3.03 MB) synced using parallel async I/O with bounded semaphores.

---

## Live Demonstration

![Live Demo](https://raw.githubusercontent.com/cafeTechne/solid-cli/master/demo_actual_sync.svg)

Real file synchronization showing the tool scanning directories, uploading files, and generating provenance metadata.

---

## State of the Art Features

*   **N3Logic Reasoning Engine:** Implements forward-chaining inference based on **Berners-Lee et al. ([0711.1533](https://arxiv.org/abs/0711.1533))** and the **[W3C N3Logic](https://www.w3.org/DesignIssues/N3Logic)** framework.
*   **Universal FUSE Mount:** Interoperable file access for virtual assets as proposed for the Open Metaverse by **Macario et al. ([2404.05317](https://arxiv.org/abs/2404.05317), [2408.13520](https://arxiv.org/abs/2408.13520))**.
*   **Privacy-Preserving Computation:** Local execution model following the **Libertas** framework ([Zhao et al., 2023](https://arxiv.org/abs/2309.16365)) to prevent data leakage in decentralized stores.
*   **Verifiable Audit:** Cryptographic integrity reports leveraging the **Issuer-Holder-Verifier model ([2201.07034](https://arxiv.org/abs/2201.07034))** and **PROV-O** provenance tracking.
*   **Knowledge Graph Generation:** Automated extraction of RDF metadata to power **Semantic Search Engines ([1102.0695](https://arxiv.org/abs/1102.0695))**.
*   **Parallel Async I/O:** High-performance "Turbo" sync achieving a **6x speedup** via bounded semaphore architecture.

---

## Quick Start

### Docker (Zero Dependency)
```bash
docker run --rm -it cafeTechne/solid-cli sync ./data https://my.pod/data
```

### Performance & Benchmarks

![Turbo Sync Performance Benchmark](https://raw.githubusercontent.com/cafeTechne/solid-cli/master/benchmark.svg)

`solid-cli` provides a **6x speedup** over traditional linear sync tools by utilizing asynchronous semaphores for parallel network saturation.

---

### Command Line Interface

![Solid-CLI Capabilities](https://raw.githubusercontent.com/cafeTechne/solid-cli/master/cli_help.svg)

### Installation (Python 3.11+)
```bash
pip install solid-cli
solid login
solid mount S: https://my.pod/
```

---

## Documentation
*   **[Submission Statement](SUBMISSION_DRAFT.md)**: DEV.to submission content and challenge statement
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
