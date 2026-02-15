# Works Cited: The Scientific Foundation of Solid-CLI

This project implements concepts from the following research papers to align with the "State of the Art" in Decentralized Web technology.

## Core Architecture

### 1. N3Logic: A Logical Framework For the World Wide Web ([0711.1533](https://arxiv.org/abs/0711.1533))
**Authors:** Tim Berners-Lee, Dan Connolly, et al.
**Key Concept:** "Logic must be powerful enough to describe complex properties... allowing rules to be expressed in a Web environment."
**Implementation:** Phase 7.2 (Semantic Reasoning Engine). We use N3 rules to infer trust and metadata.

### 2. Libertas: Privacy-Preserving Collaborative Computation ([2309.16365](https://arxiv.org/abs/2309.16365))
**Authors:** Rui Zhao, et al. (Oxford)
**Key Concept:** "Decentrised Personal Data Stores" require local computations to prevent data leakage.
**Implementation:** The Reasoning Engine runs *locally* to infer metadata, keeping "reasoning" close to the data.

### 3. A Manifesto for Web Science @10 ([1702.08291](https://arxiv.org/abs/1702.08291))
**Authors:** Wendy Hall, Jim Hendler, et al.
**Key Concept:** The Web influences "Human Rights" and "Social Good".
**Implementation:** We frame `solid verify` as a tool for **Data Sovereignty**.

## Advanced Applications (The "Metaverse" & "Trust" Layers)

### 4. WebXR as a Basis for an Open Metaverse ([2404.05317](https://arxiv.org/abs/2404.05317) & [2408.13520](https://arxiv.org/abs/2408.13520))
**Authors:** Giuseppe Macario, et al.
**Key Concept:** "Spatial web apps" require open, interoperable access to virtual assets.
**Implementation:** Phase 7.3 (Universal FUSE Mount). By mounting a Pod as a local filesystem, we allow standard 3D tools (Blender, Unity, A-Frame) to access decentralized assets natively.

### 5. Verifiable Credentials for Healthcare ([2201.07034](https://arxiv.org/abs/2201.07034))
**Key Concept:** The "Issuer-Holder-Verifier" model for trust.
**Implementation:** The `solid verify` command acts as a **Verifier**, generating a cryptographically signed "Audit Report" that proves the integrity of the data in the Pod.

### 6. Semantic Search Engine ([1102.0695](https://arxiv.org/abs/1102.0695))
**Key Concept:** Using ontologies to improve search precision.
**Implementation:** Our "PKG Extraction" generates the RDF metadata necessary for these semantic search engines to function.

---
**Submission Note:** This bibliography is the "References" section of our final submission.
