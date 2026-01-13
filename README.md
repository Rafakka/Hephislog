
<div align="center"><img width="424" height="424" alt="Hephislog_icon" src="https://github.com/user-attachments/assets/69655ad8-ee6a-44d2-9657-15db7d7d60d1" /></div>

ENG

## Hephislogº - Event-Driven Swarm Pipeline for Inteligent Data Ingestion & Normalization

  The system is built as a swarm of single-resposability agents, coordinated via and internal event bus, enabling flexible orchestration, traceability, and continuos learning across runs.

  This project demonstrates production-grade patterns commonly required in IT consulting, system integration, data plataforms, and observability-heavy enviroments.

  Hephislogº is a modular, event driven processing framework designed to ingest unstructured inputs, infer intent through probabilistic signals, and transform them into validated, normalized, and auditable outputs, without hard coded pipelines.

---

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

PT-BR

## Hephislogº - Pipeline de Enxame Orientado a Eventos para Ingestão e Normalização Inteligente de Dados

  O sistema é construído como um SWARM de agentes com responsabilidade única, coordenados por meio de um BUS de eventos interno, permitindo orquestração flexível, rastreabilidade e aprendizado contínuo entre execuções.

  Este projeto demonstra padrões de nível de produção comumente exigidos em consultoria de TI, integração de sistemas, plataformas de dados e ambientes com alta observabilidade.

  O Hephislogº é uma estrutura de processamento modular, orientada a eventos, projetada para ingerir entradas não estruturadas, inferir intenções por meio de sinais probabilísticos e transformá-las em saídas validadas, normalizadas e auditáveis, sem a necessidade de pipelines predefinidos.

  ---

## Conceitos Essenciais

### Arquitetura Orientada a Eventos

Todo o processamento é coordenado por meio de um barramento de eventos desacoplado. 
Os agentes se inscrevem em eventos semânticos (por exemplo, system.input_received, intent.organize.music) em vez de se comunicarem diretamente.

### Projeto de Agentes Baseado em Enxame

Cada agente desempenha uma função bem definida:

- Captura e extração de sinais
- Identificação de entrada
- Tomada de decisão sob incerteza
- Organização do domínio
- Normalização e validação
- Empacotamento e persistência
- Relatórios e diagnósticos

### Camada de Decisão Probabilística

Em vez de regras de roteamento rígidas, as entradas são avaliadas usando "cheiros" ponderados por confiança, permitindo que o sistema:

- rejeite fluxos de baixa confiança com segurança
- se adapte a dados ambíguos ou ruidosos
- aprenda com resultados anteriores ao longo do tempo

### Observabilidade Completa e Rastreamento de Auditoria

Cada execução produz um contexto de execução estruturado:

- fatos emitidos por estágio
- ações e decisões dos agentes
- relatórios finais com diagnósticos
- IDs de execução reproduzíveis para rastreamento

### 🔄 Fluxo de Alto Nível

- Entrada chega (arquivo, texto, URL, payload da API)
- Agentes de captura extraem sinais fracos ("cheiros") dos dados brutos
- Os agentes Identificador e Extrator detectam o formato e o domínio.
- O agente de Decisão seleciona o melhor domínio usando limites de confiança.
- Os agentes Organizador e Normalizador estruturam e validam o conteúdo.
- O empacotador universal serializa a saída em artefatos prontos para o domínio.
- Os agentes Finalizador e Relator persistem os resultados e geram diagnósticos.

O pipeline é auto-orquestrado — adicionar um novo domínio não requer nenhuma reescrita central.

### 🧩 Projetado para Extensões

Amigável a plug-ins (novos agentes se registram automaticamente via decoradores)

Núcleo agnóstico a domínios (música, receitas, APIs, documentos, etc.)

Separação clara entre:

- detecção
- decisão
- transformação
- persistência

Caminhos seguros para falhas (descartar em vez de corromper os dados)

Isso torna o Hephislog° adequado como:

- uma infraestrutura de ingestão de dados
- uma camada de integração com sistemas legados
- um gateway de pré-normalização
- um exemplo didático de design orientado a eventos limpo

### 🧪 Práticas de Engenharia Demonstradas

- Pipelines determinísticos com raciocínio probabilístico
- Execuções idempotentes com isolamento do contexto de execução
- Registro e geração de relatórios estruturados
- Fluxos testáveis ​​(testes de integração simulam pipelines completos)
- Acoplamento zero entre agentes

  ---
