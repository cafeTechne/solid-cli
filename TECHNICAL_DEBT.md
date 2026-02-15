# Technical Debt & Production Roadmap: Solid-CLI

This document outlines the current technical limitations of the `solid-cli` v0.1.0 prototype and provides a strategic roadmap for reaching "Production Grade" status.

## Current Technical Debt

| ID | Issue | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **TD-01** | **Memory-Bound I/O** | High | **Limit Upload Size**: For v0.1.0, avoid syncing files > 100MB. Use `split` for larger datasets. |
| **TD-02** | **Sync Logic (HEAD-only)** | Medium | **Manual Verification**: Run `solid verify` after sync to confirm hash integrity. |
| **TD-03** | **Watch Mode Concurrency** | High | **Atomic Changes**: Avoid mass-moving directories while `watch` is active. |
| **TD-04** | **FUSE Enumeration** | High | **CLI for Browsing**: Use `solid ls` (planned) or Pod-native web UI for navigation. |
| **TD-05** | **Reasoner Depth** | Low | **Flat Hierarchies**: Maintain Pod structure within 10 levels of depth for reliable inference. |

---

## Production Readiness Roadmap

### Phase 1: Infrastructure Robustness
- [ ] **Implement Streaming I/O**: Refactor `SolidClient.put` to use `httpx` stream generators to eliminate OOM risks.
- [ ] **Intelligent Sync**: Transition from `HEAD` checks to a metadata-driven sync (Timestamp + ETag comparison).
- [ ] **Exponential Backoff**: Implement a retry decorator for all HTTP operations to handle transient network 5xx errors.

### Phase 2: FUSE Native Experience
- [ ] **LDP Container Parsing**: Implement Turtle/JSON-LD parsing of container responses to populate `readdir`.
- [ ] **Write-Back Cache**: Implement a local cache layer to allow "instant" save operations with background syncing.

### Phase 3: Advanced Reasoning
- [ ] **Dynamic Dependency Resolution**: Allow the reasoner to fetch remote ontologies ($RDFS/OWL$) to verify extended logic rules.
- [ ] **Cryptographic Provenance**: Integrate `sign-py` to provide detached JWS signatures for every file synced.

---

## Conclusion
The current version of `solid-cli` is a high-performance **Proof of Concept**. It demonstrates the viability of Decentralized Personal Data Stores when paired with Semantic Reasoning. The architectural gaps identified above are well-understood and prioritized for the next development cycle.

*Documented as part of the GitHub Copilot CLI Challenge.*
