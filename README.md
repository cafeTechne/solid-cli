# Solid-CLI: The Privacy-Preserving Agent

> **"The Web of data with meaning... allowing a computer program to learn enough about what the data means to process it."** — Tim Berners-Lee

**Solid-CLI** is a command-line interface for **Decentralized Personal Data Stores** ([Solid Pods](https://docs.inrupt.com/ess/2.4/pod-resources)). It implements **N3Logic Client-Side Reasoning** based on the foundational work of **Berners-Lee et al. ([0711.1533](https://arxiv.org/abs/0711.1533))** and **Privacy-Preserving Computation** principles established by **Zhao/Oxford ([2309.16365](https://arxiv.org/abs/2309.16365))**.

---

## Scientific Foundation Core

Solid-CLI is engineered as an infrastructure-level extension of the Web, moving beyond traditional architectural patterns to implement rigorous computer science concepts:

### 1. Client-Side Reasoning (N3Logic)
Following the **N3Logic** framework ([Berners-Lee et al., 2007](https://arxiv.org/abs/0711.1533)), we implement a local inference engine that enables true data sovereignty. The client doesn't just store data; it understands its meaning, automatically inferring trust levels and metadata using forward-chaining rules.

### 2. Privacy-Preserving Compute (Libertas)
Inspired by the **Libertas** model ([Zhao et al., 2023](https://arxiv.org/abs/2309.16365)), our reasoning engine executes locally. This ensures that sensitive inferences are made before data ever leaves the user's control, fulfilling the requirements for collaborative computation in decentralized stores.

### 3. The Open Metaverse (WebXR Interoperability)
As proposed by **Macario et al. ([2408.13520](https://arxiv.org/abs/2408.13520))**, decentralized virtual assets require universal access. Our **FUSE Mount** (WinFsp/libfuse) follows these interoperability standards, allowing tools like Blender or Unity to treat decentralized Pods as local storage volumes.

---

## Performance: Real Benchmark Results

![Real Benchmark](https://raw.githubusercontent.com/cafeTechne/solid-cli/master/real_benchmark.svg)

**Turbo Sync Performance:** 
By leveraging parallel async I/O with bounded semaphores, we achieved a **6x speedup** over traditional linear sync tools, maintaining a sustained throughput of **3.13 MB/s** in real-world Pod environments.

---

## Live Demonstration

![Live Demo](https://raw.githubusercontent.com/cafeTechne/solid-cli/master/demo_actual_sync.svg)

Demonstration of the **Trust Audit** workflow: scanning local directories, performing delta-checks via HTTP HEAD, and generating **PROV-O** provenance metadata ([W3C, 2013]) for every file.

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
*   **[Submission Statement](SUBMISSION_DRAFT.md)**: DEV.to submission content and challenge statement
*   **[Works Cited](WORKS_CITED.md)**: Full bibliography of research backing this implementation
*   **[Technical Debt](TECHNICAL_DEBT.md)**: Architectural audit and production roadmap

---

## Technical Integrity

### Test Coverage (86% overall)
*   **Core Logic (100% tested):** `reasoner.py` (N3Logic), `auth.py`, `client.py`
*   **Systems (85-95%):** `sync.py` (Parallel I/O), `verify.py` (Trust Audit), `mount.py` (FUSE Driver)
*   **Suite:** 166 passed, 1 skipped. Verified via `pytest-cov`.

---
**License:** MIT | **Repository:** [cafeTechne/solid-cli](https://github.com/cafeTechne/solid-cli)
*Built for the [GitHub Copilot CLI Challenge](https://dev.to/t/githubcopilotchallenge).*
