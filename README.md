
<div align="center"><img width="424" height="424" alt="Hephislog_icon" src="https://github.com/user-attachments/assets/69655ad8-ee6a-44d2-9657-15db7d7d60d1" /></div>

[Leia o resumo em pt-br](docs/readme-pt-br.md)

## Hephislogº - Event-Driven Swarm Pipeline for Inteligent Data Ingestion & Normalization

  The system is built as a swarm of single-resposability agents, coordinated via and internal event bus, enabling flexible orchestration, traceability, and continuos learning across runs.

  This project demonstrates production-grade patterns commonly required in IT consulting, system integration, data plataforms, and observability-heavy enviroments.

  Hephislogº is a modular, event driven processing framework designed to ingest unstructured inputs, infer intent through probabilistic signals, and transform them into validated, normalized, and auditable outputs, without hard coded pipelines.

## Core Concepts

### Event-Driven Architecture

All processing is coordinated through a decoupled event bus. 
Agents subscribe to semantic events (e.g. system.input_received, intent.organize.music) rather than calling each other directly.

### Swarm-Based Agent Design

Each agent performs one well-defined role:

- sniffing & signal extraction
- input identification
- decision-making under uncertainty
- domain organization
- normalization & validation
- packing & persistence
- reporting & diagnostics

### Probabilistic Decision Layer

Instead of rigid routing rules, inputs are evaluated using confidence-weighted “smells”, allowing the system to:

- decline low-confidence flows safely
- adapt to ambiguous or noisy data
- learn from previous outcomes over time

### Full Observability & Audit Trail

Every run produces a structured execution context:

- facts emitted per stage
- agent actions and decisions
- final reports with diagnostics
- reproducible run IDs for tracing

### 🔄 High-Level Flow

- Input arrives (file, text, URL, API payload)
- Sniffer agents extract weak signals (“smells”) from raw data
- Identifier & Extractor agents detect format and domain
- Decision agent selects the best domain using confidence thresholds
- Organizer & Normalizer agents structure and validate content
- Universal packer serializes output into domain-ready artifacts
- Finalizer & Reporter agents persist results and generate diagnostics

The pipeline is self-orchestrating — adding a new domain requires no central rewrite.

### 🧩 Designed for Extension

Plug-in friendly (new agents auto-register via decorators)
Domain-agnostic core (music, recipes, APIs, documents, etc.)

Clear separation between:

- detection
- decision
- transformation
- persistence

Safe failure paths (decline instead of corrupting data)

This makes Hephislog° suitable as:

- a data ingestion backbone
- a legacy-system integration layer
- a pre-normalization gateway
- a teaching example of clean event-driven design

### 🧪 Engineering Practices Demonstrated

- Deterministic pipelines with probabilistic reasoning
- Idempotent runs with execution context isolation
- Structured logging and reporting
- Testable flows (integration tests simulate full pipelines)
- Zero tight coupling between agents

  ---

1. [Read about Architecture](docs/architecture.md)
2. [Read about Philosophy](docs/philosophy.md)
